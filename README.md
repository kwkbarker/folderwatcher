# folderwatcher

## install dependencies

install python 3.
install git.
## clone this repository

navigate in the terminal to the directory where you want the action folder. enter the command:

    git clone https://github.com/kwkbarker/folderwatcher.git

## create virtual environment

### mac
python3 -m pip venv venv

### windows
pip install virtualenv
virtualenv --python C:\Path\To\Python\python.exe venv

## start venv

source venv/bin/activate  //mac

.\venv\Scripts\activate  //windows

## install dependencies

python3 -m pip install -r requirements.txt

## run the program

python3 app.py [optional: path/to/action/folder]


## details

the app will launch a directory selector pop-up - choose the DESTINTION folder in which you want the app to sort the captures. the app will create the subdirectories for the different types of captures.

you may specify an ACTION folder as an argument when launching the program from the command line - if you do not, an action folder called DROP_FILES_HERE/ will be created within the folderwatcher/ project folder.

drag capture folders into the ACTION folder. the app will ignore any files that aren't in directories - it expects a directory with a name "xxx-xxx-xxx-TICKET_NAME". it will rename the folder as the TICKET_NAME (omitting the leading numbers, etc) and move the folder into the appropriate subdirectory in the destination folder you selected.