from EEETools.Tools.API.ExcelAPI.modules_importer import calculate_excel, import_excel_input, export_debug_info_to_excel
from EEETools.Tools.GUIElements.connection_and_block_check import CheckConnectionWidget
from EEETools.Tools.GUIElements.net_plot_modules import display_network
from EEETools.MainModules.main_module import CalculationOptions
from EEETools.Tools.API.Tools.file_handler import get_file_position
from tkinter import filedialog
from shutil import copyfile
import tkinter as tk
import os, warnings


def calculate(

        excel_path="", calculate_on_pf_diagram=True,
        loss_cost_is_zero=True, valve_is_dissipative=True,
        condenser_is_dissipative=True

):

    excel_path = __find_excel_path(excel_path)
    if excel_path == "":
        return

    option = CalculationOptions()
    option.calculate_on_pf_diagram = calculate_on_pf_diagram
    option.loss_cost_is_zero = loss_cost_is_zero
    option.valve_is_dissipative = valve_is_dissipative
    option.condenser_is_dissipative = condenser_is_dissipative

    with warnings.catch_warnings():

        warnings.simplefilter("ignore")
        calculate_excel(excel_path, option)

def export_debug_information(

        excel_path="", calculate_on_pf_diagram=True,
        loss_cost_is_zero=True, valve_is_dissipative=True,
        condenser_is_dissipative=True

):

    excel_path = __find_excel_path(excel_path)
    if excel_path == "":
        return

    option = CalculationOptions()
    option.calculate_on_pf_diagram = calculate_on_pf_diagram
    option.loss_cost_is_zero = loss_cost_is_zero
    option.valve_is_dissipative = valve_is_dissipative
    option.condenser_is_dissipative = condenser_is_dissipative

    with warnings.catch_warnings():

        warnings.simplefilter("ignore")
        array_handler = calculate_excel(excel_path, option, export_solution=False)
        export_debug_info_to_excel(excel_path, array_handler)

def launch_connection_debug(excel_path=""):

    excel_path = __find_excel_path(excel_path)
    if excel_path == "":
        return

    array_handler = import_excel_input(excel_path)
    CheckConnectionWidget.launch(array_handler)


def launch_network_display(excel_path=""):

    excel_path = __find_excel_path(excel_path)
    if excel_path == "":
        return

    array_handler = import_excel_input(excel_path)
    display_network(array_handler)


def plot_sankey(

        excel_path="", show_component_mixers=False,
        generate_on_pf_diagram=True, display_costs=False,
        font_size=15, min_opacity_perc=0.15

):

    from EEETools.Tools.API.Tools.sankey_diagram_generation import SankeyDiagramGenerator, SankeyDiagramOptions
    excel_path = __find_excel_path(excel_path)
    if excel_path == "":
        return

    array_handler = import_excel_input(excel_path)

    options = SankeyDiagramOptions()
    options.generate_on_pf_diagram = generate_on_pf_diagram
    options.show_component_mixers = show_component_mixers
    options.display_costs = display_costs
    options.font_size = font_size
    options.min_opacity_perc = min_opacity_perc

    SankeyDiagramGenerator(array_handler, options).show()


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
    file_position = get_file_position(filename)

    if file_position == "":

        warning_message = "\n\n<----------------- !WARNING! ------------------->\n"
        warning_message += "Unable to save the file to the desired location!\n\n"

        warning_message += "file name:\t\t\t" + filename + "\n"
        warning_message += "file position:\t\t" + file_position + "\n"
        warning_message += "new file position:\t" + file_path + "\n\n"

        warnings.warn(warning_message)

    else:

        try:

            copyfile(file_position, file_path)

        except:

            warning_message = "\n\n<----------------- !WARNING! ------------------->\n"
            warning_message += "Unable to copy the file to the desired location!\n\n"

        else:

            warning_message = "\n\n<----------------- !SUCCESS! ------------------->\n"
            warning_message += "File successfully copied to the desired location!\n\n"

        warning_message += "file name:\t\t\t" + filename + "\n"
        warning_message += "file position:\t" + file_path + "\n\n"

        warnings.warn(warning_message)


def __find_excel_path(excel_path):

    if excel_path == "":

        root = tk.Tk()
        root.withdraw()
        excel_path = filedialog.askopenfilename()

    return excel_path