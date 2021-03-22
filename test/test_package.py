import unittest
import tkinter as tk
from tkinter import filedialog
from EEETools.Tools import modules_importer


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
        modules_importer.calculate_dat(excel_path)

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
