import pyinotify
import asyncore # not found when installing in server  with pip3
import os
import sys
from pprint import pprint
from datetime import datetime
from file_poster import post_to_xdiff
from get_paths import get_folder_paths
import logging # not found when installing in server  with pip3
import logging.handlers
import time # not found when installing in server  with pip3
#from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
from logging.handlers import RotatingFileHandler
import threading
from statinfo import task_manager
from statinfo import TimerClass
import psutil
from pathlib import Path
import pathlib
import argparse


######## ARGUMENTS ########

text = "This program watches a pre-defined set of folder pairs in the server, and sends a request to xDiff whenever two OMT packages are put in them."

# intialize arg parser with a description
parser = argparse.ArgumentParser(description=text)
parser.add_argument("-V", "--version", help="show program version",
					action="store_true")
parser.add_argument("-c", "--config", help="specify path to config file containing the paths to the two packages to be compaired")

# read arguments from the command line
args = parser.parse_args()

# check for -V or --version
if args.version:
	print("This is xDiff Watcher 0.2.0")
	sys.exit()
elif args.config:
	print("Config file: %s" % args.config)
	path_to_config = args.config.rstrip('/')
else:
	print("Argument -c not found.")
	sys.exit()


######## FUNCTIONS ########

def has_handle(fpath):
	for proc in psutil.process_iter():
		try:
			for item in proc.open_files():
				if fpath == item.path:
					return True
		except Exception:
			#print(Exception)
			pass

	return False


######## REFERENCES ########

path_pair_list = get_folder_paths(path_to_config)

if path_pair_list == None:
	sys.exit("Unable to get list of paths, die young and leave a beautiful corpse.")

pprint(f"Watching the following list of path pairs: {path_pair_list}")


class Event(LoggingEventHandler):
	"""I want to capture only on_created events, ignore the rest."""

	def __init__(self, logger, path_pair, func):
		self.logger = logger
		self.path_pair = path_pair
		self.post_to_xdiff = func

	def on_any_event(self, event):
		print(event)
	
	def on_created(self, event):
		#super().on_created(event)

		if event.src_path.endswith('.omt'):
			what = 'OMT package'
			self.logger.info("Created %s: %s", what, event.src_path)

			time.sleep(5)
			self.post_to_xdiff(self.path_pair)

	#def on_deleted(self, event):
	#	pass

def main():
	logging.basicConfig(level=logging.INFO,  format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
	logger = logging.getLogger(__name__)

	event_handler = LoggingEventHandler()
	observer = Observer()

	if len(path_pair_list) > 0:
		for path_pair in path_pair_list:
			event_handler = Event(logger, path_pair, post_to_xdiff)
			observer.schedule(event_handler, path_pair['edit'], recursive=False)
	#else:
		#observer.schedule(event_handler, dir_edit, recursive=True)
	observer.start()

	try:
		while True:
			time.sleep(5)
	except KeyboardInterrupt:
		observer.stop()

	observer.join()


if __name__ == "__main__":
	main()


# REFERENCES
#https://stackoverflow.com/questions/19991033/generating-multiple-observers-with-python-watchdog
# explore patterns
# https://www.thepythoncorner.com/2019/01/how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/
# https://www.saltycrane.com/blog/2010/04/monitoring-filesystem-python-and-pyinotify/
# https://stackoverflow.com/questions/32281277/too-many-open-files-failed-to-initialize-inotify-the-user-limit-on-the-total
