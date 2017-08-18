import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import logging
import subprocess

import settings
import manager


"""
Gui class manager
"""
class Gui:
	def __init__(self):
		# Gui variable
		self.builder = Gtk.Builder().new_from_file("%s/../gui/gnome-projects.glade"
			% settings.PROGRAM_PATH)
		self.main_window    = self.builder.get_object("main_window")
		self.headerbar      = self.builder.get_object("headerbar")
		# Left pannel
		self.projects_list  = self.builder.get_object("projects_list")
		# Right pannel
		self.last_update_l  = self.builder.get_object("last_update")
		self.last_compile_l = self.builder.get_object("last_compile")
		self.description_l  = self.builder.get_object("description")
		self.log_text       = self.builder.get_object("log")

		self.project_window = ProjectWindow(self.builder)
		self.pm = manager.Manager()
		self.focus = None

		handlers = {
			# Main window header buttons event
			"close-main-window"          : self.stop,
			"clicked-update-compile-all" : (self.pm.update_compile_all, self.set_status),
			"clicked-compile-all"        : (self.pm.compile_all, self.set_status),
			"clicked-update-all"         : (self.pm.update_all, self.set_status),
			"clicked-add-project"        : self.add_project,
			# Project window buttons
			"close-project-window" : lambda *_: self.project_window.hide(),
			"save-project-window"  : self.save_project,
			"show-path-window"     : lambda *_: self.project_window.path_window.show(),
			"delete-project"       : lambda *_: self.project_window.dialog.show(),
			"entry-delete-icon"    : lambda entry, *_: entry.set_text(""),
			# File chooser dialog
			"close-path-window" : self.project_window.close_path_window,
			"open-path-window"  : lambda *_: self.project_window.path_window.hide(),
			"path-window-selection-changed" : lambda *_:
				self.project_window.path_header.set_subtitle(
					self.project_window.path_window.get_current_folder()),
			# Message dialog buttons
			"delete-confirm" : self.delete,
			"undo-confirm"   : lambda *_: self.project_window.dialog.hide()
		}
		self.builder.connect_signals(handlers)
		self.main_window.set_wmclass ("Gnome Projects", "Gnome Projects")

	def start(self):
		self.pm.start()
		self.show_projects()
		self.main_window.show()

	def stop(self, *args):
		self.pm.close()
		Gtk.main_quit()

	def add_project(self, *args):
		self.project_window.show()
		self.show_projects()

	def save_project(self, *args):
		self.project_window.save(self.pm)
		self.show_projects()

	def delete(self, *args):
		self.project_window.dialog.hide()
		self.project_window.project_window.hide()
		self.pm.delete_project(self.project_window.buffer)
		if self.project_window.buffer == self.focus:
			self.focus = None
		self.project_window.buffer = None
		self.show_projects()

	def show_projects(self):
		for w in self.projects_list.get_children():
			self.projects_list.remove(w)
		for p in self.pm.projects_list:
			row = ProjectRow(p, self)
			self.projects_list.add(row.row)

			if self.focus is None:
				self.projects_list.select_row(row.row)
				self.show_info(None, p)
				self.focus = row
			elif self.focus is row:
				self.projects_list.select_row(row.row)
				self.show_info(None, p)

	def str_date(self, date):
		label = "Not yet"
		if date is not None:
			label = date.strftime(settings.DATE_FORMAT)
		return label

	def show_info(self, widget, project):
		self.last_update_l.set_text(self.str_date(project.last_update))
		self.last_compile_l.set_text(self.str_date(project.last_compile))
		self.description_l.set_text(project.description if project.description is not None else "")
		project.error.hide()
		#self.log_text.set_buffer(p.log)

	def set_status(self, project, action):
		if action == "update":
			self.headerbar.set_subtitle("Updating " + project.name)
			project.spinner.show()
		elif action == "compile":
			self.headerbar.set_subtitle("Compiling " + project.name)
			project.spinner.show()
		elif action == "idle":
			self.headerbar.set_subtitle("Idle")
			project.spinner.hide()
		elif action == "error":
			self.headerbar.set_subtitle("Error!")
			project.spinner.hide()
			project.error.show()
		else:
			project.spinner.hide()
			project.error.hide()
			logging.error("Invalid status action")

class ProjectRow():
	def __init__(self, p, gui):
		builder = Gtk.Builder()
		builder.add_from_file(settings.PROGRAM_PATH + "/../gui/project-row.glade")
		builder.get_object("project_name").set_text(p.name)

		self.row     = builder.get_object("project_row")
		p.spinner = builder.get_object("spinner")
		p.error   = builder.get_object("error")

		handlers = {
			"grab_focus" : (gui.show_info, p),
			"on_update_btn_clicked"         : (gui.pm.update, p, gui.set_status),
			"on_compile_btn_clicked"        : (gui.pm.compile, p, gui.set_status),
			"on_update_compile_btn_clicked" : (gui.pm.update_compile, p, gui.set_status),
			"on_settings_btn_clicked" :   (gui.project_window.modify, p)
		}
		builder.connect_signals(handlers)


class ProjectWindow():
	def __init__(self, builder):
		self.project_window = builder.get_object("project_window")
		self.path_window    = builder.get_object("path_window")
		self.path_header    = builder.get_object("path_header")
		self.dialog         = builder.get_object("confirm")

		self.entry_name = builder.get_object("input_name")
		self.entry_desc = builder.get_object("input_description")
		self.entry_update = builder.get_object("input_update")
		self.entry_compile = builder.get_object("input_compile")
		self.btn_delete = builder.get_object("delete")
		self.buffer = None

	def show(self, *args):
		logging.debug("Starting the project_window to create a new project")
		self.entry_name.set_text("")
		self.entry_desc.set_text("")
		self.path_window.set_current_folder(settings.HOME)
		self.entry_update.set_text("git pull")
		self.entry_compile.set_text("cd build; cmake ..; make -j8")
		self.btn_delete.hide()
		self.project_window.show()

	def hide(self):
		self.project_window.hide()
		self.buffer = None

	def save(self, pm):
		name = self.entry_name.get_text()
		desc = self.entry_desc.get_text()
		path = self.path_window.get_current_folder()
		update = self.entry_update.get_text()
		compile = self.entry_compile.get_text()

		if self.buffer is None:
			if name != "" and path is not None and update != "":
				pm.add_project(name, desc, path, update, compile)
			else:
				logging.error("Fill all fields!!! Aggiungi il dialog")
		else:
			self.buffer.name = name
			self.buffer.description = desc
			self.buffer.path = path
			self.buffer.update_cmd = update
			self.buffer.compile_cmd = compile

		self.project_window.hide()
		self.buffer = None

	def delete(self, *args):
		pm = args[-1]
		pm.delete_project(self.buffer)
		self.buffer = None
		self.dialog.hide()
		self.project_window.hide()
		self.show_projects()

	def modify(self, btn, p):
		self.buffer = p
		logging.debug("Starting the assistant to modify the project")
		self.entry_name.set_text(p.name)
		self.entry_desc.set_text(p.description if p.description is not None else "")
		self.path_window.set_current_folder(p.path)
		self.entry_update.set_text(p.update_cmd)
		self.entry_compile.set_text(p.compile_cmd)
		self.btn_delete.show()
		self.project_window.show()

	def close_path_window(self, *args):
		self.path_window.hide()
		self.path_window.set_current_folder(settings.HOME)

