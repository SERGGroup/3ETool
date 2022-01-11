from EEETools.MainModules import ArrayHandler


def get_result_data_frames(array_handler: ArrayHandler) -> dict:

    # Stream Solution Data frame generation
    stream_data = {"Stream": list(),
                   "Name": list(),
                   "Exergy Value [kW]": list(),
                   "Specific Cost [€/kJ]": list(),
                   "Specific Cost [€/kWh]": list(),
                   "Total Cost [€/s]": list()}

    for conn in array_handler.connection_list:

        if not conn.is_internal_stream:
            stream_data["Stream"].append(conn.index)
            stream_data["Name"].append(conn.name)
            stream_data["Exergy Value [kW]"].append(conn.exergy_value)
            stream_data["Specific Cost [€/kJ]"].append(conn.rel_cost)
            stream_data["Specific Cost [€/kWh]"].append(conn.rel_cost * 3600)
            stream_data["Total Cost [€/s]"].append(conn.rel_cost * conn.exergy_value)

    # Components Data frame generation
    comp_data = {"Name": list(),
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
                 "y": list()}

    for block in array_handler.block_list:

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
                comp_data["Product Cost [€/s]"].append(block.output_cost * block.exergy_analysis["fuel"])
                comp_data["Destruction Cost [€/s]"].append(
                    block.coefficients["c_dest"] * (block.exergy_analysis["distruction"] + block.exergy_analysis["losses"]))

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

    # Output Stream Data frame generation
    useful_data = {"Stream": list(),
                   "Name": list(),
                   "Exergy Value [kW]": list(),
                   "Specific Cost [€/kJ]": list(),
                   "Specific Cost [€/kWh]": list(),
                   "Total Cost [€/s]": list()}

    for conn in array_handler.useful_effect_connections:

        useful_data["Stream"].append(conn.index)
        useful_data["Name"].append(conn.name)
        useful_data["Exergy Value [kW]"].append(conn.exergy_value)
        useful_data["Specific Cost [€/kJ]"].append(conn.rel_cost)
        useful_data["Specific Cost [€/kWh]"].append(conn.rel_cost * 3600)
        useful_data["Total Cost [€/s]"].append(conn.rel_cost * conn.exergy_value)

    return {"Stream Out": stream_data,
            "Comp Out": comp_data,
            "Eff Out": useful_data}