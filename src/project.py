from datetime import datetime

import logging
import os

class Command():
	def __init__(self, name, command, type):
		self.icon = None  # TODO mabye some day
		self.name = name
		self.command = command
		self.type = type

	def get_command(self):
		return str(" " + self.command + "\n")

"""
Single project class
"""
class Project():
	def __init__(self, name, path, desc, commands, last_update="", last_compile=""):
		self.name = name
		self.path = path
		self.commands = commands
		# Optional variable
		self.description = desc
		self.last_update = last_update
		self.last_compile = last_compile
		# ListRow graphics
		self.spinner = None
		self.error = None

	def __str__(self):
		str =   "Name:  " + self.name + \
				"\n\tPath:    " + self.path + \
				"\n\tDesc:    " + self.description + \
				"\n\tCommands:"
		for c in self.commands:
			str += "\n\t\t"+ c.name + "\t:\t" + c.command + " \t" + c.type
		return str

	def add_command(self, name, command, type):
		self.commands.append(Command(name,command,type))

	def update_value(self, name, path, desc, commands):
		self.name = name
		self.path = path
		self.description = desc
		self.commands = commands

	def go_project_dir(self):
		os.chdir(self.path)

	def get_type_cmd(self, _type):
		tmp = []
		for c in self.commands:
			if c.type == _type:
				tmp.append(c.get_command())
		return tmp

	def get_update_cmd(self):
		return self.get_type_cmd("update")

	def get_compile_cmd(self, *args):
		return self.get_type_cmd("compile")

	def get_run_cmd(self):
		return self.get_type_cmd("run")

	def get_other_cmd(self):
		return self.get_type_cmd("other")

