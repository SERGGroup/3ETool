from EEETools.Tools.EESCodeGenerator.EES_creator_tool import DefineEESTextWidget
from EEETools.Tools.EESCodeGenerator.EES_creator_tool import EESTextFilesManager
from EEETools.Tools.EESCodeGenerator.EES_checker import Zones
from EEETools.Tools.modules_importer import import_excel_input
from PyQt5.QtWidgets import QApplication
import sys, os, traceback, unittest
from EEETools import costants


def launch_app(widget):
    app = QApplication(sys.argv)
    pop_up = widget()
    pop_up.show()
    app.exec_()


class InputEESTestCase(unittest.TestCase):

    def testRunMain(self):
        widget = DefineEESTextWidget
        launch_app(widget)
        self.assertTrue(True)

    def testRunManager(self):
        widget = EESTextFilesManager
        launch_app(widget)
        self.assertTrue(True)

    def testZoneCreator(self):

        zones_list = list()
        error_found = False
        resource_excel_path = os.path.join(costants.TEST_RES_DIR, "ImportTestResources", "ExcelTestFiles")

        i = 1
        excel_path = os.path.join(resource_excel_path, "Sample Excel Input " + str(i) + ".xlsm")
        while os.path.isfile(excel_path):

            try:
                array_handler = import_excel_input(excel_path)
                zones_list.append(Zones(array_handler))

            except:
                traceback.print_exc()
                error_found = True

            i += 1
            excel_path = os.path.join(resource_excel_path, "Sample Excel Input " + str(i) + ".xlsm")

        self.assertFalse(error_found)


if __name__ == '__main__':
    unittest.main()
