from EEETools.Tools.API.DatAPI.modules_importer import import_dat
from EEETools.Tools.API.ExcelAPI.modules_importer import *
from EEETools import costants
from tkinter import filedialog
import tkinter as tk
import unittest


def import_matlab_result(excel_path):

    try:

        result_data = pandas.read_excel(excel_path, sheet_name="Eff Out").values
        return result_data[1, 6]

    except:

        return -100


class ImportTestCase(unittest.TestCase):

    def test_excel_import(self):

        array_handler_list = list()
        resource_excel_path = os.path.join(costants.TEST_RES_DIR, "ImportTestResources", "ExcelTestFiles")

        i = 1
        excel_path = os.path.join(resource_excel_path, "Sample Excel Input " + str(i) + ".xlsm")

        while os.path.isfile(excel_path):

            array_handler = import_excel_input(excel_path)
            result = import_matlab_result(excel_path)

            if result != -100:

                array_handler.options.calculate_on_pf_diagram = False
                array_handler.calculate()

                print(array_handler)

                array_handler_list.append(array_handler)
                useful_effect = array_handler.useful_effect_connections[0]

                self.assertEqual(round(result, 6), round(useful_effect.rel_cost, 6))

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
            result_excel = array_handler.useful_effect_connections

            dat_path = os.path.join(resource_dat_path, "Sample Dat " + str(i) + ".dat")
            export_dat(dat_path, array_handler)
            array_handler_dat = import_dat(dat_path)
            array_handler_dat.options.calculate_on_pf_diagram = False
            array_handler_list.append(array_handler_dat)

            array_handler_dat.calculate()
            result_dat = array_handler_dat.useful_effect_connections

            difference = 0
            sum_exergy = 0

            for result in result_dat:

                difference += result.rel_cost*result.exergy_value
                sum_exergy += result.rel_cost*result.exergy_value

            for result in result_excel:

                difference -= result.rel_cost * result.exergy_value
                sum_exergy += result.rel_cost * result.exergy_value

            err = 2*difference/sum_exergy

            self.assertEqual(round(err, 7), 0)

            i += 1
            excel_path = os.path.join(resource_excel_path, "Sample Excel Input " + str(i) + ".xlsm")

    def test_download_link(self):

        from EEETools.Tools.Other.fernet_handler import FernetHandler
        FernetHandler()

        self.assertTrue(True)

    def test_excel_calculate(self):

        import EEETools
        EEETools.calculate(

            calculate_on_pf_diagram=True,
            condenser_is_dissipative=True,
            loss_cost_is_zero=True,

        )
        self.assertTrue(True)

    def test_excel_debug(self):

        import EEETools
        EEETools.export_debug_information(calculate_on_pf_diagram=True)
        self.assertTrue(True)

    def test_excel_update(self):

        resource_excel_path = os.path.join(costants.TEST_RES_DIR, "ImportTestResources", "ExcelTestFiles")
        excel_path = os.path.join(resource_excel_path, "BHE_simple_analysis.xlsx")
        updated_exergy_values = [

            {"index": 1,  "value": 82.86},
            {"index": 2,  "value": 87.76},
            {"index": 3,  "value": 91.91},
            {"index": 4,  "value": 86.54},
            {"index": 20, "value": 0.5 * 9.81},
            {"index": 21, "value": (343.63 - 343.63) * (1 - 292.15 / 325.15)},
            {"index": 22, "value": 3.68}

        ]

        connection = updated_exergy_values[0]
        array_handler = calculate_excel(excel_path, new_exergy_list=updated_exergy_values, export_solution=False)
        self.assertEqual(connection["value"], array_handler.find_connection_by_index(connection["index"]).exergy_value)

    def test_sankey(self):

        import EEETools
        EEETools.plot_sankey(generate_on_pf_diagram=True, display_costs=True)
        self.assertTrue(True)

    def test_connection_check(self):

        import EEETools
        EEETools.launch_connection_debug()
        self.assertTrue(True)


if __name__ == '__main__':

    unittest.main()
