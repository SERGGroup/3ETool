from EEETools.Tools.GUIElements.connection_and_block_check import CheckConnectionWidget
from EEETools.Tools.GUIElements.net_plot_modules import display_network
from EEETools.Tools.API.ExcelAPI.modules_importer import import_excel_input
from tkinter import filedialog
import tkinter as tk
import unittest


class MyTestCase(unittest.TestCase):

    def test_block_connection(self):

        root = tk.Tk()
        root.withdraw()
        excel_path = filedialog.askopenfilename()

        array_handler = import_excel_input(excel_path)
        CheckConnectionWidget.launch(array_handler)

        self.assertEqual(True, True)

    def test_network(self):

        root = tk.Tk()
        root.withdraw()
        excel_path = filedialog.askopenfilename()

        array_handler = import_excel_input(excel_path)
        display_network(array_handler)

        self.assertEqual(True, True)

    def test_network_product_fuel(self):

        root = tk.Tk()
        root.withdraw()
        excel_path = filedialog.askopenfilename()

        array_handler = import_excel_input(excel_path)

        try:

            array_handler.calculate()

        except:

            pass

        display_network(array_handler.pf_diagram)

        self.assertEqual(True, True)


if __name__ == '__main__':

    unittest.main()
