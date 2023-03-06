from EEETools.MainModules import ArrayHandler


def update_exergy_values(array_handler: ArrayHandler, exergy_list: list) -> ArrayHandler:
    """
    :param array_handler: an array_handler
    :param exergy_list: a list of dictionaries having the following keys:
        "index" -> stream index as defined in the array_handler
        "value" -> exergy value for the specified stream in [kW]
    :return: the updated array handler

    """
    for stream in exergy_list:
        connection = array_handler.find_connection_by_index(stream["index"])
        connection.exergy_value = stream["value"]

    return array_handler


def get_result_data_frames(array_handler: ArrayHandler) -> dict:

    if array_handler.options.calculate_component_decomposition:

        return {

            "Stream Out": __get_stream_data_frame(array_handler),
            "Comp Out": __get_comp_data_frame(array_handler),
            "Cost Dec Out": __get_cost_dec_data_frame(array_handler),
            "Eff Out": __get_useful_data_frame(array_handler)

        }

    else:

        return {

            "Stream Out": __get_stream_data_frame(array_handler),
            "Comp Out": __get_comp_data_frame(array_handler),
            "Eff Out": __get_useful_data_frame(array_handler)

        }


def get_debug_data_frames(array_handler: ArrayHandler) -> dict:

    if not array_handler.options.calculate_on_pf_diagram:

        return {

            "Main Matrix": __get_main_matrix_data_frame(array_handler),
            "Connections List": __get_connections_list_data_frame(array_handler)

        }

    else:

        return {

            "Debug - Matrix": __get_main_matrix_data_frame(array_handler),
            "Debug - Block": __get_block_list_data_frame(array_handler),
            "Debug - Connections": __get_connections_list_data_frame(array_handler)

        }


def __get_stream_data_frame(array_handler: ArrayHandler):

    stream_data = {

        "Stream": list(),
        "Name": list(),
        "Exergy Value [kW]": list(),
        "Specific Cost [€/kJ]": list(),
        "Specific Cost [€/kWh]": list(),
        "Total Cost [€/s]": list()

    }

    for conn in array_handler.connection_list:

        if not conn.is_internal_stream:

            stream_data["Stream"].append(conn.index)
            stream_data["Name"].append(conn.name)
            stream_data["Exergy Value [kW]"].append(conn.exergy_value)
            stream_data["Specific Cost [€/kJ]"].append(conn.rel_cost)
            stream_data["Specific Cost [€/kWh]"].append(conn.rel_cost * 3600)
            stream_data["Total Cost [€/s]"].append(conn.rel_cost * conn.exergy_value)

    return stream_data


def __get_comp_data_frame(array_handler: ArrayHandler):

    comp_data = {

        "Name": list(),
        "Comp Cost [€/s]": list(),

        "Exergy_fuel [kW]": list(),
        "Exergy_product [kW]": list(),
        "Exergy_destruction [kW]": list(),
        "Exergy_loss [kW]": list(),
        "Exergy_dl [kW]": list(),

        "Fuel Cost [€/kWh]": list(),
        "Fuel Cost [€/s]": list(),
        "Product Cost [€/kWh]": list(),
        "Product Cost [€/s]": list(),
        "Destruction Cost [€/kWh]": list(),
        "Destruction Cost [€/s]": list(),

        "eta": list(),
        "r": list(),
        "f": list(),
        "y": list()

    }

    block_list = array_handler.blocks_by_index
    for block in block_list:

        if not block.is_support_block:

            comp_data["Name"].append(block.name)
            comp_data["Comp Cost [€/s]"].append(block.comp_cost)

            comp_data["Exergy_fuel [kW]"].append(block.exergy_analysis["fuel"])
            comp_data["Exergy_product [kW]"].append(block.exergy_analysis["product"])
            comp_data["Exergy_destruction [kW]"].append(block.exergy_analysis["distruction"])
            comp_data["Exergy_loss [kW]"].append(block.exergy_analysis["losses"])
            comp_data["Exergy_dl [kW]"].append(block.exergy_analysis["distruction"] + block.exergy_analysis["losses"])

            try:

                comp_data["Fuel Cost [€/kWh]"].append(block.coefficients["c_fuel"] * 3600)
                comp_data["Product Cost [€/kWh]"].append(block.output_cost * 3600)
                comp_data["Destruction Cost [€/kWh]"].append(block.coefficients["c_dest"] * 3600)

                comp_data["Fuel Cost [€/s]"].append(block.coefficients["c_fuel"] * block.exergy_analysis["fuel"])
                comp_data["Product Cost [€/s]"].append(block.output_cost * block.exergy_analysis["product"])
                comp_data["Destruction Cost [€/s]"].append(

                    block.coefficients["c_dest"] * (
                            block.exergy_analysis["distruction"] + block.exergy_analysis["losses"])

                )

                comp_data["eta"].append(block.coefficients["eta"])
                comp_data["r"].append(block.coefficients["r"])
                comp_data["f"].append(block.coefficients["f"])
                comp_data["y"].append(block.coefficients["y"])

            except:

                comp_data["Fuel Cost [€/kWh]"].append(0)
                comp_data["Product Cost [€/kWh]"].append(0)
                comp_data["Destruction Cost [€/kWh]"].append(0)

                comp_data["Fuel Cost [€/s]"].append(0)
                comp_data["Product Cost [€/s]"].append(0)
                comp_data["Destruction Cost [€/s]"].append(0)

                comp_data["eta"].append(0)
                comp_data["r"].append(0)
                comp_data["f"].append(0)
                comp_data["y"].append(0)

    return comp_data


def __get_cost_dec_data_frame(array_handler: ArrayHandler):

    cost_dec_data = {"Name": list()}
    block_list = array_handler.blocks_by_index

    for block in block_list:

        if not block.is_support_block:

            cost_dec_data["Name"].append(block.name)

            for name in block.output_cost_decomposition.keys():

                if name not in cost_dec_data.keys():

                    cost_dec_data.update({name: list()})

                cost_dec_data[name].append(block.output_cost_decomposition[name])

    return cost_dec_data


def __get_useful_data_frame(array_handler: ArrayHandler):

    useful_data = {

        "Stream": list(),
        "Name": list(),
        "Exergy Value [kW]": list(),
        "Specific Cost [€/kJ]": list(),
        "Specific Cost [€/kWh]": list(),
        "Total Cost [€/s]": list()

    }

    for conn in array_handler.useful_effect_connections:
        useful_data["Stream"].append(conn.index)
        useful_data["Name"].append(conn.name)
        useful_data["Exergy Value [kW]"].append(conn.exergy_value)
        useful_data["Specific Cost [€/kJ]"].append(conn.rel_cost)
        useful_data["Specific Cost [€/kWh]"].append(conn.rel_cost * 3600)
        useful_data["Total Cost [€/s]"].append(conn.rel_cost * conn.exergy_value)

    return useful_data


def __get_main_matrix_data_frame(array_handler: ArrayHandler):

    if array_handler.options.calculate_on_pf_diagram:

        array_handler = array_handler.pf_diagram

    block_list = array_handler.block_list
    useful_data = {"names": list()}

    for block in block_list:

        useful_data.update({"{}-{}".format(block.ID, block.name): list()})

    useful_data.update({"constants": list()})

    for block in block_list:

        useful_data["names"].append("{}-{}".format(block.ID, block.name))
        useful_data["constants"].append(array_handler.vector[block.ID])

        for other_block in block_list:

            key = "{}-{}".format(other_block.ID, other_block.name)
            useful_data[key].append(array_handler.matrix[block.ID][other_block.ID])

    return useful_data


def __get_block_list_data_frame(array_handler: ArrayHandler):

    if array_handler.options.calculate_on_pf_diagram:

        array_handler = array_handler.pf_diagram

    block_list = array_handler.block_list

    max_con_blocks = 0.
    for block in block_list:

        con_blocks = len(block.contained_blocks)
        if con_blocks > max_con_blocks:
            max_con_blocks = con_blocks

    useful_data = {

        "Block ID": list(),
        "Name": list(),
        "Cost [€/s]": list()

    }

    for i in range(max_con_blocks):

        useful_data.update({"{} Cont. Blocks".format(i + 1): list()})

    for block in block_list:

        useful_data["Block ID"].append(block.index)
        useful_data["Name"].append(block.name)
        useful_data["Cost [€/s]"].append(block.comp_cost)

        i = 1
        for cont_block in block.contained_blocks:

            useful_data["{} Cont. Blocks".format(i)].append("{}-{}".format(cont_block.ID, cont_block.name))
            i += 1

    return useful_data


def __get_connections_list_data_frame(array_handler: ArrayHandler):

    if array_handler.options.calculate_on_pf_diagram:

        array_handler = array_handler.pf_diagram

    useful_data = {

        "Stream": list(),
        "Name": list(),
        "From": list(),
        "To": list(),
        "Exergy Value [kW]": list()

    }

    for conn in array_handler.connection_list:

        useful_data["Stream"].append(conn.index)
        useful_data["Name"].append(conn.name)

        if conn.from_block is not None:

            useful_data["From"].append("{}-{}".format(conn.from_block.ID, conn.from_block.name))

        else:

            useful_data["From"].append("-")

        if conn.to_block is not None:

            useful_data["To"].append("{}-{}".format(conn.to_block.ID, conn.to_block.name))

        else:

            useful_data["To"].append("-")

        useful_data["Exergy Value [kW]"].append(conn.exergy_value)

    return useful_data
