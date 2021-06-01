from EEETools.MainModules.main_module import CalculationOptions
from EEETools.Tools.modules_importer import calculate_excel
import urllib.request, warnings
from tkinter import filedialog
from EEETools import costants
from shutil import copyfile
import tkinter as tk
import os, pyrebase
import ssl


def calculate(calculate_on_pf_diagram = True, loss_cost_is_zero = True, valve_is_dissipative = True, condenser_is_dissipative = True):

    root = tk.Tk()
    root.withdraw()
    excel_path = filedialog.askopenfilename()

    if excel_path == "":

        return

    option = CalculationOptions()
    option.calculate_on_pf_diagram = calculate_on_pf_diagram
    option.loss_cost_is_zero = loss_cost_is_zero
    option.valve_is_dissipative = valve_is_dissipative
    option.condenser_is_dissipative = condenser_is_dissipative

    calculate_excel(excel_path, option)


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

    if dir_path == "":
        return

    file_path = os.path.join(dir_path, filename)
    file_position = os.path.join(costants.RES_DIR, "Other", filename)

    if not os.path.isfile(file_position):

        try:

            __retrieve_file(filename, file_position)

        except:

            warning_message = "\n\n<----------------- !WARNING! ------------------->\n"
            warning_message += "Unable to save the file to the desired location!\n\n"

            warning_message += "file name:\t" + filename + "\n"
            warning_message += "file position:\t" + file_position + "\n"
            warning_message += "new file position:\t" + file_path + "\n\n"

            warnings.warn(warning_message)

            __retrieve_file(filename, file_path)

        else:

            copyfile(file_position, file_path)


def __retrieve_file(filename, file_position):

    firebase = pyrebase.initialize_app(costants.FIREBASE_CONFIG)
    storage = firebase.storage()
    url = storage.child("3ETool_res/Other/" + filename).get_url(token=None)
    urllib.request.urlretrieve(url, file_position)
    ssl.create_default_context()