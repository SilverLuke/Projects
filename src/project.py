from datetime import datetime

import subprocess
import logging
import os

"""
Single project class
"""
class Project():
	def __init__(self, name, desc, path, update_cmd, compile_cmd, last_update=None, last_compile=None):
		# Essential variable
		self.name = name
		self.path = path
		self.update_cmd = update_cmd
		self.compile_cmd = compile_cmd
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

	def update(self, *args):
		val = 0
		if self.update_cmd is not None:
			val = self.run_cmd(self.update_cmd)
			self.last_update = datetime.now()
		return val

	def compile(self, *args):
		val = 0
		if self.compile_cmd is not None:
			val = self.run_cmd(self.compile_cmd)
			self.last_compile = datetime.now()
		return val

	def run_cmd(self, cmd):
		logging.debug("Working for %s" % self.name)
		os.chdir(self.path)
		cmds = cmd.split(";")
		for c in cmds:
			c = c.split()
			if c[0] == "cd":  # This is a cd command
				logging.debug("%s change dir" % str(c))
				os.chdir(c[1])
			else:
				logging.debug(str(c))
				if subprocess.call(c) != 0:
					raise Exception
