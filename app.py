from tkinter import filedialog
import tkinter as tk

def getDestinationFolder():
  root = tk.Tk()
  root.withdraw()
  selected_folder = filedialog.askdirectory()
  return selected_folder


from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import sys

def watch():
  observer = Observer()

  path = sys.argv[1] if len(sys.argv) > 1 else "./DROP_FILES_HERE"

  



if __name__ == "__main__":
  watch()