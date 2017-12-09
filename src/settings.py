import os

PATH_HOME         = os.path.expanduser("~")
PATH_PROGRAM      = os.path.dirname(os.path.realpath(__file__))

PATH_PROJECT_DIR  = PATH_HOME + "/.local/share/projects"
PATH_PROJECT_FILE = PATH_PROJECT_DIR + "/projects.xml"

PATH_UI_MAIN = PATH_PROGRAM + "/../gui/main.ui"
PATH_UI_ROW  = PATH_PROGRAM + "/../gui/row.ui"


DATE_FORMAT  = "%Y-%m-%d %H:%M:%S"
