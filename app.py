from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import cv2 as cv

CATEGORIES = [
  'Apose',
  'Statue',
  'Bad',
  'Custom'
]


def countFiles(directory):
    files = []

    if os.path.isdir(directory):
        for path, dirs, filenames in os.walk(directory):
            files.extend(filenames)

    return len(files)



def makedirs(dest):
    if not os.path.exists(dest):
        os.makedirs(dest)


def remove_folders(path):
    dir = os.listdir(path)

    if len(dir) == 0:
        os.rmdir(path)
    else:
        for sub in dir:
            sub_path = os.path.join(path, sub) 
            remove_folders(sub_path)
        os.rmdir(path)


def copyFilesWithProgress(src, dest, thumbName, protocol="move"):

    # PROGRESS BAR
    for widget in pbarFrame.winfo_children():
       widget.destroy()
    p = ttk.Progressbar(
        pbarFrame, 
        orient="horizontal", 
        length=320,
        mode="determinate"
    )
    p.pack()



    numFiles = countFiles(src)

    if numFiles > 0:
        makedirs(dest)

    numCopied = 0

    for path, dirs, filenames in os.walk(src):
        for directory in dirs:
          destDir = path.replace(src,dest)
          makedirs(os.path.join(destDir, directory))

        for sfile in filenames:
            srcFile = os.path.join(path, sfile)

            destFile = os.path.join(path.replace(src, dest), sfile)
            
            if protocol == "copy":
                shutil.copy(srcFile, destFile)

                # thumbnail creation
                if thumbnail.get():   
                  if f"{thumbNum.get()}.jpg" in sfile:
                    newFilename = f"{thumbName}.jpg"
                    newSrc = os.path.join(path, newFilename)
                    os.rename(srcFile, newSrc)
                    destThumb = os.path.join(thumb.get(), newFilename)
                    img = cv.imread(newSrc)
                    scale_percent = 60 # percent of original size
                    width = int(img.shape[1] * scale_percent / 100)
                    height = int(img.shape[0] * scale_percent / 100)
                    dim = (width, height)
                    cv.resize(img, dim, interpolation = cv.INTER_AREA)
                    shutil.copy(os.path.join(newSrc), destThumb)
            
            else:
                shutil.move(srcFile, destFile)


            numCopied += 1

            p["value"] = int((numCopied/numFiles) * 100)

def lbText(text):
  lbidx.set(lbidx.get() +1)
  lb.insert(lbidx.get(), text)

import threading

def startWatch():
  watch = Watch(var.get(), drop.get())
  watch.run()

def runWatcher():
  dest = var.get()

  for cat in CATEGORIES:
    if not os.path.exists(os.path.join(dest, cat)):
      os.makedirs(os.path.join(dest, cat))
  if not os.path.exists(arch.get()):
    os.makedirs(arch.get())
  if not os.path.exists(thumb.get()):
    os.makedirs(thumb.get())

  

  thread = threading.Thread(target=startWatch)
  thread.start()

  return


class Watch():
  
  def __init__(self, dest, dropbox="./DROP_FILES_HERE"):
      self.observer = Observer()
      self.destination = dest
      self.dropbox = dropbox

  def run(self):
    lbText("Observer running.")
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
      lbText("Observer stopped.")
    
    self.observer.join()
    
  
class Handler(FileSystemEventHandler):

  def __init__(self, dest, parent):
    self.dest = dest
    self.parent = parent

  def on_created(self, event):
    if event.is_directory:
      src, dir_name = os.path.split(event.src_path)
      
      if os.path.exists(event.src_path):
       
        if dir_name != self.parent:
          # remove leading numbers
          ticket_name_list = dir_name.split('-')[1:]
          ticket_name = ""
          for tnl in ticket_name_list:
            ticket_name = ticket_name + tnl + "-"
          ticket_name = ticket_name[:-1]
          # rename original folder
          new_path = os.path.join(src, ticket_name)
          os.rename(event.src_path, new_path)

          #determine pose folder based on filename suffix
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
          archive = os.path.join(arch.get(), dir_name)

          lbText("Moving folder " + dir_name + "...")
          
          copyFilesWithProgress(new_path, destination, dir_name, "copy")

          lbText("Archiving folder " + dir_name + "...")
          copyFilesWithProgress(new_path, archive, None)

          shutil.rmtree(new_path)

          lbText("Process complete.")


def getDestinationFolder():
  dirname =  filedialog.askdirectory()
  if dirname:
    var.set(dirname)

def getDropFolder():
  dirname =  filedialog.askdirectory()
  if dirname:
    drop.set(dirname)

def getThumbFolder():
  dirname =  filedialog.askdirectory()
  if dirname:
    thumb.set(dirname)

def getArchiveFolder():
  dirname =  filedialog.askdirectory()
  if dirname:
    arch.set(dirname)

def UserFileInput(status,name, dropstatus, dropname, archstatus, archname):
  optionFrame = ttk.Frame(leftFrame)
  optionLabel = ttk.Label(optionFrame)
  optionLabel["text"] = name
  optionLabel.grid(row=2, column=0, padx=5, pady=5, sticky=W)

  var = StringVar(leftFrame)
  var.set(status)
  w = Label(optionFrame, textvariable=var)
  w.grid(row=2, column=2, padx=5, pady=5, sticky=W)
  optionFrame.grid(row=2, column=0, padx=5, pady=5, sticky=W)

  dropFrame = ttk.Frame(leftFrame)
  dropLabel = ttk.Label(dropFrame)
  dropLabel["text"] = dropname
  dropLabel.grid(row=5, column=0, padx=5, pady=5, sticky=W)

  drop = StringVar(leftFrame)
  drop.set(dropstatus)
  dropw = Label(dropFrame, textvariable=drop)
  dropw.grid(row=5, column=2, padx=5, pady=5, sticky=W)
  dropFrame.grid(row=5, column=0, padx=5, pady=5, sticky=W) 

  archFrame = ttk.Frame(leftFrame)
  archLabel = ttk.Label(archFrame)
  archLabel["text"] = archname
  archLabel.grid(row=8, column=0, padx=5, pady=5, sticky=W)
  
  arch = StringVar(leftFrame)
  arch.set(archstatus)
  archw = Label(archFrame, textvariable=arch)
  archw.grid(row=8, column=2, padx=5, pady=5, sticky=W)
  archFrame.grid(row=8, column=0, padx=5, pady=5, sticky=W)

  return var, drop, arch


def renderThumbNum():
  if thumbnail.get():
    thumbButton.grid(row=12, column=0, padx=5, pady=5, sticky=W)
    l=Label(leftFrame, text="Thumbnail Photo Index")
    l.grid(row=13, column=0, padx=5, pady=5, sticky=E)
    
    thumbNum.grid(row=13, column=1, padx=5, pady=5, sticky=W)
    thumbw.grid(row=11, column=2, padx=5, pady=5, sticky=W)
    thumbFrame.grid(row=11, column=0, padx=5, pady=5, sticky=W)
    thumbLabel.grid(row=11, column=0, padx=5, pady=5, sticky=W)
  else:
    for widget in thumbNum.winfo_children():
      widget.destroy()


if __name__ == "__main__":
  # dest = getDestinationFolder()

  root = Tk()
  root.geometry("900x550")
  root.title("FolderWatcher")

  leftFrame = Frame(root, borderwidth=2, relief="solid", width=200, height=600)
  leftFrame.grid(row=0, column=0, padx=10, pady=5)

  rightFrame = Frame(root, borderwidth=2, relief="solid", width=500, height=600)
  rightFrame.grid(row=0, column=1, padx=10, pady=5)
  pbarFrame = Frame(rightFrame)
  pbarFrame.pack(side=BOTTOM)
  ttk.Progressbar(
        pbarFrame, 
        orient="horizontal", 
        length=500,
        mode="determinate"
    ).pack()




  ttk.Button(
    leftFrame,
    text="Set Destination Folder",
    command=getDestinationFolder
  ).grid(row=1, column=0, padx=5, pady=5, sticky=W)

  

  ttk.Button(
    leftFrame,
    text="Set Drop Folder",
    command=getDropFolder
  ).grid(row=4, column=0, padx=5, pady=5, sticky=W)

  ttk.Button(
    leftFrame,
    text="Set Archive Folder",
    command=getArchiveFolder
  ).grid(row=7, column=0, padx=5, pady=5, sticky=W)





  var, drop, arch = UserFileInput(
    "None Selected", "Destination Directory: ", 
    "None Selected", "Drop Folder: ", 
    "None Selected", "Archive Folder: "
    )

  scrollbar = Scrollbar(rightFrame, orient='vertical')
  scrollbar.pack(side=RIGHT, fill=BOTH)

  lb = Listbox(rightFrame, height=30, width=20)
  lb.pack(fill=BOTH)

  lb.config(yscrollcommand = scrollbar.set)
  scrollbar.config(command = lb.yview)

  lbidx = IntVar()
  lbidx.set(0)

  thumbnail = BooleanVar(root)
  thumbNum=Entry(leftFrame, width=5)
  thumbButton = ttk.Button(
    leftFrame,
    text="Set Thumbnail Folder",
    command=getThumbFolder
  )
  thumbFrame = ttk.Frame(leftFrame)
  thumbLabel = ttk.Label(thumbFrame)
  thumbLabel["text"] = "Thumbnail Directory: "
  
  
  thumb = StringVar(leftFrame)
  thumb.set("None Selected")
  thumbw = Label(thumbFrame, textvariable=thumb)
  
  ttk.Checkbutton(
    leftFrame,
    text="Extract Thumbnails",
    variable=thumbnail,
    command=renderThumbNum
  ).grid(row=10, column=0, padx=5, pady=5, sticky=W)

  ttk.Button(
    leftFrame,
    text="Run Watcher",
    command=runWatcher
  ).grid(row=15, column=0, padx=5, pady=5, sticky=W)

  
  root.mainloop()

