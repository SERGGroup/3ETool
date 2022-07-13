from EEETools.MainModules.pf_diagram_generation_module import ArrayHandler


class SankeyDiagramOptions:

    def __init__(self):

        self.generate_on_pf_diagram = False
        self.show_component_mixers = False
        self.colors = {

            "Destruction": "150, 0, 0",
            "Losses": "50, 125, 150",
            "Default": "250, 210, 20"

        }
        self.opacity = {

            "nodes": 1,
            "links": 0.6,
            "DL_links": 0.25

        }

    def define_color(self, block_label, is_link):

        return "rgba({}, {})".format(self.get_color(block_label), self.get_opacity(block_label, is_link))

    def get_color(self, block_label):

        if block_label == "Destruction" or block_label == "Losses":

            color = self.colors[block_label]

        else:

            color = self.colors["Default"]

        return color

    def get_opacity(self, block_label, is_link):

        if is_link:

            if block_label == "Destruction" or block_label == "Losses":

                return self.opacity["DL_links"]

            return self.opacity["links"]

        else:

            return self.opacity["nodes"]


class SankeyDiagramGenerator:

    def __init__(self, input_array_handler: ArrayHandler, options: SankeyDiagramOptions = SankeyDiagramOptions()):

        super().__init__()

        self.options = options
        self.input_array_handler = input_array_handler
        self.array_handler = None

    # -------------------------------------
    # ------- Sankey Diagram Methods ------
    # -------------------------------------

    def show(self):

        import plotly.graph_objects as go
        self.__init_sankey_dicts()

        fig = go.Figure(

            data=[

                go.Sankey(

                    arrangement="snap",
                    node=self.nodes_dict,
                    link=self.link_dict

                )

            ]

        )

        fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
        fig.show()

    def __init_sankey_dicts(self):

        self.nodes_dict = {

            "label": list(),
            "color": list()

        }
        self.link_dict = {

            "source": list(),
            "target": list(),
            "value": list(),
            "color": list()

        }

        if self.options.generate_on_pf_diagram:
            self.array_handler = self.input_array_handler.get_pf_diagram()

        else:
            self.array_handler = self.input_array_handler

        self.array_handler.prepare_system()
        self.__fill_sankey_diagram_dicts()

    def __fill_sankey_diagram_dicts(self):

        for conn in self.array_handler.connection_list:

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
        self.link_dict["color"].append(self.options.define_color(to_block_label, is_link=True))

    def __check_label(self, label):

        if label not in self.nodes_dict["label"]:

            self.nodes_dict["label"].append(label)
            self.nodes_dict["color"].append(self.options.define_color(label, is_link=False))

    def __append_destruction(self):

        for block in self.array_handler.block_list:
            from_block_label = self.__get_node_label(block)
            self.__update_link_dict(from_block_label, "Destruction", block.exergy_balance)

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

        if block.is_support_block:

            main_block = block.main_block

            if main_block is not None and not self.options.show_component_mixers:

                return self.__get_node_label(main_block)

            else:

                return "{}".format(block.ID)

        else:

            return "{}".format(block.name)
