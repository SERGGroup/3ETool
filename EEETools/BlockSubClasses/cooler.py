from EEETools.MainModules.support_blocks import Drawer
from EEETools.MainModules.main_module import Block
import xml.etree.ElementTree as ETree
from EEETools import costants


class Cooler(Block):

    def __init__(self, inputID, main_class):

        super().__init__(inputID, main_class)

        self.type = "cooler"
        self.has_support_block = True
        self.support_block.append(Drawer(main_class, self, is_input=True))

    def is_ready_for_calculation(self):

        return len(self.input_connections) >= 1 and len(self.output_connections) >= 1

    def prepare_for_calculation(self):

        self.support_block[0].prepare_for_calculation()

    def initialize_connection_list(self, input_list):

        new_power_conn = self.main_class.find_connection_by_index(input_list[0])
        new_input_conn = self.main_class.find_connection_by_index(input_list[1])
        new_output_conn = self.main_class.find_connection_by_index(input_list[2])

        self.add_connection(new_power_conn, is_input=False)
        self.add_connection(new_input_conn, is_input=True, append_to_support_block=0)
        self.add_connection(new_output_conn, is_input=False, append_to_support_block=0)

    def export_xml_connection_list(self) -> ETree.Element:

        xml_connection_list = ETree.Element("Connections")

        fluid_connections = ETree.SubElement(xml_connection_list, "FluidConnections")

        for input_connection in self.support_block[0].external_input_connections:

            input_xml = ETree.SubElement(fluid_connections, "input")
            input_xml.set("index", str(input_connection.index))

        for output_connection in self.support_block[0].external_output_connections:

            output_xml = ETree.SubElement(fluid_connections, "output")
            output_xml.set("index", str(output_connection.index))

        power_connections = ETree.SubElement(xml_connection_list, "PowerConnections")

        for output_connection in self.external_output_connections:

            output_xml = ETree.SubElement(power_connections, "output")
            output_xml.set("index", str(output_connection.index))

        return xml_connection_list

    def append_xml_connection_list(self, input_list: ETree.Element):

        fluid_connections = input_list.find("FluidConnections")
        PowerConnections = input_list.find("PowerConnections")

        self.__add_connection_by_index(fluid_connections, "input", append_to_support_block=0)
        self.__add_connection_by_index(fluid_connections, "output", append_to_support_block=0)
        self.__add_connection_by_index(PowerConnections, "output")

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

        return_dict = {"flow input": [1, False],
                       "flow output": [2, False]}

        return return_dict

    @classmethod
    def return_EES_base_equations(cls):

        return_element = dict()

        variables_list = [{"variable": "flow input", "type": costants.ZONE_TYPE_FLOW_RATE},
                          {"variable": "flow output", "type": costants.ZONE_TYPE_FLOW_RATE}]

        return_element.update({"mass_continuity": {"variables": variables_list, "related_option": "none"}})

        variables_list = [{"variable": "flow input", "type": costants.ZONE_TYPE_PRESSURE},
                          {"variable": "flow output", "type": costants.ZONE_TYPE_PRESSURE}]

        return_element.update({"pressure_continuity": {"variables": variables_list, "related_option": "none"}})

        return return_element

    def return_other_zone_connections(self, zone_type, input_connection):

        if zone_type == costants.ZONE_TYPE_FLOW_RATE:

            # In the cooler flow rate is preserved, hence if "input_connection" stream is connected to the condenser
            # block the methods must returns each fluid stream connected to that block

            if self.connection_is_in_connections_list(input_connection):

                return self.get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_FLUID:

            # In the condenser fluid type is preserved, hence if "input_connection" stream is connected to the condenser
            # block the methods must returns each fluid stream connected to that block

            if self.connection_is_in_connections_list(input_connection):

                return self.get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_PRESSURE:

            # In the condenser pressure is preserved, hence if "input_connection" stream is connected to the condenser
            # block the methods must returns each fluid stream connected to that block

            if self.connection_is_in_connections_list(input_connection):

                return self.get_fluid_stream_connections()

            else:

                return list()

        else:

            return list()