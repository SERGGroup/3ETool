from ExergoEconomicAnalysisClasses.MainModules import Block
from res import costants


class Valve(Block):

    def __init__(self, inputID, main_class):

        super().__init__(inputID, main_class)

        self.type = "valve"
        self.has_support_block = False

    def is_ready_for_calculation(self):
        return len(self.input_connections) >= 1 and len(self.output_connections) >= 1

    def append_excel_connection_list(self, input_list):

        new_input_conn = self.main_class.find_connection_by_index(input_list[0])
        new_output_conn = self.main_class.find_connection_by_index(input_list[1])

        self.add_connection(new_input_conn, is_input=True)
        self.add_connection(new_output_conn, is_input=False)

    @classmethod
    def return_EES_needed_index(cls):
        return_dict = {"flow input" : [1, False],
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

            # In a valve the flow rate is preserved, hence if "input_connection" stream is connected to the
            # block the methods returns each fluid stream connected to it

            if self.connection_is_in_connections_list(input_connection):

                return self.get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_FLUID:

            # In a valve the fluid type is preserved, hence if "input_connection" stream is connected to the
            # block the methods returns each fluid stream connected to it

            if self.connection_is_in_connections_list(input_connection):

                return self.get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_PRESSURE:

            # In a valve the pressure is not preserved, hence an empty list is returned
            return list()

        else:

            return list()