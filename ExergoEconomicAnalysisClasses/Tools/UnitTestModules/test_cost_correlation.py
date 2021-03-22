from ExergoEconomicAnalysisClasses.Tools.CostCorrelations.cost_correlation_gui import *
from ExergoEconomicAnalysisClasses.Tools.CostCorrelations.CorrelationClasses.turton_correlation import *
from PyQt5.QtWidgets import QApplication
import unittest, sys


def launch_app(widget):
    app = QApplication(sys.argv)
    pop_up = widget()
    pop_up.show()
    app.exec_()


class CostCorrelationTestCase(unittest.TestCase):

    def test_correlation_handler(self):
        correlation_handler = CostCorrelationHandler()
        self.assertEqual(1, len(correlation_handler.list_modules()))

    def test_correlation_files_manager(self):
        widget = CostCorrelationFilesManager
        launch_app(widget)
        self.assertTrue(True)

    def test_header_widget(self):

        app = QApplication(sys.argv)

        correlation = TurtonCorrelation()
        main_class = TurtonEditCorrelationWidget(correlation)

        widget = TurtonHeaderWidget(main_class)
        widget.set_edit_layout = True
        widget.init_layout()
        widget.show()

        app.exec_()

        self.assertTrue(True)

    def test_parameter_widget(self):
        app = QApplication(sys.argv)

        correlation = TurtonCorrelation()
        base_class = BaseEditCorrelationWidget(correlation)

        widget = ParametersWidget(correlation.parameter_dict, base_class)
        widget.set_edit_layout = True
        widget.init_layout()
        widget.show()

        app.exec_()

        self.assertTrue(True)

    def test_coefficient_widget(self):

        app = QApplication(sys.argv)

        correlation = TurtonCorrelation()
        base_class = BaseEditCorrelationWidget(correlation)
        coeff_dict = correlation.coefficient_dict

        widget = CoefficientWidget(coeff_dict, base_class)
        widget.show()

        app.exec_()

        self.assertTrue(True)

    def test_list_view(self):

        app = QApplication(sys.argv)
        widget = QListView()
        correlation = TurtonCorrelation()

        model = QStandardItem

        for key in correlation.parameter_dict.keys():

            widget.insertItem(key)

        widget.show()
        app.exec_()

if __name__ == '__main__':
    unittest.main()
