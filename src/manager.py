from threading import Thread
from queue import Queue
from lxml import etree as ET
from datetime import datetime
import os
import logging
import subprocess

import project
import settings


class Singleton(type):
	def __init__(cls, name, bases, attrs, **kwargs):
		super().__init__(name, bases, attrs)
		cls._instance = None
	def __call__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super().__call__(*args, **kwargs)
		return cls._instance


"""
Project manager main class
"""
class Manager(metaclass=Singleton):
	def __init__(self):
		self.projects_list = []
		self.command_queue = Queue()
		self.thread = Executor(self.command_queue)

	def start(self):
		self.load_projects()
		self.thread.start()

	def close(self):
		self.save_projects()
		self.thread.stop = True
		self.command_queue.put(None)

	def save_projects(self, *args):
		root = ET.Element("projects")
		for project in self.projects_list:
			p = ET.SubElement(root, "project")
			ET.SubElement(p, "name").text = project.name
			ET.SubElement(p, "description").text = project.description
			ET.SubElement(p, "path").text = project.path
			ET.SubElement(p, "update").text = project.update_cmd
			ET.SubElement(p, "compile").text = project.compile_cmd

			if project.last_update is None:
				ET.SubElement(p, "last_update").text = None
			else:
				ET.SubElement(p, "last_update").text = project.last_update.strftime(settings.DATE_FORMAT)

			if project.last_compile is None:
				ET.SubElement(p, "last_compile").text = None
			else:
				ET.SubElement(p, "last_compile").text = project.last_compile.strftime(settings.DATE_FORMAT)

		tree = ET.ElementTree(root)
		tree.write(settings.PROJECT_FILE, pretty_print=True)
		logging.debug("All projects are saved")

	def load_projects(self):
		if not os.path.exists(settings.PROJECT_DIR):
			os.makedirs(settings.PROJECT_DIR)
			logging.debug("Projects file not found")
			root = ET.Element("projects")
			tree = ET.ElementTree(root)
			tree.write(settings.PROJECT_FILE, pretty_print=True)
			return
		else:
			tree = ET.parse(settings.PROJECT_FILE)

		root = tree.getroot()
		for p in root.findall('project'):
			name = p.find('name').text
			desc = p.find('description').text
			path = p.find('path').text
			update_cmd = p.find('update').text
			compile_cmd = p.find('compile').text

			last_update = p.find('last_update').text
			if last_update is None:
				try :
					last_update = self.get_last_update(path)
				except subprocess.CalledProcessError as e:
					logging.info("Error getting last update date in %s, maybe it isn't a git project" % name)
					last_update = None
			if last_update is not None:
				try:
					last_update = datetime.strptime(last_update, settings.DATE_FORMAT)
				except Exception as e:
					logging.warning("last update datetime error in %s ex: %s" % (name, e))
					last_update = None

			last_compile = p.find('last_compile').text
			if last_compile is not None:
				try:
					last_compile = datetime.strptime(last_compile, settings.DATE_FORMAT)
				except Exception as e:
					logging.warning("Last compile datetime error in %s ex: %s" % (name, e))
					last_compile = None

			self.add_project(name, desc, path, update_cmd, compile_cmd, last_update, last_compile)

	def get_last_update(self, path):
		os.chdir(path)
		cmd = "stat -c %y .git/FETCH_HEAD".split()
		return str(subprocess.check_output(cmd, stderr=subprocess.DEVNULL))[2:21]

	def add_project(self, name, desc, path, update, compile, last_update=None, last_compile=None):
		p = project.Project(name, desc, path, update, compile, last_update, last_compile)
		self.projects_list.append(p)
		logging.info("New project added " + p.name)

	def delete_project(self, p):
		logging.info("Project deleted " + p.name)
		self.projects_list.remove(p)

	def update_all(self, btn, gui_fun):
		logging.info("Update all projects")
		for p in self.projects_list:
			self.command_queue.put((p.update, gui_fun, p, "update"))

	def compile_all(self, btn, gui_fun):
		logging.info("Compile all projects")
		for p in self.projects_list:
			self.command_queue.put((p.compile, gui_fun, p, "compile"))

	def update_compile_all(self, btn, gui_fun):
		logging.info("Update and compile all projects")
		for p in self.projects_list:
			self.command_queue.put((p.update, gui_fun, p, "update"))
			self.command_queue.put((p.compile, gui_fun, p, "compile"))

	def update(self, btn, p, gui_fun):
		self.command_queue.put((p.update, gui_fun, p, "update"))

	def compile(self, btn, p, gui_fun):
		self.command_queue.put((p.compile, gui_fun, p, "compile"))

	def update_compile(self, btn, p, gui_fun):
		self.command_queue.put((p.update, gui_fun, p, "update"))
		self.command_queue.put((p.compile, gui_fun, p, "compile"))


"""
Backend thread used to execute the system command
"""
class Executor(Thread):
	def __init__(self, queue):
		super().__init__(name="Executor")
		self.queue = queue
		self.task = None
		self.stop = False

	# In the queue (command, graphic status, project, action)
	def run(self):
		while True:
			logging.debug("Waiting for a task...")

			if not self.stop:
				self.task = self.queue.get()
			else:
				logging.debug("Thread is force stopped")
				break

			if self.task is None:
				logging.debug("Thread is stopped")
				break

			logging.debug("Begin task")

			cmd_fun, gui_fun, obj, action = self.task
			gui_fun(obj, action)
			try:
				cmd_fun()
				gui_fun(obj, "idle")
			except Exception as e:
				logging.error("%s found error while %s it, error:\n%s" % (obj.name, action, str(e)))
				gui_fun(obj, "error")

			self.queue.task_done()
			self.task = None
