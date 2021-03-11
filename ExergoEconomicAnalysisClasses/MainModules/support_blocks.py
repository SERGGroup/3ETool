from ExergoEconomicAnalysisClasses.MainModules import Block, ArrayHandler


class Drawer(Block):

    # This class is a simple block subclass that will be used for the definition of support blocks. See the component
    # documentation for further explanations.
    #
    # For the initialization both the input_ID and the main block to which the drawer is connected as a support block
    # are required. Another optional argument has to be passed if the drawer is intended to be added to handle the
    # outputs of the main block

    def __init__(self, main_class: ArrayHandler, main_block: Block, is_input=True, allow_multiple_input=True):

        super().__init__(-100, main_class, is_support_block=True)

        self.index = float(main_block.ID) + (float(len(main_block.support_block)) + 1.) / 100.
        self.type = "drawer"
        self.name = "Support block of: " + str(main_block.name)
        self.main_block = main_block

        self.is_input = is_input
        self.connection_with_main = None

        self.input_mixer = None
        self.output_separator = None

        self.allow_multiple_input = allow_multiple_input

    def add_connection(self, new_connection, is_input, append_to_support_block=None):

        # The "add_connection" method has been overloaded because we want the drawer to have only 3 connection (1 input,
        # 1 output and the "connection_with_main") if the "allow_multiple_input" option is not on. This is needed
        # because of some issue with the EES code generation.
        #
        # The overloaded method calls the super method if the maximum number of connection has not been reached or if
        # the "allow_multiple_input" option is on. Otherwise it will add the connection to a support_block (it choose
        # the right ones between the "input_mixer" or "output_separator" blocks depending on whether the connection
        # to be added is an input or an output) and initialize the support block itself if needed, by calling
        # "__append_support_block".

        if is_input:

            n_connection = self.n_input

            if self.connection_with_main is not None and not self.is_input:
                n_connection -= 1

            support_block = self.input_mixer

        else:

            n_connection = self.n_output

            if self.connection_with_main is not None and self.is_input:
                n_connection -= 1

            support_block = self.output_separator

        if self.allow_multiple_input or n_connection < 1:

            super(Drawer, self).add_connection(new_connection, is_input, append_to_support_block)

        else:

            if support_block is None:
                support_block = self.__append_support_block(is_input)

            support_block.add_connection(new_connection, is_input)

    def remove_connection(self, deleted_conn):

        # The "remove_connection" method has been overloaded because we want the drawer to have only 3 connection (1
        # input, 1 output and the "connection_with_main") if the "allow_multiple_input" option is not on. This is
        # needed because of some issue with the EES code generation.
        #
        # This method calls the super method to remove the connection. Then it checks if the support block (if
        # present) is still needed and remove it otherwise

        super(Drawer, self).remove_connection(deleted_conn)
        self.__check_support_blocks()

    def is_ready_for_calculation(self):

        return_value = self.n_input >= 1 and self.n_output >= 1

        if self.has_support_block:

            for block in self.support_block:
                return_value = return_value and block.is_ready_for_calculation()

        return return_value

    def prepare_for_calculation(self):

        if self.has_support_block:

            for block in self.support_block:
                block.prepare_for_calculation()

        self.update_main_connection()

    def append_excel_connection_list(self, input_list):

        for elem in input_list:

            new_conn = self.main_class.find_connection_by_index(abs(elem))

            if not new_conn is None:
                is_input = (elem > 0)
                self.add_connection(new_conn, is_input)

    def connection_is_in_connections_list(self, connection):

        for connection_list in [self.input_connections, self.output_connections]:

            if connection in connection_list:
                return True

        if self.has_support_block:

            for block in self.support_block:

                if block.connection_is_in_connections_list(connection):
                    return True

        return False

    def get_fluid_stream_connections(self):

        connection_list = super(Drawer, self).get_fluid_stream_connections()

        if self.has_support_block:
            for block in self.support_block:
                connection_list.extend(block.get_fluid_stream_connections())

        return connection_list

    def return_other_zone_connections(self, zone_type, input_connection):

            return self.main_block.return_other_zone_connections(zone_type, input_connection)

    def initialize_main_connection(self):

        # connect support block with main class
        if self.is_input:
            self.__add_connection_manually(self, self.main_block, is_connection_with_main=True)

        else:
            self.__add_connection_manually(self.main_block, self, is_connection_with_main=True)

    def update_main_connection(self):

        if self.connection_with_main is None:
            self.initialize_main_connection()
            self.connection_with_main.is_fluid_stream = False

        if self.is_input:
            self.connection_with_main.exergy_value += self.exergy_balance

        else:
            self.connection_with_main.exergy_value -= self.exergy_balance

    def __add_connection_manually(self, from_block, to_block, is_connection_with_main=False):

        new_connection = self.main_class.append_connection()
        new_connection.set_block(from_block, is_from_block=True)
        from_block.output_connections.append(new_connection)
        from_block.n_output += 1

        new_connection.set_block(to_block, is_from_block=False)
        to_block.input_connections.append(new_connection)
        to_block.n_input += 1

        if is_connection_with_main:
            self.connection_with_main = new_connection

    def __append_support_block(self, is_input=True):

        # This class append an input mixer or an output separator if needed. In fact, drawer class is designed to
        # accept only 3 connections: 1 input, 1 output and the "connection_with_main" because of some issues
        # regarding the EES code definition.
        #
        # In order to deal with such limitation the derawer class is designed so that it will automatically append an
        # input mixer or an output separator so that it can replicate a multiple connection behaviour.
        #
        # This method initializes the support block (it choose between "input_mixer" and "output_separator" according
        # to the "is_input" parameter). It then moves all the input (or output) connections except for the
        # "connection_with_main" to the new block and generate the connection between the new support block and the
        # drawer class.

        self.has_support_block = True
        modules_handler = self.main_class.modules_handler

        if is_input:

            block_subclass = get_support_block_class("mixer", modules_handler)
            self.input_mixer = block_subclass(self.main_class, self, True)
            self.support_block.append(self.input_mixer)

            for connection in self.input_connections:
                if connection is not self.connection_with_main:
                    self.input_mixer.add_connection(connection, is_input=True)

            self.input_connections = list()
            self.n_input = 0

            self.input_mixer.initialize_main_connection()

            return self.input_mixer


        else:

            block_subclass = get_support_block_class("separator", modules_handler)
            self.output_separator = block_subclass(self.main_class, self, False)
            self.support_block.append(self.output_separator)

            for connection in self.output_connections:
                if connection is not self.connection_with_main:
                    self.output_separator.add_connection(connection, is_input=False)

            self.output_connections = list()
            self.n_output = 0

            self.output_separator.initialize_main_connection()

            return self.output_separator

    def __check_support_blocks(self):

        has_support_block = False

        if self.input_mixer is not None:

            if not self.input_mixer.is_needed:

                self.input_mixer.disconnect()
                self.support_block.remove(self.input_mixer)
                self.input_mixer = None

            else:

                has_support_block = True

        if self.output_separator is not None:

            if not self.output_separator.is_needed:

                self.output_separator.disconnect()
                self.support_block.remove(self.output_separator)
                self.output_separator = None

            else:

                has_support_block = True

        self.has_support_block = has_support_block

    @property
    def is_connected(self):
        return not self.connection_with_main is None


def get_support_block_class(block_subclass_name, modules_handler):

    block_subclass = modules_handler.import_correct_sub_class(block_subclass_name)

    class SupportSeparator(block_subclass):

        def __init__(self, main_class: ArrayHandler, main_block: Block, is_input=None):

            super().__init__(-100, main_class)

            self.is_support_block = True
            self.main_block = main_block

            self.__define_is_input(is_input)

            self.type += "-support block"
            self.name = "Support block of: " + str(main_block.name)

            self.connection_with_main = None

        def initialize_main_connection(self):

            if self.is_input:

                self.connection_with_main = self.main_class.append_connection(from_block=self, to_block=self.main_block)

            else:

                self.connection_with_main = self.main_class.append_connection(from_block=self.main_block, to_block=self)

        def update_main_connection(self):

            if self.connection_with_main is None:
                self.initialize_main_connection()

            if self.is_input:
                self.connection_with_main.exergy_value += self.__return_exergy_balance()

            else:
                self.connection_with_main.exergy_value -= self.__return_exergy_balance()

        def disconnect(self):

            if self.is_input:
                connection_list = self.input_connections

            else:
                connection_list = self.output_connections

            if self.connection_with_main is not None:
                self.main_class.remove_connection(self.connection_with_main)

            for conn in connection_list:
                self.main_block.add_connection(conn, is_input=self.is_input)

        def prepare_for_calculation(self):

            self.update_main_connection()

        def is_ready_for_calculation(self):

            return self.n_input >= 1 and self.n_output >= 1

        def __return_exergy_balance(self):

            exergy_balance = 0

            for conn in self.input_connections:
                exergy_balance += conn.exergy_value

            for conn in self.output_connections:
                exergy_balance -= conn.exergy_value

            return exergy_balance

        def __define_is_input(self, is_input):

            if is_input is None:

                if self.type == "mixer":

                    self.is_input = True

                elif self.type == "separator":

                    self.is_input = False

                else:

                    self.is_input = False

            else:

                self.is_input = is_input

        @property
        def is_needed(self):

            if self.is_input:

                return self.n_input > 1

            else:

                return self.n_output > 1

        @property
        def is_connected(self):
            return not self.connection_with_main is None

    return SupportSeparator