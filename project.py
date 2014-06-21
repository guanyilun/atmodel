# project.py
# Load and save project files

import os
import sqlite3

# load project file into GUI
def open(gui, proj_file):
    
    # update state
    gui.changed = False
    gui.proj_file = proj_file

# save current state as project file
def save(gui, proj_file):
    
    # delete any existing file
    try:
        os.remove(proj_file)
    except Exception:
        pass
    
    # create connection to database file
    db = sqlite3.connect(str(proj_file))
    cur = db.cursor()
    
    # create tables
    
    # write state settings
    
    # close connection
    db.close()
    
    # update state
    gui.changed = False
    gui.proj_file = proj_file
