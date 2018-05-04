import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk
import logging

import project
import settings

class CommandRow():
	def __init__(self):
		builder = Gtk.Builder().new_from_file(settings.PATH_UI_COMMAND_ROW)
		self.row = builder.get_object("command_row")
		self.name_entry = builder.get_object("name_entry")
		self.command_entry = builder.get_object("command_entry")
		self.type_menu = builder.get_object("type_menu")

	def set_name(self, name):
		self.name_entry.set_text(name)

	def set_command(self, cmd):
		self.command_entry.set_text(cmd)

	def set_type(self, type):
		self.type_menu.set_active_id(type)


class ProjectWindow():
	def __init__(self, pm, show_projects):
		builder = Gtk.Builder().new_from_file(settings.PATH_UI_NEW_PROJECT)
		self.window      = builder.get_object("project_window")
		self.path_window = builder.get_object("path_window")
		self.path_header = builder.get_object("path_header")

		# Dialogs
		self.confirm_dialog = builder.get_object("confirm_dialog")
		self.error_dialog   = builder.get_object("error_dialog")

		self.delete_project_btn = builder.get_object("delete_project_btn")

		# Main window element
		self.name_entry = builder.get_object("name_entry")
		self.desc_entry = builder.get_object("desc_entry")
		self.path_entry = builder.get_object("path_entry")

		self.command_list = builder.get_object("commands_list")

		self.pm = pm
		self.show_projects = show_projects
		self.current_project = None

		handlers = {
			# Project window
			## Header bar
			"save-project-window"  : self.save_project,
			"close-project-window" : lambda *_: self.window.hide(),
			"on_delete_project_btn_clicked": lambda *_: self.confirm_dialog.show(),
			## Other
			"show-path-window"     : lambda *_: self.path_window.show(),
			"on_entry_icon_release": lambda entry, *_: entry.set_text(""),
			"on_command_add_btn_clicked"   : self.add_command,
			"on_command_remove_btn_clicked": self.remove_command,

			# File chooser dialog
			"on_file_close_clicked": self.path_window_close,
			"on_file_open_clicked" : self.path_window_open,
			"path-window-selection-changed" : lambda *_:
				self.path_header.set_subtitle(
					self.path_window.get_current_folder()),

			# Message dialog buttons
			"delete-confirm"  : self.delete_project,
			"undo-confirm"    : lambda *_: self.confirm_dialog.hide(),
			"response_dialog" : lambda *_: self.error_dialog.hide(),
		}
		builder.connect_signals(handlers)
		logging.debug("Project window is ready")

	def get_path(self):
		self.path_window.get_current_folder()

	def set_path(self, path):
		self.path_window.set_current_folder(path)
		self.path_entry.set_text(path)

	def show(self, btn=None, project=None):
		self.current_project = project
		if self.current_project is None:
			logging.info("Starting the project_window for a new project")
			self.name_entry.set_text("")
			self.set_path(settings.PATH_HOME)
			self.desc_entry.set_text("")
			self.clear_commands_list()
			self.delete_project_btn.hide()
		else:
			logging.debug("Starting the project_window to modify the project")
			self.name_entry.set_text(self.current_project.name)
			self.set_path(self.current_project.path)
			self.desc_entry.set_text(self.current_project.description)
			self.set_commands_list(self.current_project)
			self.delete_project_btn.show()
		self.window.show()

	def hide(self):
		self.window.hide()
		self.current_project = None

	def delete(self, *args):
		self.pm.delete_project(self.current_project)
		self.current_project = None
		self.dialog.hide()
		self.window.hide()

	def set_path_entry(self):
		self.path_window.hide()
		path = self.path_window.get_current_folder()
		if path is not None:
			self.path_entry.set_text(path)

	def path_window_open(self, *args):
		self.set_path_entry()

	def path_window_close(self, *args):
		self.set_path_entry()
		self.path_window.set_current_folder(settings.PATH_HOME)

	def add_command(self, *args):
		row = CommandRow()
		self.command_list.add(row.row)

	def remove_command(self, *args):
		row = self.command_list.get_selected_row()
		if row is not None:
			self.command_list.remove(row)

	def clear_commands_list(self):
		for w in self.command_list.get_children():
			self.command_list.remove(w)

	def set_commands_list(self, project):
		self.clear_commands_list()
		for c in project.commands:
			row = CommandRow()
			row.set_name(c.name)
			row.set_command(c.command)
			row.set_type(c.type)
			self.command_list.add(row.row)

	def get_commands_list(self):
		command_list = []
		for row in self.command_list.get_children():
			box = row.get_child().get_children()
			name = box[0].get_text()  # FIXME remove box[0] box[1] ...
			command = box[1].get_text()
			type = box[2].props.active_id
			if name != "" and command != "":
				command_list.append(project.Command(name, command, type))
			else:
				logging.error("Command with name or/and command empty")
		return command_list

	def save_project(self, *args):
		name = self.name_entry.get_text()
		path = self.path_entry.get_text()
		desc = self.desc_entry.get_text()
		if name == "" or path == "":
			self.error_dialog.show()
			logging.error("Fill all fields!!!")
			return
		if self.current_project is None:
			tmp_project = project.Project(name, path, desc, self.get_commands_list())
			self.pm.add_project(tmp_project)
		else:
			self.pm.update_project(self.current_project, name, path, desc, self.get_commands_list())
		self.window.hide()
		self.show_projects()

	def delete_project(self, *args):
		self.confirm_dialog.hide()
		self.window.hide()
		self.pm.delete_project(self.current_project)
		self.current_project = None
		self.show_projects()
