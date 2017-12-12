# Author: Matthew Gray
# Copyright (C) 2017 Matthew Gray
# Last Modified: 12/12/2017
# file_syncer.py - Recursively crawls a source directory and syncs the contents of each sub directory and file with a target directory.

import datetime
import filecmp
import glob
import os
import shutil
import threading
from tkinter import *
import tkFileDialog 

# Starts new thread using input function as thread target
def start_thread(function):
    t = threading.Thread(target=function)
    t.start()

# Print message to FileSyncer application message box    
def print_to_textbox(message):
    global texbox1
    message_box.insert(END, message + "\n")

# Stores the path of a user selected directory to a variable
def browse_directory(directory_type):
    global source_directory_path
    global target_directory_path
    global sync_file_button
    directory_path = tkFileDialog.askdirectory()
    if directory_type == "SOURCE":
        source_directory_path.set(directory_path)
    elif directory_type == "TARGET":
        target_directory_path.set(directory_path)
    if len(source_directory_path.get()) > 0 and len(target_directory_path.get()) > 0: 
        sync_file_button.config(state=ACTIVE)

# Recursively crawls source directory tree and syncs files and sundirectories with target directory tree        
def file_sync(source_directory, target_directory):
    for source in glob.glob(os.path.join(source_directory, "*")):
        target = source.replace(source_directory, target_directory)
        try:
            if os.path.isdir(source):            
                if os.path.isdir(target):
                    file_sync(source, target)
                else:
                    shutil.copytree(source, target)
                    print_to_textbox("Directory synced: " + target)
            elif os.path.isfile(source):
                if not os.path.isfile(target) or (os.path.isfile(target) and not filecmp.cmp(source, target, shallow=True)):              
                    shutil.copy(source, target)
                    print_to_textbox("File synced: " + target)
        except IOError:
            print_to_textbox("IOError, sync failed: " + target)

# Recursively crawls target directory tree and deleted files and sundirectories that are not in source directory tree          
def file_desync(target_directory, source_directory):
    for target in glob.glob(os.path.join(target_directory, "*")):
        source = target.replace(target_directory, source_directory)
        try:
            if os.path.isdir(target) and not os.path.isdir(source):
                shutil.rmtree(target)
                print_to_textbox("Directory Deleted: " + target)
            elif os.path.isfile(target) and not os.path.isfile(source):
                os.remove(target)
                print_to_textbox("File deleted: " + target)
            elif os.path.isdir(target):
                file_desync(target, source)
        except IOError:
            print_to_textbox("IOError, sync failed: " + target)
            
# Main method - Calls file_sync method on source_directory and file_desync method on target_directory       
def main():

    source_directory = str(source_directory_path.get())
    target_directory = str(target_directory_path.get())

    start_time = datetime.datetime.now()
    print_to_textbox("File Sync start: " + str(start_time))
    
    print_to_textbox("Desyncing files from target to source.....")
    file_desync(target_directory, source_directory)

    print_to_textbox("Syncing files from source to target.....")
    file_sync(source_directory, target_directory)

    end_time = datetime.datetime.now()
    print_to_textbox("File Sync took: " + str(end_time - start_time) + " to finish")

### Configure GUI
root = Tk()
root.title("FileSyncer")

# Add menu bar
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="About")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.destroy)
menubar.add_cascade(label="File", menu=filemenu)

# Sting variable used to hold source directory path
source_directory_path = StringVar()

# Sting variable used to hold target directory path
target_directory_path = StringVar()

# Source Directory browse button
source_directory_button = Button(text="Source Directory", command= lambda: browse_directory("SOURCE"))
source_directory_button.grid(row=0, column=3)

# Source Directory path label
source_directory_label = Label(master=root, textvariable=source_directory_path)
source_directory_label.grid(row=1, column=3)

# Target Directory browse button
target_directory_button = Button(text="Target Directory", command=lambda: browse_directory("TARGET"))
target_directory_button.grid(row=3, column=3)

# Target Directory path label
target_directory_label = Label(master=root, textvariable=target_directory_path)
target_directory_label.grid(row=4, column=3)

# Sync Files button - Starts file sync process by calling main method with new thread. Button is only activated after Source Directory and Target Directory
# paths have been selected to sync
sync_file_button = Button(text="Sync Files", state=DISABLED, command=lambda: start_thread(main))
sync_file_button.grid(row=9, column=3)

# Displays messages to application user                 
message_box = Text(master=root)
message_box.grid(row=11, column=3)

# Set menubar object as root menu
root.config(menu=menubar)

# Tkinter application main loop
mainloop()
