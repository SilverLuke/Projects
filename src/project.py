from datetime import datetime

import subprocess
import logging
import os

"""
Single project class
"""
class Project():
	def __init__(self, name, desc, path, update_cmd, compile_cmd, run_cmd, last_update=None, last_compile=None):
		# Essential variable
		self.name = name
		self.path = path
		self.update_cmd = update_cmd
		self.compile_cmd = compile_cmd
		self.run_cmd = run_cmd
		# Optional variable
		self.description = desc
		self.last_update = last_update
		self.last_compile = last_compile
		self.log = None #= Gtk.TextBuffer()

		self.spinner = None
		self.error = None

	def __str__(self):
		return  "Nome:        " + self.name + \
				"\n\tDesc:    " + self.description + \
				"\n\tPath:    " + self.path + \
				"\n\tUpdate:  " + self.update_cmd + " (" + str(self.last_update) +")" + \
				"\n\tCompile: " + self.compile_cmd + " (" + str(self.last_compile) + ")"

	def go_project_dir(self):
		os.chdir(self.path)

	def update(self, *args):
		val = 0
		if self.update_cmd is not None:
			val = self.exec_cmd(self.update_cmd)
			self.last_update = datetime.now()
		return val

	def compile(self, *args):
		val = 0
		if self.compile_cmd is not None:
			val = self.exec_cmd(self.compile_cmd)
			self.last_compile = datetime.now()
		return val

	def run(self):
		logging.debug("run " + self.name)
		self.go_project_dir()
		subprocess.Popen(self.run_cmd, shell=True)

	def open(self):
		logging.debug("open" + self.name)
		subprocess.Popen("nautilus " + self.path, shell=True)

	def exec_cmd(self, cmd):
		os.chdir(self.path)
		logging.debug("Working for %s, running command %s" % (self.name, cmd))
		val = subprocess.call(cmd, shell=True)
		if int(val) == 0:
			logging.debug("Command executed successfully")
		else:
			logging.error("Return value %i" % val)
