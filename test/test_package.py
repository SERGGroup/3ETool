import unittest
import tkinter as tk
from tkinter import filedialog

import EEETools.Tools.API.DatAPI.modules_importer
from EEETools.Tools.API.ExcelAPI import modules_importer
from EEETools.Tools.API.terminal_api import paste_default_excel_file


class MyTestCase(unittest.TestCase):

    def test_excel_direct_calculation(self):

        root = tk.Tk()
        root.withdraw()
        excel_path = filedialog.askopenfilename()
        modules_importer.calculate_excel(excel_path)

        self.assertTrue(True)

    def test_dat_direct_calculation(self):

        root = tk.Tk()
        root.withdraw()
        excel_path = filedialog.askopenfilename()
        EEETools.Tools.API.DatAPI.modules_importer.calculate_dat(excel_path)

        self.assertTrue(True)

    def test_main_modules(self):

        paste_default_excel_file()

        self.assertTrue(True)

    def test_main_modules_calculation(self):

        import EEETools
        EEETools.calculate()

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
