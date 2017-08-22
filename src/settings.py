import os

HOME         = os.path.expanduser("~")
PROGRAM_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR  = HOME + "/.local/share/projects"
PROJECT_FILE = PROJECT_DIR + "/projects.xml"
DATE_FORMAT  = "%Y-%m-%d %H:%M:%S"
