# folderwatcher

## create virtual environment

python3 -m pip venv venv

## start venv

source venv/bin/activate

## install dependencies

python3 -m pip install -r requirements.txt

## run the program

python3 app.py


## details

the app will launch a directory selector pop-up - choose the destination folder in which you want the app to sort the captures. the app will create the subdirectories for the different types of captures.

drag capture folders into the DROP_FILES_HERE/ folders. the app will ignore files that aren't in directories. it will create the new filename (omitting the leading numbers, etc) and move the folder into the appropriate subdirectories in the destination forder you selected.