# file_syncer.py - Recursively crawls a source directory tree and syncs the contents of each sub-directory and file with a target directory tree

import datetime
import webbrowser
from filecmp import cmp
from glob import glob
from os.path import exists
from os.path import isdir
from os.path import join
from os.path import isfile
from os.path import dirname
from os.path import realpath
from shutil import copytree
from shutil import copy2
from shutil import rmtree
from yaml import dump as ymldumper
from yaml import load as ymlloader
from threading import Thread
from tkinter import Tk
from tkinter import Menu
from tkinter import StringVar
from tkinter import Text
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import END
from tkinter import DISABLED
from tkinter import NORMAL
from tkinter.ttk import Button
from tkinter.ttk import Label
from tkinter.ttk import Progressbar
from tkinter import filedialog

# Starts new thread using input function as thread target
def start_thread(function):
    t = Thread(target=function)
    t.start()

# Print message to FileSyncer application message box    
def print_to_textbox(message):
    message_box.insert(END, "\n"+ message + "\n")

# Clear FileSyncer application message box    
def clear_textbox():
    message_box.delete('1.0', END)

#Method to disable/reenable closing of the root form after sync is started
def noclosingwindows():
    pass
def yesclosingwindows():
    exit()

#Disables the button controls during sync actions
def disableInputs():
    root.protocol("WM_DELETE_WINDOW", noclosingwindows)
    source_directory_button.configure(state=DISABLED)
    target_directory_button.configure(state=DISABLED)
    sync_file_button.configure(state=DISABLED)
    menubar.entryconfig("File & options", state=DISABLED)

#Enables the button controls during sync actions
def enableInputs():
    root.protocol("WM_DELETE_WINDOW", noclosingwindows)
    source_directory_button.configure(state=NORMAL)
    target_directory_button.configure(state=NORMAL)
    sync_file_button.configure(state=NORMAL)
    menubar.entryconfig("File & options", state=NORMAL)

# About popup
def about_popup():

    global separator
    title_message = "FileSyncer3\n"
    copyright_message = "Copyright (C) 2017-2018 Matthew Gray\n"
    copyright_message2 = "Copyright (C) 2018 Nguyen Dev\n"
    description_message = "Description: Recursively crawls a source directory\n tree and syncs the contents of each subdirectory\n and file with a target directory tree."
    about_message = title_message + separator+ copyright_message + copyright_message2 + separator + description_message
    
    messagebox.showinfo("About FileSyncer3", about_message)

# Confirm sync popup
def confirm_popup():
    
    result = messagebox.askyesno("Confirm Sync", "Are you sure you want to sync these folders?\nAny files currently present will be deleted!")
    if result == True:
        start_thread(main)
        progress_bar.start()
    if result == False:
        messagebox.showwarning("Sync Cancelled", "The sync process was terminated.")
    
# Stores the path of a user selected directory to a variable
def browse_directory(directory_type):
    directory_path = filedialog.askdirectory()
    if directory_type == "SOURCE":
        source_directory_path.set(directory_path)
    elif directory_type == "TARGET":
        target_directory_path.set(directory_path)
    if len(source_directory_path.get()) > 0 and len(target_directory_path.get()) > 0:
        source_directory_exists = exists(source_directory_path.get()) and isdir(source_directory_path.get())
        target_directory_exists = exists(target_directory_path.get()) and isdir(target_directory_path.get())
        if source_directory_exists and target_directory_exists:
            sync_file_button.configure(state=NORMAL)

# Recursively crawls source directory tree and syncs files and sub-directories with target directory tree        
def file_sync(source_directory, target_directory):
    for source in glob(join(source_directory, "*")):
        target = source.replace(source_directory, target_directory)
        try:
            if isdir(source):            
                if isdir(target):
                    file_sync(source, target)
                else:
                    copytree(source, target)
                    print_to_textbox("Directory synced: " + target)
            elif isfile(source):
                if not isfile(target) or (isfile(target) and not cmp(source, target, shallow=True)):              
                    copy2(source, target)
                    print_to_textbox("File synced: " + target)
        except IOError:
            print_to_textbox("IOError, sync failed: " + target)
            messagebox.showerror("Sync failed!", "During the sync, an IOError occured. Your files might be corrupted.")

# Recursively crawls target directory tree and deletes files and sub-directories that are not in source directory tree          
def file_desync(target_directory, source_directory):
    for target in glob(join(target_directory, "*")):
        source = target.replace(target_directory, source_directory)
        try:
            if isdir(target) and not isdir(source):
                rmtree(target)
                print_to_textbox("Directory Deleted: " + target)
            elif isfile(target) and not isfile(source):
                os.remove(target)
                print_to_textbox("File deleted: " + target)
            elif isdir(target):
                file_desync(target, source)
        except IOError:
            print_to_textbox("IOError, sync failed: " + target)
            messagebox.showerror("Desync failed!", "During the desync, an IOError occured. Your files might be corrupted.")
            
def update_app():
    try:
        progress_bar.start()
        disableInputs()
        clear_textbox()
        start_time = datetime.datetime.now()
        print_to_textbox("App Update start: " + str(start_time))
        print_to_textbox("Updating the app, please wait...")
        print_to_textbox(separator)
        import updater
        updater.updateNow()
        print_to_textbox("Update completed successfully!")
        print_to_textbox(separator)
        enableInputs()
        end_time = datetime.datetime.now()
        print_to_textbox("App Update took: " + str(end_time - start_time) + " to finish")
        progress_bar.stop()
        messagebox.showinfo("Update successful!", "The update was successful. The app will now restart to complete the update.")
    except Exception as e:
        progress_bar.stop()
        enableInputs()
        print_to_textbox("Update failed because of: "+str(e))
        messagebox.showerror("Update Failed!", "During the update, an exception happened:\n"+str(e))

#Reads a user configuration file and applies it to the program
def load_cfg():
    try:
        config_dir = filedialog.askopenfilename(parent=root, filetypes=[("FileSyncer3 configuration", "*.synceryml")])
        if config_dir == "":
            messagebox.showerror("Nothing selected", "Filetype must be a .synceryml (YAML file). Please select again.")
        else:
            progress_bar.start()
            disableInputs()
            with open(config_dir, 'r') as config_file:
                config_contents = ymlloader(config_file)
            localDir = config_contents["localDir"]
            externalDir = config_contents["externalDir"]
            source_directory_path.set(localDir)
            target_directory_path.set(externalDir)
            print_to_textbox("Initialized variables with .synceryml file.")
            print_to_textbox(separator)
            enableInputs()
            progress_bar.stop()
    except Exception as e:
        progress_bar.stop()
        enableInputs()
        print_to_textbox("Load from config failed because of: "+str(e))
        messagebox.showerror("")

#Makes a user configuration file
def make_cfg():
    try:
        if source_directory_path.get() == "" or target_directory_path.get() == "":
            messagebox.showwarning("Not Enough Info!", "Select your paths using the buttons below first, then try again.")
        else:
            disableInputs()
            config_dir = filedialog.asksaveasfilename(filetypes=[("FileSyncer3 configuration", "*.synceryml")])
            if config_dir == "":
                messagebox.showerror("Make config cancelled", "Filetype must be a .synceryml (YAML file). Please select again.")
                enableInputs()
            else:
                real_config_dir = config_dir+".synceryml"
                progress_bar.start()
                clear_textbox()
                start_time = datetime.datetime.now()
                print_to_textbox("Config make start: " + str(start_time))
                print_to_textbox("Making the config, please wait...")
                print_to_textbox(separator)
                config_contents = dict(
                    localDir = source_directory_path.get(),
                    externalDir = target_directory_path.get()
                )
                with open(real_config_dir, 'w') as config_file:
                    ymldumper(config_contents, config_file)
                print_to_textbox("Config make completed successfully!")
                end_time = datetime.datetime.now()
                print_to_textbox("Config make took: " + str(end_time - start_time) + " to finish")
                enableInputs()
                progress_bar.stop()
                messagebox.showinfo("Make config success!", "Your configuration file has been created. You can now select it from the menus above.")
    except IOError:
        progress_bar.stop()
        enableInputs()
        print_to_textbox("IOError, make config failed!")
        messagebox.showerror("Make config failed!", "During the making of config, an IOError occured. Your files might be corrupted.")

# Main method - Calls file_sync method on source_directory and file_desync method on target_directory       
def main():
    disableInputs()
    clear_textbox()

    source_directory = str(source_directory_path.get())
    target_directory = str(target_directory_path.get())

    start_time = datetime.datetime.now()
    print_to_textbox("File Sync start: " + str(start_time))
    
    print_to_textbox("Desyncing files from target to source.....")
    print_to_textbox(separator)
    file_desync(target_directory, source_directory)

    print_to_textbox("Syncing files from source to target.....")
    print_to_textbox(separator)
    file_sync(source_directory, target_directory)

    end_time = datetime.datetime.now()
    print_to_textbox("File Sync took: " + str(end_time - start_time) + " to finish")
    enableInputs()
    progress_bar.stop()
    messagebox.showinfo("Sync Successful!", "The sync has been completed in "+str(end_time - start_time))
    

### Configure GUI
root = Tk()
root.wm_resizable(False, False)
root.title("FileSyncer3")
root.iconbitmap(join(dirname(realpath(__file__)), "icon.ico"))
separator = "-------------------------------------------------\n"

# Add menu bar
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Use config file...", command=lambda: start_thread(load_cfg))
filemenu.add_command(label="Make config file...", command=lambda: start_thread(make_cfg))
filemenu.add_command(label="Clear log", command=clear_textbox)
filemenu.add_command(label="Quit", command=exit)
filemenu.add_separator()
filemenu.add_checkbutton(label="New UI preview (N/A)")
filemenu.add_separator()
filemenu.add_command(label="Check for updates...", command=lambda: start_thread(update_app))
menubar.add_cascade(label="File & options", menu=filemenu)

aboutmenu = Menu(menubar, tearoff=0)
aboutmenu.add_command(label="Instructions...")
aboutmenu.add_command(label="About...", command=about_popup)
aboutmenu.add_separator()
aboutmenu.add_command(label="Send feedback to developer", command=lambda: webbrowser.open("mailto:?to=vietbetatester@outlook.com&subject=Problem with FileSyncer3"))
menubar.add_cascade(label="Help & feedback", menu=aboutmenu)

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
sync_file_button.configure(state=DISABLED)
sync_file_button.grid(row=9, column=3)

# Displays messages to application user                 
message_box = scrolledtext.ScrolledText(master=root)
message_box.grid(row=11, column=3)
print_to_textbox("Welcome to FileSyncer3! Please read the instructions in the 'Help & feedback' menu above before using this application.")
print_to_textbox("For support, click the 'Send feedback to developer' option in the 'Help & feedback' menu.")
print_to_textbox(separator)

progress_bar = Progressbar(root, orient="horizontal", length=250, mode="indeterminate")
progress_bar.grid(row=13, column=3)
progress_bar.stop()

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