from ExergoEconomicAnalysisClasses.Tools.modules_importer import *
from tkinter import filedialog
import unittest, pandas, os
from res import costants
import tkinter as tk


def import_matlab_result(excel_path):
    result_data = pandas.read_excel(excel_path, sheet_name="Eff Out").values
    return result_data[1, 6]


class ImportTestCase(unittest.TestCase):

    def test_excel_import(self):

        array_handler_list = list()
        resource_excel_path = os.path.join(costants.TEST_RES_DIR, "ImportTestResources", "ExcelTestFiles")

        i = 1
        excel_path = os.path.join(resource_excel_path, "Sample Excel Input " + str(i) + ".xlsm")

        while os.path.isfile(excel_path):

            array_handler = import_excel_input(excel_path)
            result = import_matlab_result(excel_path)
            array_handler.options.calculate_on_pf_diagram = False
            array_handler.calculate()

            print(array_handler)

            array_handler_list.append(array_handler)
            useful_effect = array_handler.useful_effect_connections[0]

            self.assertEqual(round(result, 6), round(useful_effect.relCost, 6))

            i += 1
            excel_path = os.path.join(resource_excel_path, "Sample Excel Input " + str(i) + ".xlsm")

    def test_excel_direct_calculation(self):

        root = tk.Tk()
        root.withdraw()
        excel_path = filedialog.askopenfilename()
        calculate_excel(excel_path)

        self.assertTrue(True)

    def test_dat_import_export(self):

        array_handler_list = list()
        resource_excel_path = os.path.join(costants.TEST_RES_DIR, "ImportTestResources", "ExcelTestFiles")
        resource_dat_path = os.path.join(costants.TEST_RES_DIR, "ImportTestResources", "DatTestFiles")

        i = 1
        excel_path = os.path.join(resource_excel_path, "Sample Excel Input " + str(i) + ".xlsm")

        while os.path.isfile(excel_path):

            array_handler = import_excel_input(excel_path)
            array_handler.calculate()
            result_excel = array_handler.useful_effect_connections[0]

            dat_path = os.path.join(resource_dat_path, "Sample Dat " + str(i) + ".dat")
            export_dat(dat_path, array_handler)
            array_handler_dat = import_dat(dat_path)
            array_handler_list.append(array_handler_dat)

            array_handler_dat.calculate()
            result_dat = array_handler_dat.useful_effect_connections[0]

            self.assertEqual(round(result_excel.relCost, 6), round(result_dat.relCost, 6))

            i += 1
            excel_path = os.path.join(resource_excel_path, "Sample Excel Input " + str(i) + ".xlsm")


if __name__ == '__main__':
    unittest.main()
