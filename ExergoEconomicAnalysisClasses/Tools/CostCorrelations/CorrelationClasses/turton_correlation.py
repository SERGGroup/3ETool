from ExergoEconomicAnalysisClasses.Tools.CostCorrelations.cost_correlation_classes import AbstractCostCorrelation
from ExergoEconomicAnalysisClasses.Tools.CostCorrelations.cost_correlation_classes import Parameter
from ExergoEconomicAnalysisClasses.Tools.CostCorrelations.cost_correlation_gui import BaseEditCorrelationWidget
from ExergoEconomicAnalysisClasses.Tools.CostCorrelations.cost_correlation_gui import CoefficientWidget
from ExergoEconomicAnalysisClasses.Tools.CostCorrelations.cost_correlation_gui import ParametersWidget
from PyQt5.QtGui import QFont, QDoubleValidator
import xml.etree.ElementTree as ETree
from PyQt5.QtWidgets import *
import math


class TurtonCorrelation(AbstractCostCorrelation):

    def __init__(self, correlation_data=None):

        super().__init__()

        self.name = ""
        self.note = ""
        self.material = "Carbon Steel"
        self.component_type = ""

        self.__A = Parameter("A")
        self.__P = Parameter("P")

        self.__K = list()
        self.__C = list()
        self.__B = list()

        self.__F_m = 0.
        self.__current_cepci = 0
        self.__correlation_cepci = None

        self.is_imported_from_file = False

        if correlation_data is not None:
            self.import_xml_tree(correlation_data)

    def get_cost(self):

        # This correlation format is extracted from: Turton, R, Bailie, R C, & Whiting, W B. "Analysis, synthesis and
        # design of chemical processes" Appendix A - pg.924.
        #
        # Once calculated, the cost value value is actualized using the CEPCI value relation

        CP_0 = self.__K[0]
        CP_0 += self.__K[1] * math.log10(self.__A.value)
        CP_0 += self.__K[2] * math.pow(math.log10(self.__A.value), 2)

        CP_0 = math.pow(10, CP_0)
        F_p = self.__get_F_p_coefficient()
        F_m = self.__F_m

        C_BM = CP_0 * (self.__B[0] + self.__B[1] * F_p * F_m)

        return C_BM * self.__current_cepci / self.__correlation_cepci

    def __get_F_p_coefficient(self):

        # If the material IS NOT carbon steel other parameters are required:
        #
        #   - C[0], C[1] and C[2] are interpolation parameters and could be retrieved in Turton book
        #   - __P.value is pressure value as defined in the correlation description
        #   - F_p is the pressure factor defined according to the equipment type

        F_p = self.__C[0]
        F_p += self.__C[1] * math.log10(self.__P.value)
        F_p += self.__C[2] * math.pow(math.log10(self.__P.value), 2)

        return math.pow(10, F_p)

    @property
    def parameter_dict(self):

        param_dict = {"A": self.__A,
                      "P": self.__P}

        return param_dict

    def set_parameters(self, input_dict: dict):

        if "A" in input_dict.keys():
            self.__A.value = input_dict["A"]

        if "P" in input_dict.keys():
            self.__P.value = input_dict["P"]

    @property
    def coefficient_dict(self):

        coefficients = {"corr_CEPCI": {"array size": 1, "is optional": False},
                        "F_m": {"array size": 1, "is optional": False},
                        "K": {"array size": 3, "is optional": False},
                        "C": {"array size": 3, "is optional": False},
                        "B": {"array size": 2, "is optional": True}}

        return coefficients

    @property
    def coefficients(self):

        return {"curr_CEPCI": [self.__correlation_cepci],
                "F_m": [self.__F_m],
                "K": self.__K,
                "C": self.__C,
                "B": self.__B}

    @coefficients.setter
    def coefficients(self, input_dict: dict):

        if "corr_CEPCI" in input_dict.keys():
            self.__correlation_cepci = input_dict["corr_CEPCI"][0]

        if "F_m" in input_dict.keys():
            self.__F_m = input_dict["F_m"][0]

        if "K" in input_dict.keys():
            self.__K = input_dict["K"]

        if "C" in input_dict.keys():
            self.__C = input_dict["C"]

        if "B" in input_dict.keys():
            self.__B = input_dict["B"]

    @property
    def description(self):
        return ""

    @property
    def edit_correlation_widget(self) -> QWidget:
        return TurtonEditCorrelationWidget(self)

    @property
    def parameter_settings_widget(self):
        return None

    def import_xml_tree(self, data: ETree.Element):

        header = data.find("header")

        self.name = header.get("name")
        self.component_type = header.get("component_type")
        self.note = header.get("note")

        parametersList = data.findall("parameter")

        for parameter in parametersList:

            __tmp_parameter = Parameter()
            __tmp_parameter.measure_unit = parameter.get("measure_unit")
            __tmp_parameter.range = parameter.get("range")
            __tmp_parameter.note = parameter.get("note")

            param_dict = {parameter.get("name"): __tmp_parameter}
            self.set_parameters(param_dict)

        coefficientsList = data.findall("coefficient")

        for coefficient in coefficientsList:

            __tmp_list = list()

            for element in coefficient.findall("element"):

                __tmp_list.append(float(element.get("value")))

            coeff_dict = {coefficient.get("name"): __tmp_list}
            self.coefficients = coeff_dict

    @property
    def export_xml_tree(self):

        # This class save the correlation data to a .dat file containing an encrypted xml tree. Encryption is useful in
        # order to prevent the user from modifying the file manually without going through the editor.
        #
        # The method generate the xml tree and pass it to the "export_to_file" method that is in charge of the actual
        # encryption and file saving processes.
        #
        # here is an example of turton correlation xml file:
        #
        #   <data>
        #
        #     <header
        #
        #         correlation_class = "Turton Correlation"
        #         name = "standard"
        #         component_type = "Heat Exchanger"
        #         note = "Plate Heat Exchanger"
        #
        #         ></header>
        #
        #     <parameters>
        #
        #          <parameter
        #
        #              name = "A"
        #              measure_unit = "m^2"
        #              range = "30-60"
        #              note = "Heat Exchanger Area"
        #
        #              ></parameter>
        #
        #          <parameter
        #
        #              name = "P"
        #              measure_unit = "kPa"
        #              range = "300-1000"
        #              note = "Mean Pressure"
        #
        #              ></parameter>
        #
        #     </parameters>
        #
        #     <coefficients>
        #
        #       <coefficient name = "corr_CEPCI">
        #
        #           <element value = 357>
        #
        #       </coefficient>
        #
        #       <coefficient name = "K">
        #
        #           <element value = 1.2039>
        #           <element value = 5.6434>
        #           <element value = 0.0353>
        #
        #       </coefficient>
        #
        #       <coefficient name = "C">
        #
        #           <element value = 3.4510">
        #           <element value = 0.7601">
        #           <element value = 0.0032">
        #
        #       </coefficient>
        #
        #       <coefficient name = "B">
        #
        #           <element value = 0.0012">
        #           <element value = 3.4550">
        #
        #       </coefficient>
        #
        #     </coefficients>
        #
        #   </data>

        data = ETree.Element("data")

        # <--------- HEADER DEFINITION --------->
        header = ETree.SubElement(data, "header")

        correlation_name = self.name
        correlation_note = self.note
        component_type = self.component_type

        header.set("correlation_class", "Turton Correlation")
        header.set("name", correlation_name)
        header.set("component_type", component_type)
        header.set("note", correlation_note)

        # <--------- PARAMETERS DEFINITION --------->
        parameters = ETree.SubElement(data, "parameters")

        for key in self.parameter_dict.keys():

            parameter = ETree.SubElement(parameters, "parameter")

            parameter.set("name", key)
            parameter.set("measure_unit", self.parameter_dict[key].measure_unit)
            parameter.set("range", str(self.parameter_dict[key].range))
            parameter.set("note", str(self.parameter_dict[key].note))

        # <--------- COEFFICIENTS DEFINITION --------->
        coefficients = ETree.SubElement(data, "coefficients")

        for key in self.coefficients.keys():

            coefficient = ETree.SubElement(coefficients, "coefficient")
            coefficient.set("name", key)

            for element_value in self.coefficients[key]:
                element = ETree.SubElement(coefficient, "element")
                element.set("value", str(element_value))

        return data


class TurtonEditCorrelationWidget(BaseEditCorrelationWidget):

    def __init__(self, cost_correlation_class: AbstractCostCorrelation):

        super().__init__(cost_correlation_class)
        self.title = "Turton Cost Correlation"

        self.header_widget = None
        self.parameter_widget_dict = dict()

        self.__set_header_layout()
        self.__set_parameter_layout()

    def __update(self):

        coeff_dict = dict()

        for key in self.coefficient_widget_dict.keys():

            coeff_dict.update(self.coefficient_widget_dict[key].coefficient_dict)

        self.cost_correlation.coefficients = coeff_dict

    def __reset_dialog(self):
        self.header_widget.component_type_combo.setEnabled(True)

    @property
    def is_ready_for_saving(self):

        for sel_dict in [self.parameter_widget_dict]:

            for key in sel_dict.keys():

                if not sel_dict[key].is_ready_for_saving:

                    return False

        return self.header_widget.is_ready_for_saving

    def __set_header_layout(self):

        widget = TurtonHeaderWidget(self)
        widget.set_edit_layout = True
        widget.init_layout()

        self.header_widget = widget

    def __set_parameter_layout(self):

        parameter_dict = self.cost_correlation.parameter_dict
        parameter_layout = QHBoxLayout()

        for key in parameter_dict.keys():

            widget = ParametersWidget(parameter_dict[key], self)
            widget.set_edit_layout = True
            widget.init_layout()

            self.parameter_widget_dict.update({key: widget})
            parameter_layout.addWidget(widget)

        parameter_widget = QWidget()
        parameter_widget.setLayout(parameter_layout)

        self.parameter_widget = parameter_widget


class TurtonHeaderWidget(QWidget):

    def __init__(self, parent_class: TurtonEditCorrelationWidget):

        super().__init__(None)

        self.correlation = parent_class.cost_correlation
        self.set_edit_layout = False

        self.parent_class = parent_class

        self.main_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()

    def init_layout(self):

        if self.set_edit_layout:
            self.__init_edit_objects()
            self.__init_edit_layout()

        else:
            self.__init_set_objects()
            self.__init_set_layout()

        self.setLayout(self.main_layout)

    def __init_edit_objects(self):

        self.name_edit = QLineEdit()
        self.note_edit = QTextEdit()
        self.component_type_combo = QComboBox()

        self.name_edit.setText(self.correlation.name)
        self.note_edit.setText(self.correlation.note)

        from ExergoEconomicAnalysisClasses.Tools.modules_handler import ModulesHandler
        modules_handler = ModulesHandler()

        self.component_type_combo.addItems(modules_handler.name_list)
        self.component_type_combo.setEnabled(False)

        if not self.correlation.component_type == "":

            component_type = self.correlation.component_type
            self.component_type_combo.setCurrentIndex(modules_handler.get_name_index(component_type))

        else:

            self.component_type_combo.setCurrentIndex(0)

        self.name_edit.setObjectName("name_edit")
        self.note_edit.setObjectName("note_edit")
        self.component_type_combo.setObjectName("component_type_combo")

        self.name_edit.textChanged.connect(self.on_text_edit_change)
        self.note_edit.textChanged.connect(self.on_text_edit_change)
        self.component_type_combo.currentTextChanged.connect(self.on_text_edit_change)

    def __init_set_objects(self):

        self.curr_cepci_edit = QLineEdit()
        self.name_edit = QLabel()
        self.note_edit = QLabel()
        self.component_type_combo = QLabel()

        self.note_edit.setWordWrap(True)
        self.curr_cepci_edit.setValidator(QDoubleValidator())
        self.curr_cepci_edit.setObjectName("curr_cepci_edit")
        self.curr_cepci_edit.textChanged.connect(self.on_text_edit_change)

        self.note_edit.setText(self.correlation.name)
        self.note_edit.setText(self.correlation.note)
        self.note_edit.setText(self.correlation.component_type)

    def __init_edit_layout(self):

        # <----------- FIRST ROW ----------->

        name_label = QLabel()
        name_label.setText("Correlation Name:")

        self.grid_layout.addWidget(name_label, 0, 0)
        self.grid_layout.addWidget(self.name_edit, 0, 1)

        # <---------- SECOND ROW ----------->

        component_type_label = QLabel()
        component_type_label.setText("Component Type:")

        self.grid_layout.addWidget(component_type_label, 1, 0)
        self.grid_layout.addWidget(self.component_type_combo, 1, 1)

        # <----------- FINAL ROW ----------->

        grid_layout_widget = QWidget()
        grid_layout_widget.setLayout(self.grid_layout)

        self.main_layout.addWidget(grid_layout_widget)
        self.main_layout.addWidget(self.note_edit)

    def __init_set_layout(self):

        # <----------- FIRST ROW ----------->

        name_label = QLabel()
        name_label.setText("Correlation Name:")

        self.grid_layout.addWidget(name_label, 0, 0)
        self.grid_layout.addWidget(self.name_edit, 0, 1)

        # <---------- SECOND ROW ----------->

        component_type_label = QLabel()
        component_type_label.setText("Component Type:")

        self.grid_layout.addWidget(component_type_label, 1, 0)
        self.grid_layout.addWidget(self.component_type_combo, 1, 1)

        # <---------- THIRD ROW ----------->

        curr_cepci_label = QLabel()
        curr_cepci_label.setText("Current CEPCI:")

        self.grid_layout.addWidget(curr_cepci_label, 2, 0)
        self.grid_layout.addWidget(self.curr_cepci_edit, 2, 1)

        # <----------- FINAL ROW ----------->

        grid_layout_widget = QWidget()
        grid_layout_widget.setLayout(self.grid_layout)

        self.main_layout.addWidget(grid_layout_widget)
        self.main_layout.addWidget(self.note_edit)

    def on_text_edit_change(self):

        name = self.sender().objectName()

        if name == "curr_cepci_edit":

            self.correlation.currentCEPCI = float(self.curr_cepci_edit.text())

        elif name == "name_edit":

            self.correlation.name = self.note_edit.text()

        elif name == "note_edit":

            self.correlation.note = self.note_edit.toPlainText()

        elif name == "component_type_combo":

            self.correlation.component_type = self.component_type_combo.currentText()

        self.parent_class.enable_buttons()

    @property
    def is_ready_for_saving(self):

        for edit_text in [self.name_edit, self.note_edit]:

            if edit_text.text() == "":
                return False

        return True