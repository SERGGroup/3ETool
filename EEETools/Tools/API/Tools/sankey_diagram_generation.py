from EEETools.MainModules.pf_diagram_generation_module import ArrayHandler


class SankeyDiagramOptions:

    def __init__(self):

        self.generate_on_pf_diagram = False
        self.show_component_mixers = False
        self.display_costs = False

        self.colors = {

            "Destruction": [150, 0, 0],
            "Losses": [50, 125, 150],
            "Default": [250, 210, 20],
            "Cost": [40, 170, 60],
            "Components Cost": [110, 200, 255],
            "Redistributed Cost": [255, 200, 110]

        }
        self.opacity = {

            "nodes": 1,
            "links": 0.6,
            "DL_links": 0.25,
            "Components Cost": 0.1,
            "Redistributed Cost": 0.20

        }
        self.min_opacity_perc = 0.05

    def define_color(self, block_label, is_link, cost_perc=1):

        return "rgba({}, {})".format(self.get_color(block_label), self.get_opacity(block_label, is_link, cost_perc))

    def get_color(self, block_label):

        if block_label in ["Destruction", "Losses", "Components Cost", "Redistributed Cost"]:

            color = self.colors[block_label]

        elif block_label == "Redistributed Cost":

            return self.get_color("Destruction")

        else:

            if self.display_costs:

                color = self.colors["Cost"]

            else:

                color = self.colors["Default"]

        return "{}, {}, {}".format(color[0], color[1], color[2])

    def get_opacity(self, block_label, is_link, cost_perc=1):

        if is_link:

            if block_label in ["Destruction", "Losses"]:

                return self.opacity["DL_links"] * cost_perc

            elif block_label in ["Redistributed Cost", "Components Cost"]:

                return self.opacity[block_label] * cost_perc

            return self.opacity["links"] * cost_perc

        else:

            return self.opacity["nodes"] * cost_perc


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

        if self.options.display_costs:

            self.input_array_handler.calculate()

        if self.options.generate_on_pf_diagram:

            self.array_handler = self.input_array_handler.get_pf_diagram()

        else:

            self.array_handler = self.input_array_handler

        if not self.options.display_costs:

            self.array_handler.prepare_system()

        self.__fill_sankey_diagram_dicts()

    def __fill_sankey_diagram_dicts(self):

        for conn in self.array_handler.connection_list:

            from_block_label, to_block_label = self.__get_node_labels_from_connection(conn)

            if not from_block_label == to_block_label:

                self.__update_link_dict(from_block_label, to_block_label, conn.exergy_value, conn=conn)

        if not self.options.display_costs:

            self.__append_destruction()

        else:

            self.__append_redistributed_cost()
            self.__append_components_cost()

    def __update_link_dict(self, from_block_label, to_block_label, value, conn=None):

        self.__check_label(from_block_label)
        self.__check_label(to_block_label)

        self.link_dict["source"].append(self.nodes_dict["label"].index(from_block_label))
        self.link_dict["target"].append(self.nodes_dict["label"].index(to_block_label))

        if not self.options.display_costs:

            self.link_dict["value"].append(value)
            self.link_dict["color"].append(self.options.define_color(to_block_label, is_link=True))

        else:

            if "Redistributed Cost" in [to_block_label, from_block_label]:

                color = self.options.define_color("Redistributed Cost", is_link=True)

            elif "Components Cost" in [to_block_label, from_block_label]:

                color = self.options.define_color("Components Cost", is_link=True)

            else:

                value = conn.abs_cost

                rel_cost = conn.rel_cost
                max_rel_cost = self.__get_maximum_rel_cost()
                perc = rel_cost / max_rel_cost * (1 - self.options.min_opacity_perc) + self.options.min_opacity_perc

                color = self.options.define_color(to_block_label, is_link=True, cost_perc=perc)

            self.link_dict["value"].append(value)
            self.link_dict["color"].append(color)

    def __check_label(self, label):

        if label not in self.nodes_dict["label"]:

            self.nodes_dict["label"].append(label)
            self.nodes_dict["color"].append(self.options.define_color(label, is_link=False))

    def __append_destruction(self):

        for block in self.array_handler.block_list:

            from_block_label = self.__get_node_label(block)
            self.__update_link_dict(from_block_label, "Destruction", block.exergy_balance)

    def __append_redistributed_cost(self):

        for block in self.array_handler.block_list:

            if block.is_dissipative:

                from_block_label = self.__get_node_label(block)
                self.__update_link_dict(from_block_label, "Redistributed Cost", block.difference_cost)

                red_sum = block.redistribution_sum
                for non_dissipative_blocks in block.redistribution_block_list:

                    to_block_label = self.__get_node_label(non_dissipative_blocks)
                    red_perc = round(non_dissipative_blocks.redistribution_index / red_sum, 2)

                    self.__update_link_dict(

                        "Redistributed Cost", to_block_label, block.difference_cost*red_perc

                    )

    def __append_components_cost(self):

        for block in self.array_handler.block_list:

            to_block_label = self.__get_node_label(block)
            self.__update_link_dict("Components Cost", to_block_label, block.comp_cost)

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

    def __get_maximum_rel_cost(self):

        max_rel_cost = 0.
        for conn in self.array_handler.connection_list:

            if not conn.is_loss:

                if conn.rel_cost > max_rel_cost:

                    max_rel_cost = conn.rel_cost

        return max_rel_cost