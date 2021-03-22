import os
import unittest
from EEETools.Tools.modules_handler import ModulesHandler

class ModulesHandlerTestCase(unittest.TestCase):

    def testInitializeList(self):

        modules_handler = ModulesHandler()
        print(modules_handler.name_list)

        #If there were no errors the test succedeed
        self.assertTrue(True)

    def testConvertName(self):

        modules_handler = ModulesHandler()

        for filename in os.listdir(modules_handler.data_folder):

            index = modules_handler.get_name_index(filename)

            self.assertNotEqual(-1, index)

            std_name = modules_handler.name_list[index]
            module_name = modules_handler.get_module_name(std_name)

            self.assertEqual(filename, module_name)


if __name__ == '__main__':
    unittest.main()
