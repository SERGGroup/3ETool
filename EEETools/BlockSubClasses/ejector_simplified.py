from EEETools.MainModules.support_blocks import Drawer, get_drawer_sub_class
from EEETools.MainModules import Block
import xml.etree.ElementTree as ETree
from EEETools import costants


class EjectorSimplified(Block):

    def __init__(self, inputID, main_class):

        super().__init__(inputID, main_class)

        self.type = "Ejector Simplified"
        self.has_support_block = True

        self.mass_ratio = 0.

        SupportMixer = get_drawer_sub_class("mixer", main_class)

        self.support_block.append(Drawer(main_class, self))
        self.support_block.append(Drawer(main_class, self, is_input=False))
        self.support_block.append(SupportMixer(main_class, self))

    def add_connection_to_support_block(self, support_block, new_connection, is_input):

        if support_block == "expander":

            self.support_block[0].add_connection(new_connection, is_input)

        elif support_block == "compressor":

            self.support_block[0].add_connection(new_connection, is_input)

        elif support_block == "mixer":

            self.support_block[0].add_connection(new_connection, is_input)

    def is_ready_for_calculation(self):
        return len(self.output_connections) >= 1 and len(self.support_block[0].output_connections) >= 1 and len(
            self.support_block[0].input_connections) >= 1

    def initialize_connection_list(self, input_list):

        self.mass_ratio = float(input_list[0])

        conn_output = self.main_class.find_connection_by_index(abs(input_list[1]))
        conn_input_driving = self.main_class.find_connection_by_index(abs(input_list[2]))
        conn_input_driven = self.main_class.find_connection_by_index(abs(input_list[3]))

        self.add_connection(conn_output, is_input=False, append_to_support_block=2)
        self.support_block[0].add_connection(conn_input_driving, is_input=True, append_to_support_block=0)
        self.support_block[1].add_connection(conn_input_driven, is_input=False, append_to_support_block=0)

        new_conn = self.main_class.append_connection(from_block=self)

    def prepare_for_calculation(self):

        self.support_block[0].prepare_for_calculation()

        new_conn = self.main_class.append_connection(from_block=self)
        new_conn.name = "Electrical Power Output"
        new_conn.is_useful_effect = True
        new_conn.automatically_generated_connection = True
        new_conn.exergy_value = self.exergy_balance

    def export_xml_connection_list(self) -> ETree.Element:

        xml_connection_list = ETree.Element("Connections")

        fluid_connections = ETree.SubElement(xml_connection_list, "FluidConnections")

        for input_connection in self.support_block[0].external_input_connections:

            input_xml = ETree.SubElement(fluid_connections, "input")
            input_xml.set("index", str(input_connection.index))

        for output_connection in self.support_block[0].external_output_connections:

            output_xml = ETree.SubElement(fluid_connections, "output")
            output_xml.set("index", str(output_connection.index))

        mechanical_connections = ETree.SubElement(xml_connection_list, "MechanicalConnections")

        for output_connection in self.external_output_connections:

            output_xml = ETree.SubElement(mechanical_connections, "output")
            output_xml.set("index", str(output_connection.index))

        return xml_connection_list

    def append_xml_connection_list(self, input_list: ETree.Element):

        fluid_connections = input_list.find("FluidConnections")
        mechanical_connections = input_list.find("MechanicalConnections")

        self.__add_connection_by_index(fluid_connections, "input", append_to_support_block=0)
        self.__add_connection_by_index(fluid_connections, "output", append_to_support_block=0)
        self.__add_connection_by_index(mechanical_connections, "output")

    def __add_connection_by_index(self, input_list: ETree.Element, connection_name, append_to_support_block=None):

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
        return_dict = {"power input": [0, False],
                       "flow input": [1, False],
                       "flow output": [2, False]}

        return return_dict

    @classmethod
    def return_EES_base_equations(cls):

        return_element = dict()

        variables_list = [{"variable": "flow input", "type": costants.ZONE_TYPE_FLOW_RATE},
                          {"variable": "flow output", "type": costants.ZONE_TYPE_FLOW_RATE}]

        return_element.update({"mass_continuity": {"variables": variables_list, "related_option": "none"}})

        return return_element

    def return_other_zone_connections(self, zone_type, input_connection):

        if zone_type == costants.ZONE_TYPE_FLOW_RATE:

            # In the expander flow rate is preserved, hence if "input_connection" stream is connected to the support
            # block (where the fluid streams are connected) the methods returns each fluid stream connected to the
            # support block

            if self.support_block[0].connection_is_in_connections_list(input_connection):

                return self.support_block[0].get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_FLUID:

            # In the expander fluid type is preserved, hence if "input_connection" stream is connected to the support
            # block (where the fluid streams are connected) the methods returns each fluid stream connected to the
            # support block

            if self.support_block[0].connection_is_in_connections_list(input_connection):

                return self.support_block[0].get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_PRESSURE:

            # In the expander pressure is not preserved, hence an empty list is returned
            return list()

        else:

            return list()