#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import logging
import signal
import traceback
import sys

from gui import Gui


"""
Signal handler function
"""
def InitSignal(gui):
	def signal_action(signal):
		if signal.value is signal.SIGINT.value:
			print("\r", end="")
			logging.debug("Caught signal SIGINT(2)")
		gui.stop()

	def handler(*args):
		signal_action(args[0])

	def idle_handler(*args):
		GLib.idle_add(signal_action, priority=GLib.PRIORITY_HIGH)

	def install_glib_handler(sig):
		GLib.unix_signal_add(GLib.PRIORITY_HIGH, sig, handler, sig)

	SIGS = [getattr(signal, s, None) for s in "SIGINT".split()]
	for sig in filter(None, SIGS):
		signal.signal(sig, idle_handler)
		GLib.idle_add(install_glib_handler, sig, priority=GLib.PRIORITY_HIGH)


"""
Colored debug info
"""
def add_coloring_to_emit_ansi(fn):
	RED_BOLD = '\x1b[31;1m'
	RED      = '\x1b[31m'
	GREEN    = '\x1b[32m'
	YELLOW   = '\x1b[33m'
	BLUE     = '\x1b[34m'
	PINK     = '\x1b[35m'
	CYAN     = '\x1b[36m'
	DEFAULT  = '\x1b[0m'
	def new(*args):
		levelno = args[1].levelno
		color = DEFAULT
		if levelno >= logging.CRITICAL:
			color = RED_BOLD
		elif levelno >= logging.ERROR:
			color = RED
		elif levelno >= logging.WARNING:
			color = YELLOW
		elif levelno >= logging.INFO:
			color = DEFAULT
		elif levelno >= logging.DEBUG:
			color = GREEN
		args[1].msg = color + str(args[1].msg) + DEFAULT
		return fn(*args)
	return new

def test_log():
	logging.critical("Test critical")
	logging.error("Test error")
	logging.warning("Test warning")
	logging.info("Test info")
	logging.debug("Test debug")


if __name__ == "__main__":
	#logging.basicConfig(filename='gnome-projects.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
	logging.basicConfig(format='%(levelname)-8s [ %(threadName)-10s %(filename)s:%(lineno)-4s] %(message)s',level=logging.DEBUG)
	logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)
	#~ test_log()
	try:
		gui = Gui()
		InitSignal(gui)
		gui.start()
		Gtk.main()
	except Exception as e:
		logging.critical("Exception!!!!")
		try:
			gui.stop()
		except:
			logging.critical("Gui doesn't start")
		print("\n%s\n Please report this error" % traceback.format_exc())
	sys.exit(-1)
