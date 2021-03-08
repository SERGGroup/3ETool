from ExergoEconomicAnalysisClasses.MainModules import Block
from ExergoEconomicAnalysisClasses.MainModules.support_blocks import Drawer
from res import costants


class HeatExchanger(Block):

    def __init__(self, inputID, main_class):

        super().__init__(inputID, main_class)

        self.type = "heat exchanger"
        self.has_support_block = True

        self.support_block.append(Drawer(main_class, self, is_input=True, allow_multiple_input=False))
        self.support_block.append(Drawer(main_class, self, is_input=False, allow_multiple_input=False))

    def add_new_drawer(self, is_input):
        self.support_block.append(Drawer(self.main_class, self, is_input=is_input))

    def is_ready_for_calculation(self):

        for supp_block in self.support_block:

            if not supp_block.is_ready_for_calculation:
                return False

        return True

    def append_excel_connection_list(self, input_list):

        if str(input_list[0]) in ["Heat Exchanger", "Scambiatore"]:

            new_conn_input_product = self.main_class.find_connection_by_index(abs(input_list[1]))
            new_conn_output_product = self.main_class.find_connection_by_index(abs(input_list[2]))
            new_conn_input_fuel = self.main_class.find_connection_by_index(abs(input_list[3]))
            new_conn_output_fuel = self.main_class.find_connection_by_index(abs(input_list[4]))

            self.add_connection(new_conn_input_product, is_input=True, append_to_support_block=1)
            self.add_connection(new_conn_output_product, is_input=False, append_to_support_block=1)
            self.add_connection(new_conn_input_fuel, is_input=True, append_to_support_block=0)
            self.add_connection(new_conn_output_fuel, is_input=False, append_to_support_block=0)

        elif str(input_list[0]) in ["Heat Exchanger - Multi Fuel", "Scambiatore - Multi Fuel"]:

            new_conn_input_product = self.main_class.find_connection_by_index(abs(input_list[1]))
            new_conn_output_product = self.main_class.find_connection_by_index(abs(input_list[2]))

            self.add_connection(new_conn_input_product, is_input=True, append_to_support_block=1)
            self.add_connection(new_conn_output_product, is_input=False, append_to_support_block=1)

            for elem in input_list[3:]:

                new_conn = self.main_class.find_connection_by_index(abs(elem))

                if not new_conn is None:
                    is_input = (elem > 0)
                    self.add_connection(new_conn, is_input=is_input, append_to_support_block=0)

        else:

            new_conn_input_fuel = self.main_class.find_connection_by_index(abs(input_list[1]))
            new_conn_output_fuel = self.main_class.find_connection_by_index(abs(input_list[2]))

            self.add_connection(new_conn_input_fuel, is_input=True, append_to_support_block=0)
            self.add_connection(new_conn_output_fuel, is_input=False, append_to_support_block=0)

            for elem in input_list[3:]:

                new_conn = self.main_class.find_connection_by_index(abs(elem))

                if not new_conn is None:
                    is_input = (elem > 0)
                    self.add_connection(new_conn, is_input=is_input, append_to_support_block=1)

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

            # In an heat exchanger the flow rate is preserved for each drawer, hence the program identify the drawer
            # to which "input_connection" stream is connected and returns each fluid stream connected to that block

            if connected_drawer is not None:

                return connected_drawer.get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_FLUID:

            # In an heat exchanger fluid type is preserved for each drawer, hence the program identify the drawer to
            # which "input_connection" stream is connected and returns each fluid stream connected to that block

            if connected_drawer is not None:

                return connected_drawer.get_fluid_stream_connections()

            else:

                return list()

        elif zone_type == costants.ZONE_TYPE_PRESSURE:

            # In an heat exchanger pressure is preserved for each drawer, hence the program identify the drawer to which
            # "input_connection" stream is connected and returns each fluid stream connected to that block

            if connected_drawer is not None:

                return connected_drawer.get_fluid_stream_connections()

            else:

                return list()

        else:

            return list()