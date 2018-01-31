import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Vte, GLib
import logging

import settings
import manager
import projectwindow

"""
Gui class manager
"""
class Gui:
	def __init__(self):
		# Gui variable
		builder= Gtk.Builder().new_from_file(settings.PATH_UI_MAIN)
		self.main_window    = builder.get_object("main_window")
		self.headerbar      = builder.get_object("headerbar")
		self.main_window.set_wmclass("Projects", "Projects")
		# Left pannel
		self.projects_list  = builder.get_object("projects_list")
		# Right pannel
		self.last_update_l  = builder.get_object("last_update")
		self.last_compile_l = builder.get_object("last_compile")
		self.description_l  = builder.get_object("description")

		# Other
		self.focus = None
		self.terminal = self.new_term(builder.get_object("terminal"))
		self.pm = manager.Manager(self.terminal, self.set_status)
		self.project_window = None
		handlers = {
			# Main window header buttons event
			"close-main-window"          : self.stop,
			"clicked-update-compile-all" : self.pm.update_compile_all,
			"clicked-compile-all"        : self.pm.compile_all,
			"clicked-update-all"         : self.pm.update_all,
			"on_add_project_clicked"     : self.add_project,
		}
		builder.connect_signals(handlers)

	def new_term(self, box):
		terminal = Vte.Terminal()
		terminal.set_scrollback_lines(5000)
		terminal.set_size(500,10)
		terminal.set_encoding("UTF-8")
		terminal.spawn_sync(
			Vte.PtyFlags.DEFAULT,
			settings.PATH_HOME,
			[settings.SHELL],
			[],
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None,
			None
		)
		box.add(terminal)
		return terminal

	def get_project_window(self):
		if self.project_window is None:
			self.project_window = projectwindow.ProjectWindow(self.pm, self.show_projects)
			self.project_window.window.set_transient_for(self.main_window)
		return self.project_window

	def start(self):
		self.pm.start()
		self.show_projects()
		self.main_window.show()
		self.terminal.show()

	def stop(self, *args):
		self.pm.stop()
		logging.shutdown()
		Gtk.main_quit()

	def add_project(self, *args):
		self.get_project_window().show()

	def settings(self, btn, p):
		self.get_project_window().show(project=p)

	def show_projects(self):
		logging.debug("Show project")
		for w in self.projects_list.get_children():
			self.projects_list.remove(w)
		for p in self.pm.projects_list:
			row = ProjectRow(p, self)
			self.projects_list.add(row.row)

	def str_date(self, date):
		label = "Not yet"
		if date:
			label = date
		return label

	def show_info(self, project):
		self.last_update_l.set_text(self.str_date(project.last_update))
		self.last_compile_l.set_text(self.str_date(project.last_compile))
		self.description_l.set_text(project.description)
		project.error.hide()

	def handle_focus(self, widget, btn, row):
		if btn.button == 1:  # Left click
			logging.debug("Handle left input, cd")
			if self.focus:
				self.focus.close()
			self.pm.change_dir(row.p.path)
		elif btn.button == 3:  # Right click
			logging.debug("Handle right input, open the button list")
			if self.focus is None:
				self.focus = row
				self.focus.open()
			elif self.focus != row:
				self.focus.close()
				self.focus = row
				self.focus.open()
			else:
				self.focus.close()
				self.focus = None
		self.show_info(row.p)
		self.projects_list.select_row(row.row)

	def set_status(self, action, project=None):
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
		builder.add_from_file(settings.PATH_UI_PROJECT_ROW)
		builder.get_object("project_name").set_text(p.name)

		self.row  = builder.get_object("project_row")
		self.btn_list  = builder.get_object("btn_list")
		self.p    = p
		p.spinner = builder.get_object("spinner")
		p.error   = builder.get_object("error")

		handlers = {
			"on_project_row_button_release_event" : (gui.handle_focus, self),
			"on_update_compile_btn_clicked" : (gui.pm.update_compile,    p),
			"on_run_btn_clicked"            : (gui.pm.run,               p),
			"on_open_btn_clicked"           : (gui.pm.open,              p),
			"on_settings_btn_clicked"       : (gui.settings,  p),
		}
		builder.connect_signals(handlers)

		for c in p.commands:
			btn = Gtk.Button()
			btn.set_label(c.name)
			btn.connect("clicked", gui.pm.run_command, c, p.path)
			btn.show()
			self.btn_list.add(btn)

	def open(self):
		if len(self.p.commands) > 0:
			self.btn_list.show()

	def close(self):
		self.btn_list.hide()
