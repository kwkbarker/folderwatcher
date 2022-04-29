from posixpath import dirname
from tkinter import filedialog
import tkinter as tk

CATEGORIES = [
  '_Apose',
  '_Statue',
  '_Bad',
  '_Custom'
]


def getDestinationFolder():
  root = tk.Tk()
  root.withdraw()
  selected_folder = filedialog.askdirectory()
  return selected_folder


from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
import sys
import os
import time
import shutil

class Watch():
  

  path = sys.argv[1] if len(sys.argv) > 1 else "./DROP_FILES_HERE"
  if not os.path.isdir(path):
    os.makedirs(path)
  rt, parent_folder = os.path.split(path)
  print(parent_folder)

  def __init__(self, dest):
      self.observer = Observer()
      self.destination = dest

  def run(self):
    event_handler = Handler(self.destination, self.parent_folder)
  
    self.observer.schedule(event_handler, self.path, recursive=True)
    self.observer.start()
    try:
      while True:
        time.sleep(5)
    except:
      self.observer.stop()
      print('Observer stopped.')
    
    self.observer.join()
  
class Handler(FileSystemEventHandler):

  def __init__(self, dest, parent):
      self.dest = dest
      self.parent = parent

  def on_created(self, event):
        if event.is_directory:
          print("src path: " + event.src_path)
          root, dir_name = os.path.split(event.src_path)
          if dir_name != self.parent:
            ticket_name = dir_name.split('-')[-1]
            new_path = os.path.join(root, ticket_name)
            os.rename(event.src_path, new_path)

            pose = ticket_name.split('_')[-1]

            if pose.lower() == 'a':
              destination_subfolder = '_Apose'
            elif pose.lower() == 's':
              destination_subfolder = '_Statue'
            elif pose.lower() == 'b' or pose.lower() == 'bad':
              destination_subfolder = '_Bad'
            else:
              destination_subfolder = '_Custom'

            destination = os.path.join(self.dest, destination_subfolder, ticket_name)

            dest = shutil.move(new_path, destination)
            print(dest)


if __name__ == "__main__":
  dest = getDestinationFolder()
  for cat in CATEGORIES:
    if not os.path.exists(os.path.join(dest, cat)):
      os.makedirs(os.path.join(dest, cat))
  watch = Watch(dest)
  watch.run()
  