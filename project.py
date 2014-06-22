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
    
    # add in all widget collections
    for name, collect in gui.collections.iteritems():
        
        # build a list of input fields
        field_str = "id"
        for key, widget in collect[0].inputs.iteritems():
            field_str += "," + key
        
        # create table for collection
        cur.execute("create table " + name + " (" + field_str + ")")
        
        # insert values of widgets for every set in collection
        
    
    # close connection
    db.close()
    
    # update state
    gui.changed = False
    gui.proj_file = proj_file
