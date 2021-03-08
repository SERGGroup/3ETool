from ExergoEconomicAnalysisClasses.Tools.modules_handler import ModulesHandler
import warnings
import numpy as np
import copy
from res import costants


class Block:

    # Construction Methods
    def __init__(self, inputID, main_class, is_support_block=False):

        self.__ID = inputID

        self.index = inputID
        self.name = " "
        self.type = "generic"

        self.comp_cost = 0.
        self.output_cost = 0.

        self.input_connections = list()
        self.output_connections = list()

        self.n_input = 0
        self.n_output = 0

        self.is_support_block = is_support_block
        self.has_modification = False
        self.has_support_block = False

        self.move_skipped_block_at_the_end = False
        self.calculate_by_streams = False

        self.error_value = 0

        self.main_class = main_class
        self.support_block = list()
        self.main_block = None
        self.connection_with_main = None

    # Getter and Setter
    def modify_ID(self, newID):

        # When the ID of the block is modified, for exemple in ordering the BlockArray List, the ID has to be modified
        # also in the connection related to the block

        self.__ID = newID

    @property
    def ID(self):
        return self.__ID

    def add_connection(self, new_connection, is_input, append_to_support_block=None):

        if append_to_support_block is None:

            if is_input:

                new_connection.set_block(self, is_from_block=False)
                self.input_connections.append(new_connection)
                self.n_input += 1

            else:

                new_connection.set_block(self, is_from_block=True)
                self.output_connections.append(new_connection)
                self.n_output += 1

        else:

            if issubclass(type(append_to_support_block), Block) or type(append_to_support_block) is Block:

                sel_block = append_to_support_block

            else:

                try:
                    sel_block = self.support_block[int(append_to_support_block)]

                except:

                    warningString = ""
                    warningString += str(append_to_support_block) + " is not a suitable index"
                    warningString += " connection not updated"

                    warnings.warn(warningString)
                    return

            sel_block.add_connection(new_connection, is_input)

    def remove_connection(self, deleted_conn):

        # This method tries to remove the connection from the input_connections List (it can do that because
        # connection class has __eq__ method implemented) if the elimination does not succeed (i.e. there is not such
        # connection in the List) it rises a warning and exit

        # The method search the connection to be deleted in the input_connection list and in the output_connection
        # list. If none of this search succeed the method repeat the search in the support blocks

        try:

            self.input_connections.remove(deleted_conn)

        except:

            try:

                self.output_connections.remove(deleted_conn)

            except:

                found = False

                if self.has_support_block:

                    warnings.filterwarnings("error")

                    for block in self.support_block:

                        try:
                            block.remove_connection(deleted_conn)

                        except:
                            pass

                        else:
                            found = True

                    warnings.filterwarnings("default")

                if not found:
                    warningString = ""
                    warningString += "You're trying to delete "
                    warningString += str(deleted_conn) + " from " + str(self) + " but "
                    warningString += "the connection is not related with the selected block"

                    warnings.warn(warningString)

            else:

                # if the connection is found in the outputs its toBlockID is replaced with -1
                # (default for disconnected streams, it means that its an exergy input with cost 0)
                deleted_conn.set_block(None, is_from_block=True)

        else:

            # if the connection is found in the inputs its toBlockID is replaced with -1
            # (default for disconnected streams, it means that its an exergy loss)
            deleted_conn.set_block(None, is_from_block=False)

    def append_output_cost(self, defined_steam_cost):

        # The stream cost is calculated in the overall calculation,
        # this method is meant to be used in order to assign the
        # right cost to the output streams

        # Cost of the exergy losses will be considered as 0

        self.output_cost = defined_steam_cost

        for outConn in self.output_connections:

            if outConn.is_loss:
                outConn.set_cost(0)

            else:
                outConn.set_cost(defined_steam_cost)

    def disconnect_block(self):

        # this method will remove every connection from the block, it is usefull if the block has to be deleted

        _tmpConnectionArray = copy.deepcopy(self.input_connections)
        _tmpConnectionArray.extend(copy.deepcopy(self.output_connections))

        for conn in _tmpConnectionArray:
            self.remove_connection(conn)

    def append_excel_connection_list(self, input_list):

        raise (NotImplementedError, "block.append_excel_connection_list() must be overloaded in subclasses")

    # Calculation Methods
    def get_matrix_row(self, n_elements):

        if self.calculate_by_streams:

            return self.__get_matrix_row_by_stream(n_elements)

        else:

            return self.__get_matrix_row_by_block(n_elements)

    def __get_matrix_row_by_block(self, n_blocks):

        # This Methods returns the row of the Cost Matrix corresponding to the current block in a block-oriented
        # computation scheme

        # The Cost Matrix is a squared matrix of size NXN where N is the number of blocks. Another column,
        # representing the known variables vector has been added at the end of the matrix, hence its actual
        # dimensions are NX(N+1). In the Cost Matrix the elements on the diagonal correspond to the Exergetic value
        # of the flows exiting from the block while the off-diagonal elements match with the input flows into the
        # blocks. Off-diagonal terms must be negative. For example at column "m" you will find the exergy flux coming
        # into the component from block with ID "m".

        # The last column represent known variable and should be filled with the known costs
        # For further details please refers to the paper (to be quoted)

        # line initialization with an array of zeroes (dimension N+1)
        row = np.zeros(n_blocks + 1)
        element_cost = self.comp_cost
        exergy_sum = 0

        # This part of the code scrolls the input connections, for each of them it checks if che connection
        # came form another block (it's an internal connection) or if it's a system input.
        # In the latter case its absolute cost must be known so it will be considered as a known variable
        # result is written in the last column

        for conn in self.input_connections:

            if not (conn.is_system_input or conn.exergy_value == 0):

                row[conn.fromID] = -conn.exergy_value

            else:

                element_cost += conn.exergy_value * conn.relCost

        row[-1] = element_cost

        # Output connections are scrolled, if they are not exergy losses their exergy values is summed up
        # result is written in the column related to the current block

        for conn in self.output_connections:

            if not conn.is_loss:
                exergy_sum += conn.exergy_value

        row[self.ID] = exergy_sum

        return row

    def __get_matrix_row_by_stream(self, n_blocks):

        # This Methods returns the rows of the Cost Matrix corresponding to the current block in a stream-oriented
        # computation scheme

        # The Cost Matrix is a squared matrix of size NXN where N is the number of streams. Another column,
        # representing the known variables vector has been added at the end of the matrix, hence its actual
        # dimensions are NX(N+1).
        #
        # The Cost Matrix is composed by the balance equation for each component equations and by some support
        # equation needed for the system to be solvable. In our case the only support equation allowed (due to the
        # presence of support blocks) are:
        #
        #       - cost of each non-loss output streams has to be equal
        #       - cost of each loss output streams has to be 0
        #
        # The cost balance equation is composed as follows:
        #
        #       - for input streams with undefined exergy cost must be inserted in the matrix with negative sign
        #       - for output streams exergy value must be inserted in the matrix with positive sign
        #       - The last column represent known variable and should be filled with the known costs
        #
        # For further details please refers to the paper (to be quoted)

        # initialization with an matrix of zeroes (dimension [n_output, N+1])
        sub_martix = np.zeros((self.n_non_empty_output, n_blocks + 1))
        row = 0

        # COMPONENT COST BALANCE EQUATION

        # Output connections are scrolled and added to the matrix with positive sign
        for conn in self.output_connections:

            if not conn.has_to_be_skipped:

                sub_martix[row, conn.ID] = conn.exergy_value

        # This part of the code scrolls the input connections, for each of them it checks if che connection
        # came form another block (it's an internal connection) or if it's a system input.
        # In the latter case its absolute cost must be known so it will be considered as a known variable
        # result is written in the last column

        element_cost = self.comp_cost

        for conn in self.input_connections:

            if not conn.has_to_be_skipped:

                sub_martix[row, conn.ID] = -conn.exergy_value

            else:

                element_cost += conn.exergy_value * conn.relCost

        sub_martix[row, -1] = element_cost

        # COMPONENT SUPPORT EQUATIONS
        if self.n_non_empty_output > 1:

            row += 1

            # Each output cost is equal
            if self.n_non_loss_output > 1:

                non_loss_output = self.non_loss_output
                for i in range(1, self.n_non_loss_output):

                    sub_martix[row, non_loss_output[0].ID] = 1
                    sub_martix[row, non_loss_output[i].ID] = -1
                    row += 1

            # Loss cost 0
            for conn in self.output_connections:

                if conn.is_loss and (not conn.has_to_be_skipped):

                    sub_martix[row, conn.ID] = 1
                    row += 1

        return sub_martix

    def prepare_for_calculation(self):

        # This method is used in block's subclasses to execute the calculations needed before the launch of the main
        # calculation, it has to be overloaded if needed

        pass

    # Support Methods
    @property
    def is_ready_for_calculation(self):

        # This method is used to check if the block has every input it needs to perform a calculation.
        # WARING: IT HAS TO BE OVERLOADED BY SUBCLASSES!!

        if type(self) is Block:
            return True

        else:
            raise (NotImplementedError, "block.is_ready_for_calculation() must be overloaded in subclasses")

    @property
    def get_main_ID(self):

        if self.is_support_block:

            return self.main_block.get_main_ID

        else:

            return self.ID

    @property
    def has_to_be_skipped(self):

        # this method returns true if all the outputs are exergy losses or have an exergy value equal to 0
        # hence the corresponding column in the solution matrix will be and empty vector resulting in a singular matrix

        # To avoid this issue the program automatically skips such block in the solution matrix and set its stream
        # cost to 0

        for outConn in self.output_connections:

            if (not outConn.is_loss) and (not outConn.exergy_value == 0):
                return False

        return True

    @property
    def non_loss_output(self):

        # This method returns a list of non-loss output, hence it scrolls the output connection and append the
        # connections that are not losses

        output_list = list()

        for outConn in self.output_connections:

            if (not outConn.is_loss) and (not outConn.exergy_value == 0):
                output_list.append(outConn)

        return output_list

    @property
    def n_non_loss_output(self):

        # This method the number of non-loss output, hence it scrolls the output connection and count the number of
        # them which are not losses

        counter = 0
        for outConn in self.output_connections:

            if (not outConn.is_loss) and (not outConn.exergy_value == 0):

                counter += 1

        return counter

    @property
    def n_non_empty_output(self):

        # This method the number of non-empty output, hence it scrolls the output connection and count the number of
        # them which are not empty
        counter = 0
        for outConn in self.output_connections:

            if not outConn.has_to_be_skipped:
                counter += 1

        return counter

    # EES Methods
    @classmethod
    def return_EES_needed_index(cls):

        # WARNING: This methods must be overloaded in subclasses!!
        # This methods returns a dictionary that contain a list of streams that have to be present in the EES text
        # definition.
        #
        # The first element of the list must be an index and means that the EES script must contains indices [$0],
        # [$1] and [$2] (the actual value can be updated in the editor).
        #
        # If the second element is True it means that multiple inputs can be connected to that port (for example a
        # mixer can have different input streams). This enables the usage of specific keywords ($sum, $multiply and
        # $repeat). If none of the key_words has been imposed the system automatically subsitute the index with the
        # first one in list ignoring the others. The the mixer example below should clarify this passage:

        #  EXPANDER EXAMPLE
        #
        #   dict:
        #
        #       { "output power index" : [0, True] }
        #       { "input flow index"   : [1, False] }
        #       { "output flow index"  : [2, False] }
        #
        #   EES text:
        #
        #   "TURBINE [$block_index]"
        #
        #   turb_DeltaP[$block_index] = $input[0]
        #   turb_eff[$block_index] = $input[1]
        #
        #   s_iso[$2] = s[$1]
        #   h_iso[$2] = enthalpy($fluid, P = P[$2], s = s_iso[$2])
        #
        #   p[$2] = p[$1] - turb_DeltaP[$block_index]
        #   h[$2] = h[$1] - (h[$1] - h_iso[$2])*turb_eff[$block_index]
        #   T[$2] = temperature($fluid, P = P[$2], h = h[$2])
        #   s[$2] = entropy($fluid, P = P[$2], h = h[$2])
        #   m_dot[$2] = m_dot[$1]
        #
        #   $sum{W[$0]} = m_dot[$2]*(h[$1] - h[$2])

        #  MIXER EXAMPLE
        #
        #   dict:
        #
        #       { "input flow index"   : [0, True] }
        #       { "output flow index"  : [1, False] }
        #
        #   EES text:
        #
        #   "Mixer [$block_index]"
        #
        #   "mass balance"
        #   m_dot[$1] = $sum{m_dot[$0]}
        #
        #   "energy balance"
        #   m_dot[$1]*h[$1] = $sum{m_dot[$0]*h[$0]}
        #
        #   "set pressure"
        #   p[$1] = p[$0]
        #

        if type(cls) is Block:
            return dict()

        else:
            raise (NotImplementedError, "block.is_ready_for_calculation() must be overloaded in subclasses")

    @classmethod
    def return_EES_base_equations(cls):

        # WARNING: This methods must be overloaded in subclasses!!
        # This methods returns a dictionary that contain a list of streams that have to be present in the EES text
        # definition.

        if type(cls) is Block:
            return dict()

        else:
            raise (NotImplementedError, "block.is_ready_for_calculation() must be overloaded in subclasses")

    def return_other_zone_connections(self, zone_type, input_connection):

        # WARNING: This methods must be overloaded in subclasses!!
        #
        # This method is needed in order to generate zones (that is to say a list of connections that shares some
        # thermodynamic parameter (e.g. "flow rate" zone is a list of connections that has the same flow rate)
        #
        # This method must return a list of connections connected to the block that belongs to the same zone as
        # "input_connection".
        #
        # For example: as in a Turbine the flow rate is conserved between input and output, if this method is invoked
        # with flow_input as "input_connection" and with "flow rate" as zone_type it must return a list containing
        # flow_output

        if type(self) is Block:
            return list()

        else:
            raise (NotImplementedError, "block.is_ready_for_calculation() must be overloaded in subclasses")

    def connection_is_in_connections_list(self, connection):

        return connection in self.input_connections or connection in self.output_connections

    def get_fluid_stream_connections(self):

        connection_list = list()

        for connection in self.input_connections:

            if connection.is_fluid_stream:
                connection_list.append(connection)

        for connection in self.output_connections:

            if connection.is_fluid_stream:
                connection_list.append(connection)

        return connection_list

    # Overloaded Method

    def __this_has_higher_skipping_order(self, other):

        if self.has_to_be_skipped == other.has_to_be_skipped:

            return None

        else:

            return self.has_to_be_skipped

    def __this_has_higher_support_block_order(self, this, other):

        if this.is_support_block == other.is_support_block:

            if this.is_support_block:

                return self.__this_has_higher_support_block_order(this.main_block, other.main_block)

            else:

                return None

        else:

            return this.is_support_block

    def __gt__(self, other):

        # enables comparison
        # self > other

        skipping_order = self.__this_has_higher_skipping_order(other)

        if skipping_order is not None and self.move_skipped_block_at_the_end:

            return skipping_order

        else:

            self_has_higher_support_block_order = self.__this_has_higher_support_block_order(self, other)

            if self_has_higher_support_block_order is None:

                # if both are (or not are) support blocks the program check the IDs
                # (hence self > other if self.ID > other.ID)
                return self.ID > other.ID

            else:

                # if only one of the two is a support blocks the program return the support block as the greatest of the
                # couple (hence self > other if other.is_support_block = False AND self.is_support_block = True)
                return self_has_higher_support_block_order

    def __lt__(self, other):

        # enables comparison
        # self < other

        skipping_order = self.__this_has_higher_skipping_order(other)

        if skipping_order is not None and self.move_skipped_block_at_the_end:

            return not skipping_order

        else:

            self_has_higher_support_block_order = self.__this_has_higher_support_block_order(self, other)

            if self_has_higher_support_block_order is None:

                # if both are (or not are) support blocks the program check the IDs
                # (hence self < other if self.ID < other.ID)
                return self.ID < other.ID

            else:

                # if only one of the two is a support blocks the program return the support block as the greatest of the
                # couple (hence self < other if other.is_support_block = True AND self.is_support_block = False)
                return not self_has_higher_support_block_order

    def __le__(self, other):

        return not self.__gt__(other)

    def __ge__(self, other):

        return not self.__lt__(other)

    def __str__(self):

        # enables printing and str() method
        # e.g. str(Block1) -> "Block (ID: 2, name: Expander 1)"

        string2Print = "Block "
        string2Print += "(ID: " + str(self.ID)
        string2Print += ", name: " + str(self.name)
        string2Print += ", type: " + str(self.type) + ")"

        return string2Print

    def __repr__(self):

        # enables simple representation
        # e.g. Block1 -> "Block (ID: 2, name: Expander 1)"

        return str(self)


class Connection:

    # Construction Methods
    def __init__(self, inputID, from_block_input=None, to_block_input=None, exergy_value=0, is_fluid_stream=True):

        self.__ID = inputID

        self.index = inputID
        self.name = " "

        self.from_block = from_block_input
        self.to_block = to_block_input

        self.relCost = 0.
        self.exergy_value = exergy_value

        self.is_useful_effect = False
        self.is_fluid_stream = is_fluid_stream

        self.zones = {costants.ZONE_TYPE_FLUID: None,
                      costants.ZONE_TYPE_FLOW_RATE: None,
                      costants.ZONE_TYPE_PRESSURE: None,
                      costants.ZONE_TYPE_ENERGY: None}

        self.sort_by_index = True

    def set_block(self, block, is_from_block):

        if is_from_block:

            self.from_block = block

        else:

            self.to_block = block

    # EES Checker Methods
    def add_zone(self, zone):

        self.zones[zone.type] = zone

    def return_other_zone_connections(self, zone):

        __tmp_zone_connections = list()

        if self.to_block is not None:
            __tmp_zone_connections.extend(self.to_block.return_other_zone_connections(zone.type, self))

        if self.from_block is not None:
            __tmp_zone_connections.extend(self.from_block.return_other_zone_connections(zone.type, self))

        return __tmp_zone_connections

    # Property setter and getter
    @property
    def ID(self):

        return self.__ID

    def modify_ID(self, inputID):

        self.__ID = inputID

    @property
    def fromID(self):
        if self.from_block is not None:
            return self.from_block.ID
        else:
            return -1

    @property
    def toID(self):
        if self.to_block is not None:
            return self.to_block.ID
        else:
            return -1

    def set_cost(self, cost):

        self.relCost = cost

    # Boolean Methods
    @property
    def is_system_input(self):

        return self.fromID == -1

    @property
    def is_block_input(self):

        return not self.toID == -1

    @property
    def is_loss(self):

        return (self.toID == -1 and not self.is_useful_effect)

    @property
    def is_internal_stream(self):

        if not (self.to_block is None or self.from_block is None):

            if self.to_block.get_main_ID == self.from_block.get_main_ID:
                return True

        return False

    @property
    def has_to_be_skipped(self):

        # This method returns true the stream exergy value equal to 0 hence the corresponding column in the solution
        # matrix will be and empty vector resulting in a singular matrix

        # To avoid this issue the program automatically skips such block in the solution matrix and set its stream
        # cost to 0

        return (self.exergy_value == 0) or self.is_system_input or self.is_loss

    # Overloaded Methods

    def __this_has_higher_skipping_order(self, other):

        if self.has_to_be_skipped == other.has_to_be_skipped:

            return None

        else:

            return self.has_to_be_skipped

    def __gt__(self, other):

        # enables comparison
        # self > other

        if self.sort_by_index:

            return self.index > other.index

        else:

            skipping_order = self.__this_has_higher_skipping_order(other)

            if skipping_order is not None:

                return skipping_order

            else:

                # if both are (or not are) to be skipped the program check the IDs
                # (hence self > other if self.ID > other.ID)
                return self.ID > other.ID

    def __lt__(self, other):

        # enables comparison
        # self < other
        if self.sort_by_index:

            return self.index < other.index

        else:

            skipping_order = self.__this_has_higher_skipping_order(other)

            if skipping_order is not None:

                return not skipping_order

            else:

                # if both are (or not are) to be skipped the program check the IDs
                # (hence self < other if self.ID < other.ID)
                return self.ID < other.ID

    def __le__(self, other):

        return not self.__gt__(other)

    def __ge__(self, other):

        return not self.__lt__(other)

    def __eq__(self, other):

        # enables comparison
        # Connection1 == Connection2 -> True if ID1 = ID2

        return self.ID == other.ID

    def __str__(self):

        # enables printing and str() method
        # e.g. str(Block1) -> "Connection (ID: 2, name: Expander 1, from: 5, to:3)"
        if not self.from_block is None:

            from_ID = self.from_block.get_main_ID

        else:

            from_ID = self.fromID

        if not self.to_block is None:

            to_ID = self.to_block.get_main_ID

        else:

            to_ID = self.toID

        string2Print = "Connection "
        string2Print += "(ID: " + str(self.ID)
        string2Print += ", name: " + str(self.name)
        string2Print += ", from: " + str(from_ID)
        string2Print += ", to: " + str(to_ID) + ")"

        return string2Print

    def __repr__(self):

        # enables simple representation
        # e.g. Block1 -> "Block (ID: 2, name: Expander 1)"

        return str(self)


class ArrayHandler:

    def __init__(self):

        self.block_list = list()
        self.n_block = 0
        self.n_block_matrix = 0

        self.connection_list = list()
        self.n_connection = 0
        self.n_conn_matrix = 0

        self.matrix = np.zeros(0)
        self.vector = np.zeros(0)

        self.modules_handler = ModulesHandler()
        self.calculate_by_streams = False

    def append_block(self, input_element="Generic"):

        # this method accepts three types of inputs:
        #
        #   - a Block or one of its subclasses:
        #       in this case the object is directly appended to the list
        #
        #   - a str or something that can be converted to a string containing the name of the block subclass that had
        #     to be added:
        #       in this case the method automatically import the correct block sub-class and append it to the blockArray
        #       list if there is any problem with the import process the program will automatically import the "generic"
        #       subclass
        #
        #   - a List:
        #       in this case append_block method is invoked for each component of the list

        if type(input_element) is list:

            new_blocks = list()

            for elem in input_element:
                new_block = self.append_block(elem)
                new_blocks.append(new_block)

            self.__reset_IDs(reset_block=True)
            return new_blocks

        else:

            if issubclass(type(input_element), Block) or type(input_element) is Block:

                new_block = input_element

            else:

                try:

                    block_class = self.import_correct_sub_class(str(input_element))

                except:

                    block_class = self.import_correct_sub_class("Generic")

                new_block = block_class(self.n_block, self)

            self.n_block += 1
            self.block_list.append(new_block)
            self.__reset_IDs(reset_block=True)

            return new_block

    def append_connection(self, new_conn=None, from_block=None, to_block=None):

        if new_conn is None:
            new_conn = Connection(self.n_connection)

        self.__try_append_connection(new_conn, from_block, is_input=False)
        self.__try_append_connection(new_conn, to_block, is_input=True)

        if not new_conn in self.connection_list:
            self.connection_list.append(new_conn)
            self.__reset_IDs(reset_block=False)

        return new_conn

    def remove_block(self, block, disconnect_block=True):

        if block in self.block_list:

            if disconnect_block:
                block.disconnect_block()

            self.block_list.remove(block)

        else:

            warningString = ""
            warningString += "You're trying to delete "
            warningString += str(block) + " from block list but "
            warningString += "that block isn't in the list"

            warnings.warn(warningString)

        self.__reset_IDs(reset_block=True)

    def remove_connection(self, connection):

        if connection in self.connection_list:

            if not connection.is_system_input:
                self.block_list[connection.fromID].remove_connection(connection)

            if connection.is_block_input:
                self.block_list[connection.toID].remove_connection(connection)

            self.connection_list.remove(connection)

        else:

            warningString = ""
            warningString += "You're trying to delete "
            warningString += str(connection) + " from connection list but "
            warningString += "that connection isn't in the list"

            warnings.warn(warningString)

        self.__reset_IDs(reset_block=False)

    def calculate(self):

        # This methods generate the cost matrix combining the lines returned by each block and then solve it. Before
        # doing so, it invokes the method "__prepare_system" that prepares the system to be solved asking the
        # blocks to generate their own support blocks (if needed) and appending them to the block list.

        if not self.is_ready_for_calculation:

            warning_string = "The system is not ready - calculation not started"
            warnings.warn(warning_string)

        else:

            self.__prepare_system()

            i = 0
            if self.calculate_by_streams:

                n_elements = self.n_conn_matrix

                if n_elements == 0:

                    n_elements = self.n_connection

                self.matrix = np.zeros((n_elements, n_elements))
                self.vector = np.zeros(n_elements)

                for block in self.block_list:

                    block.calculate_by_streams = self.calculate_by_streams

                    sub_matrix = block.get_matrix_row(n_elements)
                    sub_matrix_len = sub_matrix.shape[0]

                    self.vector[i:(i+sub_matrix_len)] = sub_matrix[:, -1]
                    self.matrix[i:(i+sub_matrix_len),:] = sub_matrix[:, 0:-1]
                    i += sub_matrix_len


            else:

                n_elements = self.n_block_matrix

                if n_elements == 0:
                    n_elements = self.n_block

                self.matrix = np.zeros((n_elements, n_elements))
                self.vector = np.zeros(n_elements)

                for block in self.block_list:

                    if not block.has_to_be_skipped:

                        block.calculate_by_streams = self.calculate_by_streams

                        row = block.get_matrix_row(n_elements)

                        self.vector[i] = row[-1]
                        self.matrix[i, :] = row[0:-1]
                        i += 1

            try:

                sol = np.linalg.solve(self.matrix, self.vector)
                self.__append_solution(sol)

            except:

                sol = np.linalg.lstsq(self.matrix, self.vector)
                self.__append_solution(sol[0])

    def find_connection_by_index(self, index):

        for conn in self.connection_list:

            try:

                if conn.index == index:
                    return conn

            except:
                pass

        return None

    def append_excel_costs_and_useful_output(self, input_list, add_useful_output, input_cost):

        for elem in input_list:

            new_conn = self.find_connection_by_index(elem)

            if not new_conn is None:

                if add_useful_output:
                    new_conn.is_useful_effect = True

                else:
                    new_conn.relCost = input_cost

            # Overloaded Methods

    @property
    def useful_effect_connections(self):

        return_list = list()

        for conn in self.connection_list:

            if conn.is_useful_effect:
                return_list.append(conn)

        return return_list

    # support methods
    def import_correct_sub_class(self, subclass_name):

        return self.modules_handler.import_correct_sub_class(subclass_name)

    @property
    def is_ready_for_calculation(self):

        for block in self.block_list:

            if not block.is_ready_for_calculation:
                return False

        return True

    @property
    def there_are_block_to_be_skipped(self):

        for block in self.block_list:

            if block.has_to_be_skipped:
                return True

        return False

    def __reset_IDs(self, reset_block=True):

        if reset_block:

            elem_list = self.block_list

        else:

            elem_list = self.connection_list

        i = 0
        elem_list.sort()

        for elem in elem_list:
            elem.modify_ID(i)
            i += 1

        self.n_block = len(self.block_list)
        self.n_connection = len(self.connection_list)

    def __update_block_list(self):

        # this method asks the blocks to generate their own support blocks (if needed) and appends them to the
        # block list. Finally it orders the lists and reset the IDs.

        for block in self.block_list:

            if block.has_support_block:
                block_list = block.support_block
                self.append_block(block_list)

        self.__reset_IDs(reset_block=True)

    def __prepare_system(self):

        # this method has to be called just before the calculation, it asks the blocks to prepare themselves for the
        # calculation

        self.__update_block_list()

        for block in self.block_list:
            block.prepare_for_calculation()

        if self.there_are_block_to_be_skipped:

            self.calculate_by_streams = True
            self.__move_skipped_element_at_the_end()

    def __append_solution(self, sol):

        i = 0

        if self.calculate_by_streams:

            for conn in self.connection_list:

                if not conn.has_to_be_skipped:
                    conn.set_cost(sol[i])
                    i += 1

        else:

            for block in self.block_list:

                if not block.has_to_be_skipped:

                    block.append_output_cost(sol[i])
                    i += 1

                else:

                    block.append_output_cost(0.)

        self.__reset_IDs(reset_block=True)
        self.__reset_IDs(reset_block=False)

    def __try_append_connection(self, new_conn, block_input, is_input):

        if not block_input is None:

            if issubclass(type(block_input), Block) or type(block_input) is Block:

                block_input.add_connection(new_conn, is_input=is_input)

            else:

                try:

                    self.block_list[int(block_input)].add_connection(new_conn, is_input=is_input)

                except:

                    warningString = ""
                    warningString += str(block_input) + " is not an accepted input"
                    warnings.warn(warningString)

    def __move_skipped_element_at_the_end(self):

        self.n_block_matrix = 0
        self.n_conn_matrix  = 0

        for block in self.block_list:

            block.move_skipped_block_at_the_end = True

            if not block.has_to_be_skipped:
                self.n_block_matrix += 1

        for conn in self.connection_list:

            conn.sort_by_index = False

            if not conn.has_to_be_skipped:
                self.n_conn_matrix += 1

        self.__reset_IDs(reset_block=True)
        self.__reset_IDs(reset_block=False)

        for conn in self.connection_list:
            conn.sort_by_index = True

        for block in self.block_list:
            block.move_skipped_block_at_the_end = False

    def __str__(self):

        # enables printing and str() method
        # e.g. str(ArrayHandler1) will result in:
        #
        # "Array Handler with 2 blocks and 5 connections
        #
        # blocks:
        #       Block (ID: 0, name: Expander 1)
        #       Block (ID: 1, name: Compressor 1)"
        #
        # connections:
        #       Connection (ID: 0, name: a, from: -1, to: 0)
        #       Connection (ID: 1, name: b, from: -1, to: 1)
        #       Connection (ID: 2, name: c, from: 1, to: 0)
        #       Connection (ID: 3, name: d, from: 0, to: -1)
        #       Connection (ID: 4, name: e, from: 0, to: -1)"

        string2_print = "Array Handler with "

        if self.n_block == 0:
            string2_print += "No Blocks"

        elif self.n_block == 1:
            string2_print += "1 Block"

        else:
            string2_print += str(self.n_block) + " Blocks"

        string2_print += " and "

        if self.n_connection == 0:
            string2_print += "No Connections"

        elif self.n_connection == 1:
            string2_print += "1 Connection"

        else:
            string2_print += str(self.n_connection) + " Connections"

        if self.n_block > 0:
            string2_print += "\n\nBlocks:"

            for block in self.block_list:
                if not block.is_support_block:
                    string2_print += "\n" + "\t" + "\t" + str(block)

        if self.n_connection > 0:
            string2_print += "\n\nConnections:"

            for conn in self.connection_list:

                if not conn.is_internal_stream:
                    string2_print += "\n" + "\t" + "\t" + str(conn)

        string2_print += "\n" + "\n"

        return string2_print

    def __repr__(self):

        # enables simple representation
        # e.g. BlockList1 will result in:
        #
        # "Array Handler with 2 blocks and 5 connections
        #
        # blocks:
        #       Block (ID: 0, name: Expander 1)
        #       Block (ID: 1, name: Compressor 1)"
        #
        # connections:
        #       Connection (ID: 0, name: a, from: -1, to: 0)
        #       Connection (ID: 1, name: b, from: -1, to: 1)
        #       Connection (ID: 2, name: c, from: 1, to: 0)
        #       Connection (ID: 3, name: d, from: 0, to: -1)
        #       Connection (ID: 4, name: e, from: 0, to: -1)"

        return str(self)