# file_syncer.py - Recursively crawls a source directory tree and syncs the contents of each sub-directory and file with a target directory tree

import datetime
import filecmp
import glob
import os
import shutil
import threading
from tkinter import Tk
from tkinter import Menu
from tkinter import StringVar
from tkinter import Text
from tkinter import Toplevel
from tkinter import ACTIVE
from tkinter import END
from tkinter.ttk import Button
from tkinter.ttk import Label
from tkinter import filedialog

# Starts new thread using input function as thread target
def start_thread(function):
    t = threading.Thread(target=function)
    t.start()

# Print message to FileSyncer application message box    
def print_to_textbox(message):
    message_box.insert(END, message + "\n")

# Clear FileSyncer application message box    
def clear_textbox():
    message_box.delete('1.0', END)

# Center popup box relative to root    
def center_popup(toplevel):
    root.update_idletasks()
    toplevel.update_idletasks()
    w = toplevel.winfo_width()
    h = toplevel.winfo_height()
    x = root.winfo_width()/2 + root.winfo_x()-132
    y = root.winfo_height()/2 + root.winfo_y()-55
    toplevel.geometry("%dx%d+%d+%d" % (w, h, x, y))
  
# About popup
def about_popup():
    
    global separator
    title_message = "FileSyncer3\n"
    copyright_message = "Copyright (C) 2017 Matthew Gray\n"
    copyright_message2 = "Copyright (C) 2018 Nguyen Dev\n"
    description_message = "Description: Recursively crawls a source directory\n tree and syncs the contents of each subdirectory\n and file with a target directory tree."
    about_message = title_message + separator+ copyright_message + copyright_message2 + separator + description_message
    
    toplevel = Toplevel(padx=5, pady=5, takefocus=True)
    toplevel.wm_title("About")
    label = Label(toplevel, text=about_message)
    label.grid(row=0, column=2)
    center_popup(toplevel)
    toplevel.grab_set()

# Confirm sync popup
def confirm_popup():
    
    confirm_message = "Are you sure you want to sync these folders?"
    
    toplevel = Toplevel(padx=5, pady=5, takefocus=True)
    toplevel.wm_title("Confirm Sync")
    label = Label(toplevel, text=confirm_message)
    label.grid(row=0, column=1)
    yes_button = Button(master=toplevel, text="Yes", command=lambda: confirm_sync(toplevel))
    yes_button.grid(row=2, column=1)
    no_button = Button(master=toplevel, text="No", command=toplevel.destroy)
    no_button.grid(row=3, column=1)
    center_popup(toplevel)
    toplevel.grab_set()

# Starts main thread after confirm button clicked
def confirm_sync(toplevel):
    toplevel.destroy()
    start_thread(main)
    
# Stores the path of a user selected directory to a variable
def browse_directory(directory_type):
    global source_directory_path
    global target_directory_path
    global sync_file_button
    directory_path = filedialog.askdirectory()
    if directory_type == "SOURCE":
        source_directory_path.set(directory_path)
    elif directory_type == "TARGET":
        target_directory_path.set(directory_path)
    if len(source_directory_path.get()) > 0 and len(target_directory_path.get()) > 0:
        source_directory_exists = os.path.exists(source_directory_path.get()) and os.path.isdir(source_directory_path.get())
        target_directory_exists = os.path.exists(target_directory_path.get()) and os.path.isdir(target_directory_path.get())
        if source_directory_exists and target_directory_exists:
            sync_file_button.config(state=ACTIVE)

# Recursively crawls source directory tree and syncs files and sub-directories with target directory tree        
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
                    print_to_textbox("\n")
            elif os.path.isfile(source):
                if not os.path.isfile(target) or (os.path.isfile(target) and not filecmp.cmp(source, target, shallow=True)):              
                    shutil.copy(source, target)
                    print_to_textbox("File synced: " + target)
                    print_to_textbox("\n")
        except IOError:
            print_to_textbox("IOError, sync failed: " + target)
            print_to_textbox("\n")

# Recursively crawls target directory tree and deletes files and sub-directories that are not in source directory tree          
def file_desync(target_directory, source_directory):
    for target in glob.glob(os.path.join(target_directory, "*")):
        source = target.replace(target_directory, source_directory)
        try:
            if os.path.isdir(target) and not os.path.isdir(source):
                shutil.rmtree(target)
                print_to_textbox("Directory Deleted: " + target)
                print_to_textbox("\n")
            elif os.path.isfile(target) and not os.path.isfile(source):
                os.remove(target)
                print_to_textbox("File deleted: " + target)
                print_to_textbox("\n")
            elif os.path.isdir(target):
                file_desync(target, source)
        except IOError:
            print_to_textbox("IOError, sync failed: " + target)
            print_to_textbox("\n")
            
# Main method - Calls file_sync method on source_directory and file_desync method on target_directory       
def main():

    global separator
    clear_textbox()

    source_directory = str(source_directory_path.get())
    target_directory = str(target_directory_path.get())

    start_time = datetime.datetime.now()
    print_to_textbox("File Sync start: " + str(start_time))
    print_to_textbox("\n")
    
    print_to_textbox("Desyncing files from target to source.....")
    print_to_textbox(separator)
    file_desync(target_directory, source_directory)

    print_to_textbox("Syncing files from source to target.....")
    print_to_textbox(separator)
    file_sync(source_directory, target_directory)

    end_time = datetime.datetime.now()
    print_to_textbox("File Sync took: " + str(end_time - start_time) + " to finish")

### Configure GUI
root = Tk()
root.title("FileSyncer")
separator = "-------------------------------------------------\n"

# Add menu bar
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="About", command=about_popup)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.destroy)
menubar.add_cascade(label="Commands", menu=filemenu)

# String variable used to hold source directory path
source_directory_path = StringVar()

# String variable used to hold target directory path
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
sync_file_button = Button(text="Sync Files", command=confirm_popup)
sync_file_button.grid(row=9, column=3)

# Displays messages to application user                 
message_box = Text(master=root)
message_box.grid(row=11, column=3)

# Set menubar object as root menu
root.config(menu=menubar)
root.update()

# Center root menu on application startup
root.update_idletasks()
w = root.winfo_reqwidth()
h = root.winfo_reqheight()
x = (root.winfo_screenwidth() - w) / 2
y = (root.winfo_screenheight() - h) / 2
root.geometry("%dx%d+%d+%d" % (w, h, x, y))

# Tkinter application main loop
root.mainloop()
