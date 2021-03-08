from ExergoEconomicAnalysisClasses.Tools.Other.fernet_handler import FernetHandler
from ExergoEconomicAnalysisClasses.Tools.Other.handler import Handler
from PyQt5.QtWidgets import QWidget
from res import costants
from abc import ABC
import abc, os


class AbstractCostCorrelation(ABC):

    def __init__(self):
        self.name = ""
        self.note = ""
        self.component_type = ""

        self.fernet_handler = FernetHandler()

    def import_from_file(self, file_path):
        """DON'T OVERRIDE THIS METHOD"""
        data = self.fernet_handler.read_file(file_path)
        self.import_xml_tree(data)

    def export_to_file(self, file_path = ""):
        """DON'T OVERRIDE THIS METHOD"""

        if file_path == "":

            correlation_handler = CostCorrelationHandler()
            file_path = correlation_handler.get_file_path(self)

        data = self.export_xml_tree()
        self.fernet_handler.save_file(file_path, data)

    @abc.abstractmethod
    def import_xml_tree(self, data):
        raise NotImplementedError()

    @abc.abstractmethod
    def export_xml_tree(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_cost(self):
        raise NotImplementedError()

    @property
    def currentCEPCI(self):
        return self.__current_cepci

    @currentCEPCI.setter
    def currentCEPCI(self, input_cepci):
        self.__current_cepci = input_cepci

    @property
    @abc.abstractmethod
    def parameter_dict(self) -> dict:
        raise NotImplementedError()

    @abc.abstractmethod
    def set_parameters(self, input_dict):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def coefficient_dict(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def coefficients(self):
        raise NotImplementedError()

    @coefficients.setter
    @abc.abstractmethod
    def coefficients(self, input_dict: dict):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def description(self):
        pass

    @property
    @abc.abstractmethod
    def edit_correlation_widget(self) -> QWidget:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def parameter_settings_widget(self):
        raise NotImplementedError()


class CostCorrelationHandler(Handler):

    def __init__(self):

        super().__init__()

        self.data_folder = os.path.join(costants.ROOT_DIR, "res", "Cost Correlation Data")
        self.subclass_directory_path = "ExergoEconomicAnalysisClasses.Tools.CostCorrelations.CorrelationClasses"

        from ExergoEconomicAnalysisClasses.Tools.modules_handler import ModulesHandler
        modules_handler = ModulesHandler()
        self.name_list = modules_handler.name_list

    def check_data_folder(self):

        if not os.path.isdir(self.data_folder):

            try:

                os.mkdir(self.data_folder)

            except:

                pass

        for name in self.name_list:

            folder_name = self.get_module_name(name)
            name_folder_path = os.path.join(self.data_folder, folder_name)

            if not os.path.isdir(name_folder_path):

                try:

                    os.mkdir(name_folder_path)

                except:

                    pass

    def open_file(self, file_path):

        fernet_handler = FernetHandler()
        data = fernet_handler.read_file(file_path)

        __header = data.find("header")
        __correlation_name = __header.get("correlation_class")
        __subclass = self.import_correct_sub_class(__correlation_name)

        return __subclass(data)

    def save_file(self, correlation_class, file_path = ""):

        if file_path == "":

            file_path = self.get_file_path(correlation_class)

        correlation_class.export_to_file(file_path)

    def get_file_path(self, correlation_class):

        file_folder = os.path.join(self.data_folder, self.get_module_name(correlation_class.component_type))

        if os.path.isdir(file_folder):

            return os.path.join(file_folder, self.get_module_name(correlation_class.name) + ".dat")

        else:

            raise FileNotFoundError

    @staticmethod
    def rename_file(new_name, file_path):

        fernet_handler = FernetHandler()
        data = fernet_handler.read_file(file_path)

        header = data.find("header")
        header.attrib["name"] = new_name

        fernet_handler.save_file(file_path, data)


# <----------------------------------------->
# <------------ SUPPORT CLASSES ------------>
# <----------------------------------------->

class Parameter:

    def __init__(self, input_name):

        self.name = input_name
        self.note = ""
        self.measure_unit = ""

        self.value = 0.
        self.__range = Range()

    @property
    def range(self):
        return self.__range

    @range.setter
    def range(self, input_range):
        self.__range.initialize(input_range)


class Range:

    def __init__(self):

        self.low = 0.
        self.high = 0.

    def __str__(self):

        if self.low == self.high:

            if self.low == 0:

                return ""

            else:

                return str(self.low)

        else:

            return str(self.low) + " - " + str(self.high)

    def initialize(self, input_range):

        if type(input_range) is str:

            input_range = input_range.strip()

            if input_range == "":

                self.low = 0.
                self.high = 0.

            elif "-" not in input_range:

                self.low = float(input_range)
                self.high = float(input_range)

            else:

                elements = input_range.split("-")
                self.low = float(elements[0])
                self.high = float(elements[1])

        elif type(input_range) is list:

            self.low = input_range[0]
            self.high = input_range[1]

        elif type(input_range) is Range:

            self.low = input_range.low
            self.high = input_range.high
