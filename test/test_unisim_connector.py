from EEETools.Tools.Other.unisim_connect import UNISIMConnector
from tkinter import filedialog
import tkinter as tk
import unittest


class MyTestCase(unittest.TestCase):

    def test_open_file(self):

        root = tk.Tk()
        root.withdraw()
        unisim_path = filedialog.askopenfilename()

        with UNISIMConnector(unisim_path) as unisim:

            a = unisim.get_block("COND")
            b = unisim.get_stream("4")
            print(a)