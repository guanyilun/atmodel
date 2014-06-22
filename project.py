# project.py
# Load and save project files

import os
import sqlite3

import dyngui

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
        for key, wid in collect[0].inputs.iteritems():
            field_str += "," + key
        
        # create table for collection
        cur.execute("create table " + name + " (" + field_str + ")")
        
        # insert values of widgets for every set in collection
        for i, group in enumerate(collect):
            values = str(i) # id
            
            # append value of each widget within the group
            for key, wid in group.inputs.iteritems():
                values += ", '" + str(dyngui.widget_val(wid.widget)) + "'"
            
            # insert widget group as row in table
            cur.execute("insert into " + name + " values (" + values + ")")
    
    # close connection
    db.close()
    
    # update state
    gui.changed = False
    gui.proj_file = proj_file
