from EEETools.MainModules import Block
from EEETools.MainModules.support_blocks import Drawer
import xml.etree.ElementTree as ETree
from EEETools import costants


class CombustionChamber(Block):

    def __init__(self, inputID, main_class):
        super().__init__(inputID, main_class)

        self.type = "combustion chamber"
        self.has_support_block = True
        self.support_block.append(Drawer(main_class, self, is_input=False, allow_multiple_input=False))

    def add_connection_to_support_block(self, new_connection, is_input):
        self.support_block[0].add_connection(new_connection, is_input)

    def is_ready_for_calculation(self):
        return len(self.input_connections) >= 1 and len(self.support_block[0].output_connections) >= 1 and len(
            self.support_block[0].input_connections) >= 1

    def append_excel_connection_list(self, input_list):

        new_conn_fuel_in = self.main_class.find_connection_by_index(abs(input_list[0]))
        new_conn_input_flow = self.main_class.find_connection_by_index(abs(input_list[1]))
        new_conn_output_flow = self.main_class.find_connection_by_index(abs(input_list[2]))

        self.add_connection(new_conn_fuel_in, is_input=True)
        self.add_connection(new_conn_input_flow, is_input=True, append_to_support_block=0)
        self.add_connection(new_conn_output_flow, is_input=False, append_to_support_block=0)

    def export_xml_other_parameters(self) -> ETree.Element:

        other_tree = ETree.Element("Other")
        return other_tree

    def append_xml_other_parameters(self, input_list: ETree.Element):

        pass

    def export_xml_connection_list(self) -> ETree.Element:

        xml_connection_list = ETree.Element("Connections")

        fluid_connections = ETree.SubElement(xml_connection_list, "FluidConnections")

        for input_connection in self.support_block[0].external_input_connections:

            input_xml = ETree.SubElement(fluid_connections, "input")
            input_xml.set("index", str(input_connection.index))

        for output_connection in self.support_block[0].external_output_connections:

            output_xml = ETree.SubElement(fluid_connections, "output")
            output_xml.set("index", str(output_connection.index))

        fuel_connections = ETree.SubElement(xml_connection_list, "FuelConnections")

        for input_connection in self.external_input_connections:

            input_xml = ETree.SubElement(fuel_connections, "input")
            input_xml.set("index", str(input_connection.index))

        return xml_connection_list

    def append_xml_connection_list(self, input_list: ETree.Element):

        fluid_connections = input_list.find("FluidConnections")
        fuel_connections = input_list.find("FuelConnections")

        self.__add_connection_by_index(fluid_connections, "input", append_to_support_block=0)
        self.__add_connection_by_index(fluid_connections, "output", append_to_support_block=0)
        self.__add_connection_by_index(fuel_connections, "input")

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
        return_dict = {"fuel input": [0, False],
                       "flow input": [1, False],
                       "flow output": [2, False]}

        return return_dict

    @classmethod
    def return_EES_base_equations(cls):

        return_element = dict()

        variables_list = [{"variable": "fuel input",  "type": costants.ZONE_TYPE_PRESSURE},
                          {"variable": "flow input",  "type": costants.ZONE_TYPE_PRESSURE},
                          {"variable": "flow output", "type": costants.ZONE_TYPE_PRESSURE}, ]

        return_element.update({"pressure_continuity": {"variables": variables_list, "related_option": "none"}})

        return return_element

    def return_other_zone_connections(self, zone_type, input_connection):

        if zone_type == costants.ZONE_TYPE_FLOW_RATE:

            # In the combustion chamber flow rate is not preserved (input and fuel flows are mixed), hence an empty
            # list is returned

            return list()

        elif zone_type == costants.ZONE_TYPE_FLUID:

            # In the combustion chamber fluid type is preserved, hence if "input_connection" stream is connected to
            # the support block (where the fluid streams are connected) the methods returns each fluid stream
            # connected to the support block.
            #
            # (this is an approximation because we consider that the amount of fuel injected is not enough to modify
            # the main fuel properties, an optional check_box should be considered!!)

            if self.support_block[0].connection_is_in_connections_list(input_connection):

                return self.support_block[0].get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_PRESSURE:

            # In the combustion chamber pressure is preserved, hence if "input_connection" stream is connected to the
            # support block (where the fluid streams are connected) or to the block itself (where the input is
            # connected) the methods returns each fluid stream connected to the support block. In addition,
            # as also the fluid input must have the same pressure, it is added as well!

            if self.support_block[0].connection_is_in_connections_list(input_connection) or self.connection_is_in_connections_list(input_connection):

                return_list = list()
                return_list.extend(self.support_block[0].get_fluid_stream_connections())
                return_list.extend(self.get_fluid_stream_connections())

                return return_list

            else:

                return list()

        else:
            return list()