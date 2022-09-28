from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
from move_with_progress import copyFilesWithProgress
import shutil

CATEGORIES = [
  'Apose',
  'Statue',
  'Bad',
  'Custom'
]

def runWatcher():
  dest = var.get()
  dropbox = drop.get()

  textArea = scrolledtext.ScrolledText(root)
  textArea.insert(INSERT, dest)
  textArea.configure(state="disabled")

  for cat in CATEGORIES:
    if not os.path.exists(os.path.join(dest, cat)):
      os.makedirs(os.path.join(dest, cat))
  if not os.path.exists("./Archive"):
    os.makedirs("./Archive")

  watch = Watch(dest, dropbox)
  watch.run()

  return

class Watch():
  
  def __init__(self, dest, dropbox="./DROP_FILES_HERE"):
      self.observer = Observer()
      self.destination = dest
      self.dropbox = dropbox

  def run(self):

    if not os.path.isdir(self.dropbox):
      os.makedirs(self.dropbox)
    rt, parent_folder = os.path.split(self.dropbox)
    event_handler = Handler(self.destination, parent_folder)
  
    self.observer.schedule(event_handler, self.dropbox, recursive=True)
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
      root, dir_name = os.path.split(event.src_path)
      if os.path.exists(event.src_path):
        if dir_name != self.parent:
          ticket_name = dir_name.split('-')[-1]
          new_path = os.path.join(root, ticket_name)
          os.rename(event.src_path, new_path)

          pose = ticket_name.split('_')[-1]

          if pose.lower() == 'a':
            destination_subfolder = 'Apose'
          elif pose.lower() == 's':
            destination_subfolder = 'Statue'
          elif pose.lower() == 'b' or pose.lower() == 'bad':
            destination_subfolder = 'Bad'
          else:
            destination_subfolder = 'Custom'

          destination = os.path.join(self.dest, destination_subfolder, ticket_name)
          archive = os.path.join("./Archive", ticket_name)
          

          copyFilesWithProgress(new_path, destination, "copy")
          copyFilesWithProgress(new_path, archive)

          shutil.rmtree(new_path)

          print('DONE')