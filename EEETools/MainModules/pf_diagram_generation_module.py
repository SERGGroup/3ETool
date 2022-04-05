import warnings

from EEETools.MainModules.main_module import Connection, ArrayHandler, Block
from EEETools.BlockSubClasses.generic import Generic


class ProductBlock(Generic):

    def __init__(self, inputID, main_class, base_block: Block):

        super().__init__(inputID, main_class)

        self.base_block = base_block
        self.name = base_block.name
        self.contained_blocks = [base_block]
        self.contained_connection = list()

    def add_connection(self, new_connection, is_input, append_to_support_block=None):

        super(ProductBlock, self).add_connection(new_connection, is_input,
                                                 append_to_support_block=append_to_support_block)

        if not is_input:
            self.contained_connection.append(new_connection)

    def append_output_cost(self, defined_steam_cost):

        self.output_cost = defined_steam_cost
        self.base_block.output_cost = defined_steam_cost

        for outConn in self.contained_connection:

            if outConn.is_loss:
                outConn.set_cost(0.)

            else:
                outConn.set_cost(defined_steam_cost)

    def generate_output_cost_decomposition(self, inverse_matrix_row):

        super(ProductBlock, self).generate_output_cost_decomposition(inverse_matrix_row)

        for block in self.contained_blocks:
            block.output_cost_decomposition = self.output_cost_decomposition

    def find_product_connections(self):

        for conn in self.base_block.output_connections:
            self.__check_connection(conn)

        self.__set_comp_cost()

    def contains(self, element):

        if "Connection" in str(type(element)) or issubclass(type(element), Connection):

            return element in self.contained_connection

        else:

            return element in self.contained_blocks

    def calculate_coefficients(self, total_destruction):

        super(ProductBlock, self).calculate_coefficients(total_destruction)

        self.base_block.coefficients = self.coefficients
        self.base_block.exergy_analysis = self.exergy_analysis

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

                self.main_class.generate_product_connection(conn, from_product_block=self,
                                                            to_product_block=self.main_class.find_element(new_block))

    def __set_comp_cost(self):

        self.comp_cost = 0

        for block in self.contained_blocks:
            self.comp_cost += block.comp_cost

    def this_has_higher_skipping_order(self, other):

        return None

    def this_has_higher_support_block_order(self, this, other):

        return None


class ProductConnection(Connection):

    def __init__(self, base_connection: Connection):
        super().__init__(base_connection.ID)

        self.base_connection = base_connection
        self.name = self.base_connection.name

        self.exergy_value = base_connection.exergy_value
        self.rel_cost = base_connection.rel_cost

        self.is_useful_effect = base_connection.is_useful_effect
        self.is_fluid_stream = base_connection.is_fluid_stream

    @property
    def rel_cost(self) -> float:
        return self.__rel_cost

    @rel_cost.setter
    def rel_cost(self, rel_cost_input):
        self.__rel_cost = rel_cost_input
        self.base_connection.rel_cost = rel_cost_input


class PFArrayHandler(ArrayHandler):

    # -------------------------------------
    # ------ Initialization  Methods ------
    # -------------------------------------

    def __init__(self, base_array_handler: ArrayHandler):

        super().__init__()
        self.base_array_handler = base_array_handler
        self.__generate_lists()
        self.__identify_support_blocks()

    def __generate_lists(self):

        for connection in self.base_array_handler.system_inputs:

            new_block = connection.to_block
            self.generate_product_block(new_block, input_connection=connection)

    def __identify_support_blocks(self):

        for prod_block in self.block_list:

            if prod_block.base_block.is_support_block:
                prod_block.is_support_block = True
                prod_block.main_block = self.find_element(prod_block.base_block.main_block)

    def generate_product_connection(self, input_connection: Connection, from_product_block=None, to_product_block=None):

        new_conn = ProductConnection(input_connection)
        self.append_connection(new_conn, from_block=from_product_block, to_block=to_product_block)

    def generate_product_block(self, input_block: Block, input_connection=None, from_block=None):

        new_block = self.find_element(input_block)

        if new_block is None:

            new_block = self.__append_new_product_block(input_block, input_connection, from_block)
            new_block.find_product_connections()

        elif input_connection is not None:

            self.generate_product_connection(input_connection, to_product_block=new_block,
                                             from_product_block=from_block)

    def __append_new_product_block(self, input_block: Block, input_connection, from_block) -> ProductBlock:

        new_block = ProductBlock(self.n_block, self, input_block)
        self.append_block(new_block)

        if input_connection is not None:
            self.generate_product_connection(input_connection, to_product_block=new_block,
                                             from_product_block=from_block)

        return new_block

    # -------------------------------------
    # ---------- Support Methods ----------
    # -------------------------------------

    def find_element(self, element):

        for prod_block in self.block_list:

            if prod_block.contains(element):
                return prod_block

        return None

    def contains(self, element):

        return self.find_element(element) is not None

    # -------------------------------------
    # ------- Sankey Diagram Methods ------
    # -------------------------------------

    def sankey_diagram_data(self, show_component_mixers=False):

        self.show_component_mixers = show_component_mixers
        self.__init_sankey_dicts()

        return {

            "nodes": self.nodes_dict,
            "links": self.link_dict
        }

    def __init_sankey_dicts(self):

        self.nodes_dict = {

            "label": list(),
            "groups": list()

        }
        self.link_dict = {

            "source": list(),
            "target": list(),
            "value": list()

        }

        self.__fill_sankey_diagram_dicts()

    def __fill_sankey_diagram_dicts(self):

        for conn in self.connection_list:

            from_block_label, to_block_label = self.__get_node_labels_from_connection(conn)
            if not from_block_label == to_block_label:
                self.__update_link_dict(from_block_label, to_block_label, conn.exergy_value)

        self.__append_destruction()

    def __update_link_dict(self, from_block_label, to_block_label, exergy_value):

        self.__check_label(from_block_label)
        self.__check_label(to_block_label)

        self.link_dict["source"].append(self.nodes_dict["label"].index(from_block_label))
        self.link_dict["target"].append(self.nodes_dict["label"].index(to_block_label))
        self.link_dict["value"].append(exergy_value)

    def __check_label(self, label):

        if label not in self.nodes_dict["label"]:
            self.nodes_dict["label"].append(label)

    def __append_destruction(self):

        for block in self.block_list:

            from_block_label = self.__get_node_label(block)
            self.__update_link_dict(from_block_label, "Destruction", block.exergy_balance)

    def __define_support_block_groups(self):

        for block in self.block_list:

            if block.base_block.is_support_block:

                main_block = self.find_element(block.base_block.main_block)

                if main_block is not None:

                    support_block_index = self.nodes_dict["label"].index(self.__get_node_label(block))
                    main_block_index = self.nodes_dict["label"].index(self.__get_node_label(main_block))
                    self.nodes_dict["groups"].append([support_block_index, main_block_index])

    def __get_node_labels_from_connection(self, conn):

        if conn.is_system_output:

            from_block_label = self.__get_node_label(conn.from_block)

            if conn.is_loss:
                to_block_label = "Losses"

            else:
                to_block_label = conn.name

        elif conn.is_system_input:

            from_block_label = conn.name
            to_block_label = self.__get_node_label(conn.to_block)

        else:

            from_block_label = self.__get_node_label(conn.from_block)
            to_block_label = self.__get_node_label(conn.to_block)

        return from_block_label, to_block_label

    def __get_node_label(self, block):

        if block.base_block.is_support_block:

            main_block = self.find_element(block.base_block.main_block)

            if main_block is not None and not self.show_component_mixers:

                return self.__get_node_label(main_block)

            else:

                return "{}".format(block.ID)

        else:

            return "{}-{}".format(block.ID, block.name)