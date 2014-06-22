# project.py
# Load and save project files

import os
import sqlite3

import dyngui
import inputs

# load project file into GUI
def open(gui, proj_file):
    
    # create connection to database file
    db = sqlite3.connect(str(proj_file))
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    
    # clear all collections of groups
    for name, collect in gui.collections.iteritems():
        
        for i in xrange(len(collect) - 1, -1, -1):
            group = collect[i]
            group.group_widget.setParent(None) # prevent display
            group.group_widget.deleteLater() # remove from list of QGroupBox widgets
            collect.remove(group) # remove from collection
    
    # load groups from database into collections
    for name, collect in gui.collections.iteritems():
        
        if name == "compos":
            continue # handle composite tab later
        
        # fetch all rows from the table associated with the collection
        cur.execute("select * from " + name)
        rows = cur.fetchall()
        
        # convert each row to a group of widgets
        for row in rows:
            # call the function generating a list of inputs associated with the collection
            inputs_set = getattr(inputs, name)(gui, row)
            
            # insert the newly created group of widgets into the collection
            collect_list = getattr(gui, name + "_list") # form layout containing widget groups
            collect.append(dyngui.collect_obj(inputs_set, dyngui.new_group(collect_list, inputs_set)))
    
    # update non-collection groups with saved values
    
    # update free-floating widgets with saved values
    
     # close connection
    db.close()
    
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
        if len(collect) > 0:
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
    
    # groups of widgets not part of any collections
    cur.execute("create table misc (groupname, key, value)")
    
    for name, group in gui.groups.iteritems(): # loop through all groups
        for key, wid in group.iteritems(): # loop through all widgets in each group
            cur.execute("insert into misc values ('"
                    + name + "', '" + key + "', '"
                    + str(dyngui.widget_val(wid.widget)) + "')")
    
    # free-floating widgets not part of any group or collection
    for key, widget in gui.floating.iteritems():
        cur.execute("insert into misc values ('', '"
                + key + "', '" + str(dyngui.widget_val(widget)) + "')")
    
    # close connection
    db.commit()
    db.close()
    
    # update state
    gui.changed = False
    gui.proj_file = proj_file
