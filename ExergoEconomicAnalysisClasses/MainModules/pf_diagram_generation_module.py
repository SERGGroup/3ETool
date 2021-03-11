from ExergoEconomicAnalysisClasses.MainModules.main_module import Connection, ArrayHandler, Block
from ExergoEconomicAnalysisClasses.BlockSubClasses.generic import Generic


class ProductBlock(Generic):

    def __init__(self, inputID, main_class, base_block: Block):

        super().__init__(inputID, main_class)
        self.base_block = base_block

        self.contained_blocks = [base_block]
        self.contained_connection = list()

    def add_connection(self, new_connection, is_input, append_to_support_block=None):

        super(ProductBlock, self).add_connection(new_connection, is_input, append_to_support_block=append_to_support_block)

        if not is_input:

            self.contained_connection.append(new_connection)

    def append_output_cost(self, defined_steam_cost):

        self.output_cost = defined_steam_cost

        for outConn in self.contained_connection:

            if outConn.is_loss:
                outConn.set_cost(0.)

            else:
                outConn.set_cost(defined_steam_cost)

    def find_product_connections(self):

        for conn in self.base_block.output_connections:
            self.__check_connection(conn)

        self.__set_comp_cost()

    def contains(self, element):

        if "Connection" in str(type(element)) or issubclass(type(element), Connection):

            return element in self.contained_connection

        else:

            return element in self.contained_blocks

    def __check_connection(self, conn):

        if conn.is_system_output:

            self.main_class.generate_product_connection(conn, from_product_block=self)

        else:

            new_block = conn.to_block

            if not self.main_class.contains(new_block):

                if new_block.can_be_removed_in_pf_definition:

                    self.contained_connection.append(conn)
                    self.contained_blocks.append(new_block)

                    for conn in new_block.output_connections:

                        self.__check_connection(conn)

                else:

                    self.main_class.generate_product_block(new_block, input_connection=conn, from_block=self)

            else:

                self.main_class.generate_product_connection(conn, from_product_block=self, to_product_block=self.main_class.find_element(new_block))

    def __set_comp_cost(self):

        self.comp_cost = 0

        for block in self.contained_blocks:
            self.comp_cost += block.comp_cost


class ProductConnection(Connection):

    def __init__(self, base_connection: Connection):

        super().__init__(base_connection.ID)

        self.base_connection = base_connection

        self.exergy_value = base_connection.exergy_value
        self.relCost = base_connection.relCost

        self.is_useful_effect = base_connection.is_useful_effect
        self.is_fluid_stream = base_connection.is_fluid_stream


class PFArrayHandler(ArrayHandler):

    def __init__(self, base_array_handler: ArrayHandler):

        super().__init__()
        self.base_array_handler = base_array_handler
        self.__generate_lists()

    def __generate_lists(self):

        for connection in self.base_array_handler.system_inputs:

            new_block = connection.to_block
            self.generate_product_block(new_block, input_connection=connection)

    def generate_product_connection(self, input_connection: Connection, from_product_block=None, to_product_block=None):

        new_conn = ProductConnection(input_connection)
        self.append_connection(new_conn, from_block=from_product_block, to_block=to_product_block)

    def generate_product_block(self, input_block: Block, input_connection=None, from_block = None):

        new_block = self.find_element(input_block)

        if new_block is None:

            new_block = self.__append_new_product_block(input_block, input_connection, from_block)
            new_block.find_product_connections()

        elif input_connection is not None:

            self.generate_product_connection(input_connection, to_product_block=new_block, from_product_block=from_block)

    def __append_new_product_block(self, input_block: Block, input_connection, from_block) -> ProductBlock:

        new_block = ProductBlock(self.n_block, self, input_block)
        self.append_block(new_block)

        if input_connection is not None:
            self.generate_product_connection(input_connection, to_product_block=new_block, from_product_block=from_block)

        return new_block

    def find_element(self, element):

        for prod_block in self.block_list:

            if prod_block.contains(element):
                return prod_block

        return None

    def contains(self, element):

        return self.find_element(element) is not None
