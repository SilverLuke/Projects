import os

PATH_HOME         = os.path.expanduser("~")
PATH_PROGRAM      = os.path.dirname(os.path.realpath(__file__))

PATH_TEST = PATH_PROGRAM + "/../test"
PATH_RELEASE = PATH_HOME + "/.local/share/projects"

PATH_PROJECT_DIR  = PATH_RELEASE
PATH_PROJECT_FILE = PATH_PROJECT_DIR + "/projects.xml"

PATH_UI_MAIN        = PATH_PROGRAM + "/../gui/main.glade"
PATH_UI_NEW_PROJECT = PATH_PROGRAM + "/../gui/project window.glade"
PATH_UI_PROJECT_ROW = PATH_PROGRAM + "/../gui/project row.glade"
PATH_UI_COMMAND_ROW = PATH_PROGRAM + "/../gui/command row.glade"

SHELL = os.environ.get('SHELL')
#DATE_FORMAT  = "%Y-%m-%d %H:%M:%S"
