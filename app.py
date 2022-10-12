import threading
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import cv2 as cv
import multiprocessing as mp

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


class Watch():
  
  def __init__(self, dest, dropbox):
      self.observer = Observer()
      self.destination = dest
      self.dropbox = dropbox

  def run(self, gui):
    if not os.path.isdir(self.dropbox):
      os.makedirs(self.dropbox)
    rt, parent_folder = os.path.split(self.dropbox)
    event_handler = Handler(self.destination, parent_folder, gui)
  
    self.observer.schedule(event_handler, self.dropbox, recursive=True)
    self.observer.start()
    
    try:
      while gui.watchdog != None:
        print("Watch running...")
        time.sleep(5)
    except KeyboardInterrupt:
      self.observer.stop()
    
    if self.observer:
      self.observer.join()

  def stop(self):
    self.observer.stop()
    self.observer.join()
    self.observer = None
    
  
class Handler(FileSystemEventHandler):

  def __init__(self, dest, parent, gui):
    self.dest = dest
    self.parent = parent
    self.gui = gui

  def on_created(self, event):
    if event.is_directory:
      src, dir_name = os.path.split(event.src_path)
      
      if os.path.exists(event.src_path):
       
        if dir_name != self.parent:
          # remove leading numbers
          ticket_name_list = dir_name.split('-')
          if len(ticket_name_list) > 1 and ticket_name_list[0].isnumeric()\
              and ticket_name_list[1].isnumeric():
            ticket_name = ticket_name_list[1]
            for tnl in ticket_name_list[2:]:
              ticket_name = ticket_name + "-" + tnl
          else:
            ticket_name = dir_name
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
          archive = os.path.join(self.gui.arch.get(), dir_name)

          self.gui.lbText("Moving folder " + dir_name + "...")
          
          self.gui.copyFilesWithProgress(new_path, destination, dir_name, "copy")

          self.gui.lbText("Archiving folder " + dir_name + "...")
          self.gui.copyFilesWithProgress(new_path, archive, None)

          shutil.rmtree(new_path)

          self.gui.lbText("Process complete.")


class GUI:

  def setButtonColorRG(self, button, variable):
    # SET BUTTON COLORS
    if variable.get() == "None Selected":
      button.config(style= "redButton.TButton")
    else:
      button.config(style= "greenButton.TButton")

  def checkRunButtonState(self):
    if self.var.get() == "None Selected" or self.drop.get() == "None Selected" or \
      self.arch.get() == "None Selected":
      self.runButton.state(["disabled"])
    else:
      if self.thumbnail.get():
        if self.thumb.get() == "None Selected":
          self.runButton.state(["disabled"])
        else:
          self.runButton.state(["!disabled"])
      else:
        self.runButton.state(["!disabled"])


  def getDestinationFolder(self):
    dirname =  filedialog.askdirectory()
    if dirname:
      self.var.set(dirname)
      folder = os.path.split(dirname)[-1]
      self.destAbbr.set(f".../{folder}")
    self.setButtonColorRG(self.destButton, self.var)
    self.checkRunButtonState()

  def getDropFolder(self):
    dirname =  filedialog.askdirectory()
    if dirname:
      self.drop.set(dirname)
      folder = os.path.split(dirname)[-1]
      self.dropAbbr.set(f".../{folder}")
    self.setButtonColorRG(self.dropButton, self.drop)
    self.checkRunButtonState()


  def getThumbFolder(self, thumbButton):
    dirname =  filedialog.askdirectory()
    if dirname:
      self.thumb.set(dirname)
      folder = os.path.split(dirname)[-1]
      self.thumbAbbr.set(f".../{folder}")
    self.setButtonColorRG(thumbButton, self.thumb)
    self.checkRunButtonState()

  def getArchiveFolder(self):
    dirname =  filedialog.askdirectory()
    if dirname:
      self.arch.set(dirname)
      folder = os.path.split(dirname)[-1]
      self.archAbbr.set(f".../{folder}")
    self.setButtonColorRG(self.archButton, self.arch)
    self.checkRunButtonState()


  def copyFilesWithProgress(self, src, dest, thumbName, protocol="move"):

    # PROGRESS BAR
    for widget in self.pbarFrame.winfo_children():
      widget.destroy()
    p = ttk.Progressbar(
        self.pbarFrame, 
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
                if self.thumbnail.get():
                  if not os.path.exists(os.path.join(self.thumb.get(), f"{thumbName}.jpg")):
                    if f"{self.thumbNum.get()}.jpg" in sfile:
                      newFilename = f"{thumbName}.jpg"
                      newSrc = os.path.join(path, newFilename)
                      os.rename(srcFile, newSrc)
                      destThumb = os.path.join(self.thumb.get(), newFilename)
                      img = cv.imread(newSrc)
                      scale_percent = 60 # percent of original size
                      width = int(img.shape[1] * scale_percent / 100)
                      height = int(img.shape[0] * scale_percent / 100)
                      dim = (width, height)
                      cv.resize(img, dim, interpolation = cv.INTER_AREA)
                      shutil.move(os.path.join(newSrc), destThumb)
            
            else:
                shutil.move(srcFile, destFile)


            numCopied += 1

            p["value"] = int((numCopied/numFiles) * 100)

  def lbText(self, text):
    self.lbidx.set(self.lbidx.get() +1)
    self.lb.insert(self.lbidx.get(), text)

  def startWatch(self):
    if self.watchdog == None:
      self.watchdog = Watch(self.var.get(), self.drop.get())
      self.lbText("Watcher is running.")
      self.runButton.config(
        style="redButton.TButton",
        text="Watching..."
        )
      self.runButton.state(["disabled"])
      self.watchdog.run(self)
    else:
      self.lbText("Watcher already running.")

  
  def stopWatch(self):
    if self.watchdog != None:
      self.lbText("Watcher stopped.")
      self.watchdog.stop()
      self.watchdog = None
      self.thread.join()
      self.root.destroy()
    else:
      self.lbText("No watcher is running.")
      self.root.destroy()

  def runWatcher(self):
    dest = self.var.get()

    for cat in CATEGORIES:
      if not os.path.exists(os.path.join(dest, cat)):
        os.makedirs(os.path.join(dest, cat))
    if not os.path.exists(self.arch.get()):
      os.makedirs(self.arch.get())
    if not os.path.exists(self.thumb.get()):
      os.makedirs(self.thumb.get())

    if not self.thread:
      self.thread = threading.Thread(target=self.startWatch)
      self.thread.start()

  def renderThumbNum(self):
    if self.thumbnail.get():
      # set thumb dir button
      thumbButton = ttk.Button(
        self.thumbFrame,
        text="Set Thumbnail Folder",
        command=lambda: self.getThumbFolder(thumbButton)
      )

      # Thumb DIR indicator
      thumbLabel = ttk.Label(self.thumbFrame)
      thumbLabel["text"] = "Thumbnail Directory: "
      thumbButton.config(style= "redButton.TButton")
      thumbw = Label(self.thumbFrame, textvariable=self.thumbAbbr)
      thumbButton.grid(row=11, column=0, padx=5, pady=5, sticky=W)
      l=Label(self.thumbFrame, text="Thumbnail Photo Index")
      l.grid(row=13, column=0, padx=5, pady=5, sticky=E)
      
      self.thumbNum.grid(row=13, column=1, padx=5, pady=5, sticky=W)
      thumbw.grid(row=12, column=2, padx=5, pady=5, sticky=W)
      self.thumbFrame.grid(row=12, column=0, padx=5, pady=5, sticky=W)
      thumbLabel.grid(row=12, column=0, padx=5, pady=5, sticky=W)
      self.checkRunButtonState()
    else:
      for widget in self.thumbFrame.winfo_children():
        widget.destroy()
      self.checkRunButtonState()

  def UserFileInput(self, status,name, dropstatus, dropname, archstatus, archname):
    optionFrame = ttk.Frame(self.leftFrame)
    optionLabel = ttk.Label(optionFrame)
    optionLabel["text"] = name
    optionLabel.grid(row=2, column=0, padx=5, pady=5, sticky=W)

    self.var = StringVar(self.leftFrame)
    self.destAbbr = StringVar(self.leftFrame)
    self.var.set(status)
    self.destAbbr.set(status)
    w = Label(optionFrame, textvariable=self.destAbbr)
    w.grid(row=2, column=2, padx=5, pady=5, sticky=W)
    optionFrame.grid(row=2, column=0, padx=5, pady=5, sticky=W)

    dropFrame = ttk.Frame(self.leftFrame)
    dropLabel = ttk.Label(dropFrame)
    dropLabel["text"] = dropname
    dropLabel.grid(row=5, column=0, padx=5, pady=5, sticky=W)

    self.drop = StringVar(self.leftFrame)
    self.dropAbbr = StringVar(self.leftFrame)
    self.drop.set(dropstatus)
    self.dropAbbr.set(dropstatus)
    dropw = Label(dropFrame, textvariable=self.dropAbbr)
    dropw.grid(row=5, column=2, padx=5, pady=5, sticky=W)
    dropFrame.grid(row=5, column=0, padx=5, pady=5, sticky=W) 

    archFrame = ttk.Frame(self.leftFrame)
    archLabel = ttk.Label(archFrame)
    archLabel["text"] = archname
    archLabel.grid(row=8, column=0, padx=5, pady=5, sticky=W)
    
    self.arch = StringVar(self.leftFrame)
    self.archAbbr = StringVar(self.leftFrame)
    self.arch.set(archstatus)
    self.archAbbr.set(archstatus)
    archw = Label(archFrame, textvariable=self.archAbbr)
    archw.grid(row=8, column=3, padx=5, pady=5, sticky=E)
    archFrame.grid(row=8, column=0, padx=5, pady=5, sticky=W)

  def __init__(self):
      self.watchdog = None
      self.thread = None

      self.root = Tk()
      self.root.geometry("650x550")
      self.root.title("FolderWatcher")
      self.root.config(bg="grey")

      style = ttk.Style(self.root)
      style.theme_use('default')
      style.configure("redButton.TButton", background="red")
      style.configure("greenButton.TButton", background="green")
      style.configure("blueButton.TButton", background="blue", foreground="white")
      style.configure("yellowButton.TButton", background="yellow")
      style.configure("TFrame", background="lightgrey")
      style.configure("TLabel", background="lightgrey")

      self.root.grid_rowconfigure(0, minsize=400, weight=1)
      self.root.grid_columnconfigure(0, minsize=350, weight=1) 
      self.root.grid_columnconfigure(1, weight=1)

      self.leftFrame = Frame(self.root, borderwidth=2, relief="solid", width=400, height=600)
      self.leftFrame.config(background="lightgrey")
      self.leftFrame.grid(row=0, column=0, padx=10, pady=5)

      self.rightFrame = Frame(self.root, borderwidth=2, relief="solid", width=250, height=600)
      self.rightFrame.grid(row=0, column=1, padx=10, pady=5, sticky=E)

      self.exitButton = ttk.Button(self.root, command=self.stopWatch,  text="EXIT")
      self.exitButton.grid(row=100, column=0, sticky=SW, padx=5, pady=5)

      self.pbarFrame = Frame(self.rightFrame)
      self.pbarFrame.pack(side=BOTTOM)
      ttk.Progressbar(
            self.pbarFrame, 
            orient="horizontal", 
            length=500,
            mode="determinate"
        ).pack()

      self.destButton = ttk.Button(
        self.leftFrame,
        text="Set Destination Folder",
        command=self.getDestinationFolder
      )
      self.destButton.grid(row=1, column=0, padx=5, pady=5, sticky=W)
      self.destButton.config(style= "redButton.TButton")
      

      self.dropButton = ttk.Button(
        self.leftFrame,
        text="Set Drop Folder",
        command=self.getDropFolder
      )
      self.dropButton.grid(row=4, column=0, padx=5, pady=5, sticky=W)
      self.dropButton.config(style= "redButton.TButton")


      self.archButton = ttk.Button(
        self.leftFrame,
        text="Set Archive Folder",
        command=self.getArchiveFolder
      )
      self.archButton.grid(row=7, column=0, padx=5, pady=5, sticky=W)
      self.archButton.config(style= "redButton.TButton")

      self.UserFileInput(
        # "/Users/kevinbarker/Dropbox/Mac/Desktop/dest/", "Destination Directory: ", 
        # "/Users/kevinbarker/Dropbox/Mac/Desktop/drop/", "Drop Folder: ", 
        # "/Users/kevinbarker/Dropbox/Mac/Desktop/arch/", "Archive Folder: "

        "None Selected", "Destination Directory: ", 
        "None Selected", "Drop Folder: ", 
        "None Selected", "Archive Folder: "
        )
      

      scrollbar = Scrollbar(self.rightFrame, orient='vertical')
      scrollbar.pack(side=RIGHT, fill=BOTH)

      self.lb = Listbox(self.rightFrame, height=65, width=45)
      self.lb.pack(fill=BOTH)

      self.lb.config(yscrollcommand = scrollbar.set)
      scrollbar.config(command = self.lb.yview)

      self.lbidx = IntVar()
      self.lbidx.set(0)

      # FRAME for content that appears on thumbnail check
      self.thumbFrame = ttk.Frame(self.leftFrame)
      # field to enter thumbnail index #
      self.thumbNum=Entry(self.thumbFrame, width=5)

      # thumb variables
      self.thumb = StringVar(self.leftFrame)
      self.thumbAbbr = StringVar(self.leftFrame)
      self.thumb.set("None Selected")
      self.thumbAbbr.set("None Selected")
      
      #THUMBNAIL CHECKBOX
      self.thumbnail = BooleanVar(self.root)
      ttk.Checkbutton(
        self.leftFrame,
        text="Extract Thumbnails",
        variable=self.thumbnail,
        command=self.renderThumbNum
      ).grid(row=10, column=0, padx=5, pady=5, sticky=W)

      self.runButton = ttk.Button(
        self.leftFrame,
        text="Run Watcher",
        command=self.runWatcher
      )
      self.runButton.config(style="blueButton.TButton")
      self.runButton.state(["disabled"])
      self.runButton.grid(row=15, column=0, padx=5, pady=5, sticky=S)
 
      self.root.mainloop()

if __name__ == "__main__":
  GUI()


