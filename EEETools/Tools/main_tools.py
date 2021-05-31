from EEETools.Tools.modules_importer import *
from tkinter import filedialog
from EEETools import costants
from shutil import copyfile
import tkinter as tk
import os, pyrebase


def calculate():

    root = tk.Tk()
    root.withdraw()
    excel_path = filedialog.askopenfilename()
    calculate_excel(excel_path)


def paste_default_excel_file():
    __import_file("Default Excel Input_eng.xlsm")


def paste_user_manual():
    __import_file("User Guide-eng.pdf")


def paste_components_documentation():
    __import_file("Component Documentation-eng.pdf")


def __import_file(filename):

    root = tk.Tk()
    root.withdraw()

    dir_path = filedialog.askdirectory()
    file_path = os.path.join(dir_path, filename)
    file_position = os.path.join(costants.RES_DIR, "Other", filename)

    if not os.path.isfile(file_position):

        __retrieve_file(filename)

    copyfile(file_position, file_path)


def __retrieve_file(filename):

    firebase = pyrebase.initialize_app(costants.FIREBASE_CONFIG)
    storage = firebase.storage()

    file_position = os.path.join(costants.RES_DIR, "Other", filename)
    storage.child("3ETool_res/Other/" + filename).download("", file_position)