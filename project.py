# project.py
# Load and save project files

import os
import sqlite3

import dyngui
import inputs

# load new project
def new (gui):

    gui.changed = False
    gui.proj_file = ""

    # clear all collections of groups
    for name, collect in gui.collections.iteritems():

        for i in xrange(len(collect) - 1, -1, -1):
            group = collect[i]
            group.group_widget.setParent(None) # prevent display
            group.group_widget.deleteLater() # remove from list of QGroupBox widgets
            collect.remove(group) # remove from collection

    # add one group to each collection
    atmos_set0 = inputs.atmos(gui)
    gui.atmos_collection.append(dyngui.collect_obj(atmos_set0,
            dyngui.new_group(gui.atmos_list, atmos_set0)))

    galactic_set0 = inputs.galactic(gui)
    gui.galactic_collection.append(dyngui.collect_obj(galactic_set0,
            dyngui.new_group(gui.galactic_list, galactic_set0)))

    mirror_set0 = inputs.mirror(gui)
    gui.mirror_collection.append(dyngui.collect_obj(mirror_set0,
            dyngui.new_group(gui.mirror_list, mirror_set0)))

    zodiac_set0 = inputs.zodiac(gui)
    gui.zodiac_collection.append(dyngui.collect_obj(zodiac_set0,
            dyngui.new_group(gui.zodiac_list, zodiac_set0)))

    signal_set0 = inputs.signal(gui)
    gui.signal_collection.append(dyngui.collect_obj(signal_set0,
            dyngui.new_group(gui.signal_list, signal_set0)))

    compos_set0 = inputs.compos(gui)
    gui.compos_collection.append(dyngui.collect_obj(compos_set0,
            dyngui.new_group_tab(gui.compos_tabs, compos_set0, "New")))

# load project file into GUI
def open (gui, proj_file):

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

    ## Collections

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

    # load all tabs for composite calculations (where groups are placed in individual tabs)
    cur.execute("select * from compos")
    rows = cur.fetchall()

    for row in rows:
        inputs_set = inputs.compos(gui, row)
        gui.collections["compos"].append(dyngui.collect_obj(inputs_set,
                dyngui.new_group_tab(gui.compos_tabs, inputs_set,
                row["_label"] == "" and "New" or row["_label"])))

    ## Non-Collection Groups and Free-Floating Widgets

    cur.execute("select * from misc")
    rows = cur.fetchall()

    # organize values by group
    misc = {} # organized dictionary of all the rows
    for row in rows:
        if row["groupname"] in misc:
            misc[row["groupname"]][row["key"]] = row["value"]
        else: # first key in this group
            misc[row["groupname"]] = {row["key"] : row["value"]}

    # set values
    for name, group in misc.iteritems():

        # group of free-floating widget values
        if name == "":
            for key, value in group.iteritems():
                dyngui.widget_val_restore(gui.floating[key], value)

        # other non-collection group of widgets
        else:
            for key, value in group.iteritems():
                dyngui.widget_val_restore(gui.groups[name][key].widget, value)

     # close connection
    db.close()

    # update state
    gui.changed = False
    gui.proj_file = proj_file

# save current state as project file
def save (gui, proj_file):

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
