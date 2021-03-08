from ExergoEconomicAnalysisClasses.MainModules import Block
from ExergoEconomicAnalysisClasses.MainModules.support_blocks import Drawer

from res import costants


class Compressor(Block):

    def __init__(self, inputID, main_class):

        super().__init__(inputID, main_class)

        self.type = "compressor"
        self.has_support_block = True
        self.support_block.append(Drawer(main_class, self, is_input=False, allow_multiple_input=False))

    def add_connection_to_support_block(self, new_connection, is_input):
        self.support_block[0].add_connection(new_connection, is_input)

    def is_ready_for_calculation(self):

        return len(self.output_connections) >= 1 and len(self.support_block[0].output_connections) >= 1 and len(
            self.support_block[0].input_connections) >= 1

    def append_excel_connection_list(self, input_list):

        new_conn_power = self.main_class.find_connection_by_index(abs(input_list[0]))
        new_conn_input_flow = self.main_class.find_connection_by_index(abs(input_list[1]))
        new_conn_output_flow = self.main_class.find_connection_by_index(abs(input_list[2]))

        new_conn_power.is_fluid_stream = False

        self.add_connection(new_conn_power, is_input=True)
        self.add_connection(new_conn_input_flow, is_input=True, append_to_support_block=0)
        self.add_connection(new_conn_output_flow, is_input=False, append_to_support_block=0)

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

            # In the compressor flow rate is preserved, hence if "input_connection" stream is connected to the support
            # block (where the fluid streams are connected) the methods returns each fluid stream connected to the
            # support block

            if self.support_block[0].connection_is_in_connections_list(input_connection):

                return self.support_block[0].get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_FLUID:

            # In the compressor fluid type is preserved, hence if "input_connection" stream is connected to the support
            # block (where the fluid streams are connected) the methods returns each fluid stream connected to the
            # support block

            if self.support_block[0].connection_is_in_connections_list(input_connection):

                return self.support_block[0].get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_PRESSURE:

            # In the compressor pressure is not preserved, hence an empty list is returned
            return list()

        else:

            return list()
