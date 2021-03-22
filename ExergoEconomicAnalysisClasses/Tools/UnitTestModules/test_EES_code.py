import unittest, traceback, os
from ExergoEconomicAnalysisClasses import costants
from ExergoEconomicAnalysisClasses.Tools.EESCodeGenerator.EES_parser import EESCodeAnalyzer


class EESCodeTestCase(unittest.TestCase):

    def test_parser(self):

        self.results = list()
        self.code_analyzer = EESCodeAnalyzer()
        self.error_found = False

        resource_file_path = os.path.join(costants.TEST_RES_DIR, "TXTFiles", "EESTestScripts")

        self.__test_file(resource_file_path)

        variable_list = list()
        for result in self.results:

            if not result is None:
                result.append_variable_to_list(variable_list)
                print(result.rich_text)

        self.assertFalse(self.error_found)
        self.assertEqual(13, len(variable_list))

    def test_splitter(self):

        self.code_analyzer = EESCodeAnalyzer()
        self.results = list()
        self.error_found = False

        resource_file_path = os.path.join(costants.TEST_RES_DIR, "TXTFiles", "EESSplitterTestScript")

        self.__test_file(resource_file_path, test_split=True)
        self.assertFalse(self.error_found)
        self.assertEqual(3, len(self.results))

    def __test_file(self, file_path, test_split=False):

        resource_file = open(file_path)

        if test_split:

            text = resource_file.read()

            try:

                self.results.extend(self.code_analyzer.get_code_parts(text, print_token=True))

            except:

                traceback.print_exc()
                self.error_found = True

        else:

            lines = resource_file.readlines()

            for line in lines:

                line = line.strip('\n')

                try:

                    self.results.append(self.code_analyzer.parse_string(line, print_token=True))

                except:

                    traceback.print_exc()
                    self.error_found = True

                line = resource_file.readline()


if __name__ == '__main__':
    unittest.main()
