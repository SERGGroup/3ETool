from ExergoEconomicAnalysisClasses.MainModules import Block
from ExergoEconomicAnalysisClasses.MainModules.support_blocks import Drawer
import xml.etree.ElementTree as ETree


class Alternator(Block):

    def __init__(self, inputID, main_class):

        super().__init__(inputID, main_class)

        self.type = "alternator"
        self.has_support_block = True
        self.support_block.append(Drawer(main_class, self))

        self.efficiency = 1.

    def add_connection_to_support_block(self, new_connection, is_input):
        self.support_block[0].add_connection(new_connection, is_input, )

    def is_ready_for_calculation(self):
        return len(self.support_block[0].input_connections) >= 1

    def prepare_for_calculation(self):

        self.support_block[0].prepare_for_calculation()

        new_conn = self.main_class.append_connection(from_block=self)
        new_conn.name = "electrical power output"
        new_conn.is_useful_effect = True
        new_conn.automatically_generated_connection = True
        new_conn.exergy_value = self.exergy_balance

    def append_excel_connection_list(self, input_list):

        self.efficiency = float(input_list[0])

        for elem in input_list[1:]:

            new_conn = self.main_class.find_connection_by_index(abs(elem))

            if not new_conn is None:

                is_input = (elem > 0)
                new_conn.is_fluid_stream = False

                if is_input:

                    self.add_connection(new_conn, is_input, append_to_support_block=0)

                else:

                    self.add_connection(new_conn, is_input)

    def export_xml_other_parameters(self) -> ETree.Element:

        other_tree = ETree.Element("Other")
        other_tree.set("efficiency", str(self.efficiency))
        return other_tree

    def append_xml_other_parameters(self, input_list: ETree.Element):

        self.efficiency = float(input_list.get("efficiency"))

    def export_xml_connection_list(self) -> ETree.Element:

        xml_connection_list = ETree.Element("Connections")

        mechanical_connections = ETree.SubElement(xml_connection_list, "MechanicalConnections")

        for input_connection in self.support_block[0].external_input_connections:

            if not input_connection.automatically_generated_connection:

                input_xml = ETree.SubElement(mechanical_connections, "input")
                input_xml.set("index", str(input_connection.index))

        for output_connection in self.support_block[0].external_output_connections:

            if not output_connection.automatically_generated_connection:

                output_xml = ETree.SubElement(mechanical_connections, "output")
                output_xml.set("index", str(output_connection.index))

        electrical_connections = ETree.SubElement(xml_connection_list, "ElectricalConnections")

        for input_connection in self.external_input_connections:

            if not input_connection.automatically_generated_connection:

                input_xml = ETree.SubElement(electrical_connections, "input")
                input_xml.set("index", str(input_connection.index))

        for output_connection in self.external_output_connections:

            if not output_connection.automatically_generated_connection:

                output_xml = ETree.SubElement(electrical_connections, "output")
                output_xml.set("index", str(output_connection.index))

        a = ETree.tostring(xml_connection_list)
        return xml_connection_list

    def append_xml_connection_list(self, input_list: ETree.Element):

        a = ETree.tostring(input_list)

        mechanical_connections = input_list.find("MechanicalConnections")
        electrical_connections = input_list.find("ElectricalConnections")

        self.__add_connection_by_index(mechanical_connections, "input", append_to_support_block=0)
        self.__add_connection_by_index(mechanical_connections, "output", append_to_support_block=0)

        self.__add_connection_by_index(electrical_connections, "input")
        self.__add_connection_by_index(electrical_connections, "output")

    def __add_connection_by_index(self, input_list: ETree.Element, connection_name, append_to_support_block = None):

        if connection_name == "input":

            is_input = True

        else:

            is_input = False

        for connection in input_list.findall(connection_name):

            new_conn = self.main_class.find_connection_by_index(float(connection.get("index")))

            if new_conn is not None:

                self.add_connection(new_conn, is_input, append_to_support_block=append_to_support_block)

    @classmethod
    def return_EES_needed_index(cls):

        # Alternator has multiple input and outputs for exergy flux:

        return_dict = {"global output": [0, False],
                       "mechanical input": [1, True],
                       "mechanical output": [2, True],
                       "electrical input": [3, True],
                       "electrical output": [4, True]}

        return return_dict

    @classmethod
    def return_EES_base_equations(cls):

        # WARNING: This methods must be overloaded in subclasses!!
        # This methods returns a dictionary that contain a list of streams that have to be present in the EES text
        # definition.

        return dict()

    @property
    def exergy_balance(self):

        exergy_balance = 0

        for conn in self.input_connections:

            if conn == self.support_block[0].connection_with_main:
                exergy_balance += conn.exergy_value * self.efficiency

            else:
                exergy_balance += conn.exergy_value

        for conn in self.output_connections:
            exergy_balance -= conn.exergy_value

        return exergy_balance

    @property
    def can_be_removed_in_pf_definition(self):
        return False

    def return_other_zone_connections(self, zone_type, input_connection):

        # Alternator is connected only to energy streams, hence it is not interested in the zones generation process
        return list()