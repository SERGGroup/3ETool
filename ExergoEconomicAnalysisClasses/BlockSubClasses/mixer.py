from ExergoEconomicAnalysisClasses.MainModules import Block
import xml.etree.ElementTree as ETree
from res import costants


class Mixer(Block):

    def __init__(self, inputID, main_class):
        Block.__init__(self, inputID, main_class)
        self.type = "mixer"

    def is_ready_for_calculation(self):
        return len(self.input_connections) >= 1 and len(self.output_connections) >= 1

    def append_excel_connection_list(self, input_list):

        for elem in input_list:

            new_conn = self.main_class.find_connection_by_index(abs(elem))

            if not new_conn is None:

                is_input = (elem > 0)
                self.add_connection(new_conn, is_input)

    def export_xml_other_parameters(self) -> ETree.Element:

        other_tree = ETree.Element("Other")
        return other_tree

    def append_xml_other_parameters(self, input_list: ETree.Element):

        pass

    def export_xml_connection_list(self) -> ETree.Element:

        xml_connection_list = ETree.Element("Connections")
        fluid_connections = ETree.SubElement(xml_connection_list, "FluidConnections")

        for input_connection in self.external_input_connections:

            input_xml = ETree.SubElement(fluid_connections, "input")
            input_xml.set("index", str(input_connection.index))

        for output_connection in self.external_output_connections:

            output_xml = ETree.SubElement(fluid_connections, "output")
            output_xml.set("index", str(output_connection.index))

        return xml_connection_list

    def append_xml_connection_list(self, input_list: ETree.Element):

        fluid_connections = input_list.find("FluidConnections")

        self.__add_connection_by_index(fluid_connections, "input")
        self.__add_connection_by_index(fluid_connections, "output")

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

        return_dict = {"flow input": [1, True],
                       "flow output": [2, False]}

        return return_dict

    @classmethod
    def return_EES_base_equations(cls):

        return_element = dict()

        variables_list = [{"variable": "flow input", "type": costants.ZONE_TYPE_PRESSURE},
                          {"variable": "flow output", "type": costants.ZONE_TYPE_PRESSURE}]

        return_element.update({"pressure_continuity": {"variables": variables_list, "related_option": "none"}})

        return return_element

    def return_other_zone_connections(self, zone_type, input_connection):

        if zone_type == costants.ZONE_TYPE_FLOW_RATE:

            # In a mixer the flow rate is not preserved, hence an empty list is returned

                return list()

        elif zone_type == costants.ZONE_TYPE_FLUID:

            # In a mixer the fluid type is preserved, hence if "input_connection" stream is connected to the
            # block the methods returns each fluid stream connected to it

            if self.connection_is_in_connections_list(input_connection):

                return self.get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_PRESSURE:

            # In a mixer the pressure is preserved, hence if "input_connection" stream is connected to the
            # block the methods returns each fluid stream connected to it

            if self.connection_is_in_connections_list(input_connection):

                return self.get_fluid_stream_connections()

            else:

                return list()

        else:

            return list()