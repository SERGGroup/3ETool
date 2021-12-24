from EEETools.MainModules import Block
from EEETools.MainModules.support_blocks import Drawer
import xml.etree.ElementTree as ETree
from EEETools import costants


# EXACTLY THE SAME AS HEAT_EXCHANGER (Maintained only to keep the analogy with Matlab application)

class Evaporator(Block):

    def __init__(self, inputID, main_class):

        super().__init__(inputID, main_class)

        self.type = "evaporator"
        self.has_support_block = True

        self.support_block.append(Drawer(main_class, self, is_input=True, allow_multiple_input=False))
        self.support_block.append(Drawer(main_class, self, is_input=False, allow_multiple_input=False))

    def add_new_drawer(self, is_input):
        self.support_block.append(Drawer(self.main_class, self, is_input=is_input, allow_multiple_input=False))

    def is_ready_for_calculation(self):

        for supp_block in self.support_block:

            if not supp_block.is_ready_for_calculation:
                return False

        return True

    def initialize_connection_list(self, input_list):

        new_conn_input_product = self.main_class.find_connection_by_index(abs(input_list[0]))
        new_conn_output_product = self.main_class.find_connection_by_index(abs(input_list[1]))

        self.add_connection(new_conn_input_product, is_input=True, append_to_support_block=1)
        self.add_connection(new_conn_output_product, is_input=False, append_to_support_block=1)

        for elem in input_list[2:]:

            new_conn = self.main_class.find_connection_by_index(abs(elem))

            if new_conn is not None:
                is_input = (elem > 0)
                self.add_connection(new_conn, is_input=is_input, append_to_support_block=0)

    def export_xml_other_parameters(self) -> ETree.Element:

        other_tree = ETree.Element("Other")
        return other_tree

    def append_xml_other_parameters(self, input_list: ETree.Element):

        pass

    def export_xml_connection_list(self) -> ETree.Element:

        xml_connection_list = ETree.Element("Connections")

        fuels_connections = ETree.SubElement(xml_connection_list, "FuelsConnections")
        product_connections = ETree.SubElement(xml_connection_list, "ProductConnections")

        for support_block in self.support_block:

            if support_block.is_input:

                main_tree = ETree.SubElement(fuels_connections, "Block")

            else:

                main_tree = ETree.SubElement(product_connections, "Block")

            for input_connection in support_block.external_input_connections:

                input_xml = ETree.SubElement(main_tree, "input")
                input_xml.set("index", str(input_connection.index))

            for output_connection in support_block.external_output_connections:

                output_xml = ETree.SubElement(main_tree, "output")
                output_xml.set("index", str(output_connection.index))

        return xml_connection_list

    def append_xml_connection_list(self, input_list: ETree.Element):

        fuels_connections = input_list.find("FuelsConnections")
        product_connections = input_list.find("ProductConnections")

        self.__add_support_blocks(len(fuels_connections.findall("Block")), True)
        self.__add_support_blocks(len(product_connections.findall("Block")), False)

        i = 0
        support_block_array = self.input_support_block
        for connection in fuels_connections.findall("Block"):
            self.__add_connection_by_index(connection, "input", append_to_support_block=support_block_array[i])
            self.__add_connection_by_index(connection, "output", append_to_support_block=support_block_array[i])
            i = i + 1

        i = 0
        support_block_array = self.output_support_block
        for connection in product_connections.findall("Block"):
            self.__add_connection_by_index(connection, "input", append_to_support_block=support_block_array[i])
            self.__add_connection_by_index(connection, "output", append_to_support_block=support_block_array[i])
            i = i + 1

    def __add_connection_by_index(self, input_list: ETree.Element, connection_name, append_to_support_block=None):

        if connection_name == "input":

            is_input = True

        else:

            is_input = False

        for connection in input_list.findall(connection_name):

            new_conn = self.main_class.find_connection_by_index(float(connection.get("index")))

            if new_conn is not None:
                self.add_connection(new_conn, is_input, append_to_support_block = append_to_support_block)

    def __add_support_blocks(self, n_support_blocks, is_input):

        for i in range(1, n_support_blocks):

            self.add_new_drawer(is_input)

    @property
    def input_support_block(self) -> list:

        return_list = list()

        for support_block in self.support_block:

            if support_block.is_input:

                return_list.append(support_block)

        return return_list

    @property
    def output_support_block(self) -> list:

        return_list = list()

        for support_block in self.support_block:

            if not support_block.is_input:
                return_list.append(support_block)

        return return_list

    @classmethod
    def return_EES_needed_index(cls):

        return_dict = {"input_1": [1, False],
                       "output_1": [1, False],
                       "input_2": [1, False],
                       "output_2": [1, False]}

        return return_dict

    @classmethod
    def return_EES_base_equations(cls):

        return_element = dict()

        variables_list = [{"variable": "input_1", "type": costants.ZONE_TYPE_FLOW_RATE},
                          {"variable": "output_1", "type": costants.ZONE_TYPE_FLOW_RATE}]

        return_element.update({"mass_continuity_1": {"variables": variables_list, "related_option": "none"}})

        variables_list = [{"variable": "input_2", "type": costants.ZONE_TYPE_FLOW_RATE},
                          {"variable": "output_2", "type": costants.ZONE_TYPE_FLOW_RATE}]

        return_element.update({"mass_continuity_2": {"variables": variables_list, "related_option": "none"}})

        variables_list = [{"variable": "input_1", "type": costants.ZONE_TYPE_PRESSURE},
                          {"variable": "output_1", "type": costants.ZONE_TYPE_PRESSURE}]

        return_element.update({"pressure_continuity_1": {"variables": variables_list, "related_option": "none"}})

        variables_list = [{"variable": "input_2", "type": costants.ZONE_TYPE_PRESSURE},
                          {"variable": "output_2", "type": costants.ZONE_TYPE_PRESSURE}]

        return_element.update({"pressure_continuity_2": {"variables": variables_list, "related_option": "none"}})

        return return_element

    def return_other_zone_connections(self, zone_type, input_connection):

        connected_drawer = None
        for drawer in self.support_block:

            if drawer.connection_is_in_connections_list(input_connection):
                connected_drawer = drawer
                break

        if zone_type == costants.ZONE_TYPE_FLOW_RATE:

            # In the evaporator flow rate is preserved for each drawer, hence the program identify the drawer to which
            # "input_connection" stream is connected and returns each fluid stream connected to that block

            if connected_drawer is not None:

                return connected_drawer.get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_FLUID:

            # In the evaporator fluid type is preserved for each drawer, hence the program identify the drawer to which
            # "input_connection" stream is connected and returns each fluid stream connected to that block

            if connected_drawer is not None:

                return connected_drawer.get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_PRESSURE:

            # In the evaporator pressure is preserved for each drawer, hence the program identify the drawer to which
            # "input_connection" stream is connected and returns each fluid stream connected to that block

            if connected_drawer is not None:

                return connected_drawer.get_fluid_stream_connections()

            else:

                return list()

        else:

            return list()
