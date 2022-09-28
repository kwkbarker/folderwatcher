import sys
from tkinter import *
from tkinter import ttk

class ProgressBar(object):

    def __init__(self, message, width=20, progressSymbol='O', emptySymbol='X'):
        self.width = width

        if self.width < 0:
            self.width = 0

        self.message = message
        self.progressSymbol = progressSymbol
        self.emptySymbol = emptySymbol


    def update(self, progress):
        totalBlocks = self.width
        filledBlocks = int(round(progress / (100 / float(totalBlocks)) ))
        emptyBlocks = totalBlocks - filledBlocks

        progressBar = self.progressSymbol * filledBlocks + \
        self.emptySymbol * emptyBlocks

        if not self.message:
            self.message = ''

        progressMessage = '\r{0} {1} {2}%'.format(self.message,
        progressBar,
        progress)
        if progress != 100:
            sys.stdout.write(progressMessage)
        else:
            sys.stdout.write(progressMessage + "\n")
        sys.stdout.flush()

    def calculateAndUpdate(self, done, total):
        progress = int(round( (done / float(total)) * 100) )
        self.update(progress)

import os

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

import shutil

def copyFilesWithProgress(src, dest, protocol="move"):
    # p = ProgressBar('Moving folders... ')

    p = ttk.Progressbar(
        root, 
        orient="horizontal", 
        length=320,
        mode="determinate"
    )

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
            else:
                shutil.move(srcFile, destFile)

            numCopied += 1

            p["value"] = numCopied/numFiles

