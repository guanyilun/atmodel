# project.py
# Load and save project files

# load project file into GUI
def open(gui, proj_file):
    
    # update state
    gui.changed = False
    gui.proj_file = proj_file

# save current state as project file
def save(gui, proj_file):
    
    # update state
    gui.changed = False
    gui.proj_file = proj_file
