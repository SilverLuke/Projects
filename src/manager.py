from lxml import etree as ET
import os
import logging
import subprocess

from project import Project, Command
import settings


"""
Project manager main class
"""
class Manager():
	def __init__(self, terminal, show_status):
		self.xml = self.check_file()
		self.projects_list = []
		# Terminal
		self.terminal = terminal
		self.gui_notify = show_status

	def __str__(self):
		_str = ""
		for p in self.projects_list:
			_str += str(p)
		return _str

	def start(self):
		self.load_projects()

	def stop(self):
		pass

	def check_file(self):
		if not os.path.exists(settings.PATH_PROJECT_FILE):
			os.makedirs(settings.PATH_PROJECT_DIR)
			logging.debug("Creating projects.xml ...")
			root = ET.Element("projects_list")
			tree = ET.ElementTree(root)
			tree.write(settings.PATH_PROJECT_FILE, pretty_print=True)
		else:
			tree = ET.parse(settings.PATH_PROJECT_FILE)
			root = tree.getroot()
		return root

	def load_projects(self):
		for project_xml in self.xml.findall('project'):
			name = project_xml.find('name').text
			path = project_xml.find('path').text
			desc = project_xml.findtext('description', "")
			update = self.get_update_date(project_xml.findtext('last_update', ""), path)
			compil = project_xml.findtext('last_compile', "")
			project = Project(name, path, desc, [], last_update=update, last_compile=compil)
			for command_xml in project_xml.iter('command'):
				name = command_xml.find('name').text
				cmd  = command_xml.find('exec').text
				type = command_xml.find('type').text
				project.add_command(name, cmd, type)
			self.projects_list.append(project)

	def get_update_date(self, date, path):
		if not date:
			try :
				date = self.get_last_update(path)
			except subprocess.CalledProcessError as e:
				logging.info("Error getting last update date, maybe it isn't a git project")
		return date

	# Get last update from git
	def get_last_update(self, path):
		os.chdir(path)
		cmd = "stat -c %y .git/FETCH_HEAD".split()
		return str(subprocess.check_output(cmd, stderr=subprocess.DEVNULL))[2:21]

	def save_xml(self):
		tree = ET.ElementTree(self.xml)
		tree.write(settings.PATH_PROJECT_FILE, pretty_print=True)

	def add_xml_project(self, project):
		p = ET.SubElement(self.xml, "project")
		ET.SubElement(p, "name").text = project.name
		ET.SubElement(p, "path").text = project.path
		ET.SubElement(p, "description").text = project.description
		ET.SubElement(p, "last_update").text = project.last_update
		ET.SubElement(p, "last_compile").text = project.last_compile
		c_l = ET.SubElement(p, "commands_list")
		for command in project.commands:
			c = ET.SubElement(c_l, "command")
			ET.SubElement(c, "name").text = command.name
			ET.SubElement(c, "exec").text = command.command
			ET.SubElement(c, "type").text = command.type
		self.save_xml()

	def add_project(self, project):
		logging.info("Project added " + project.name)
		project.last_update = self.get_update_date(project.last_update, project.path)
		self.projects_list.append(project)
		self.add_xml_project(project)

	def delete_project(self, p):
		logging.info("Project deleted " + p.name)
		self.projects_list.remove(p)
		self.xml.clear()
		for project in self.projects_list:
			self.add_xml_project(project)
		self.save_xml()

	def update_project(self, old, name, path, desc, commands):
		logging.info("Project changed")
		old.update_value(name, path, desc, commands)
		self.xml.clear()
		for project in self.projects_list:
			self.add_xml_project(project)
		self.save_xml()

	def change_dir(self, path):
		cd = " cd %s\n" % path
		self.terminal.feed_child(cd, len(cd))

	def update_all(self, btn):
		logging.info("Update all projects")
		for p in self.projects_list:
			self.update(p)

	def compile_all(self, btn):
		logging.info("Compile all projects")
		for p in self.projects_list:
			self.compile(p)

	def update_compile_all(self, btn):
		logging.info("Update and compile all projects")
		for p in self.projects_list:
			self.update_compile(None, p)

	def update(self, p):
		self.change_dir(p.path)
		cmd = p.get_update_cmd()
		self.gui_notify("update", p)
		for c in cmd:
			self.terminal.feed_child(c, len(c))
		self.gui_notify("idle", p)

	def compile(self, p):
		self.change_dir(p.path)
		cmd = p.get_compile_cmd()
		self.gui_notify("compile", p)
		for c in cmd:
			self.terminal.feed_child(c, len(c))
		self.gui_notify("idle", p)

	def run_command(self, btn, cmd, path):
		self.change_dir(path)
		tmp = cmd.get_command()
		self.terminal.feed_child(tmp, len(tmp))

	def update_compile(self, btn, p):
		self.update(p)
		self.compile(p)

	def run(self, btn, p):
		os.chdir(p.path)
		cmd = p.get_run_cmd()
		for c in cmd:
			subprocess.Popen(c, shell=True)
		self.gui_notify("idle", p)

	def open(self, btn, p):
		logging.debug("Open fs " + p.name)
		subprocess.Popen("nautilus " + p.path, shell=True)

