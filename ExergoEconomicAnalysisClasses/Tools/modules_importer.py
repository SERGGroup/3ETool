from ExergoEconomicAnalysisClasses.Tools.Other.matrix_analyzer import MatrixAnalyzer
from datetime import date, datetime
import pandas, math

from ExergoEconomicAnalysisClasses.MainModules.main_module import ArrayHandler


def import_excel_input(excel_path) -> ArrayHandler:

    array_handler = ArrayHandler()

    # import connections
    excel_connection_data = pandas.read_excel(excel_path, sheet_name="Stream")

    for line in excel_connection_data.values:

        line = line.tolist()
        if not math.isnan(line[0]):
            new_conn = array_handler.append_connection()

            new_conn.index = line[0]
            new_conn.name = str(line[1])
            new_conn.exergy_value = line[2]

    # import blocks
    excel_block_data = pandas.read_excel(excel_path, sheet_name="Componenti")

    for line in excel_block_data.values:

        line = line.tolist()

        if not (math.isnan(line[0]) or type(line[0]) is str):

            if line[0] > 0:

                if "Heat Exchanger" in str(line[2]) or "Scambiatore" in str(line[2]):

                    new_block = array_handler.append_block("Heat Exchanger")
                    excel_connection_list = list()
                    excel_connection_list.append(str(line[2]))
                    excel_connection_list.extend(line[5:-1])

                else:

                    new_block = array_handler.append_block(str(line[2]))
                    excel_connection_list = line[5:-1]

                new_block.index = line[0]
                new_block.name = str(line[1])
                new_block.comp_cost = line[3]

                new_block.append_excel_connection_list(excel_connection_list)

            else:

                array_handler.append_excel_costs_and_useful_output(line[5:-1], line[0] == 0, line[3])

    return array_handler


def export_solution_to_excel(excel_path, array_handler: ArrayHandler):

    #Stream Solution Data frame generation
    stream_data = { "Stream"                    : list(),
                    "Name"                      : list(),
                    "Exergy Value [kW]"         : list(),
                    "Specific Cost [Euro/kJ]"   : list(),
                    "Total Cost [Euro/s]"       : list()}

    for conn in array_handler.connection_list:

        if not conn.is_internal_stream:

            stream_data["Stream"].append(conn.index)
            stream_data["Name"].append(conn.name)
            stream_data["Exergy Value [kW]"].append(conn.exergy_value)
            stream_data["Specific Cost [Euro/kJ]"].append(conn.relCost)
            stream_data["Total Cost [Euro/s]"].append(conn.relCost*conn.exergy_value)

    stream_df = pandas.DataFrame(data = stream_data)

    # Output Stream Data frame generation
    usefull_data = {"Stream": list(),
                    "Name": list(),
                    "Exergy Value [kW]": list(),
                    "Specific Cost [Euro/kJ]": list(),
                    "Total Cost [Euro/s]": list()}

    for conn in array_handler.useful_effect_connections:

        usefull_data["Stream"].append(conn.index)
        usefull_data["Name"].append(conn.name)
        usefull_data["Exergy Value [kW]"].append(conn.exergy_value)
        usefull_data["Specific Cost [Euro/kJ]"].append(conn.relCost)
        usefull_data["Total Cost [Euro/s]"].append(conn.relCost * conn.exergy_value)

    usefull_df = pandas.DataFrame(data = usefull_data)

    # generation of time stamps for excel sheet name
    today = date.today()
    now = datetime.now()
    today_str = today.strftime("%d %b")
    now_str = now.strftime("%H.%M")

    with pandas.ExcelWriter(excel_path, mode="a") as writer:

        stream_df.to_excel(writer, sheet_name=("Stream Out" + " - " + today_str + " - " + now_str))
        usefull_df.to_excel(writer, sheet_name=("Eff Out" + " - " + today_str + " - " + now_str))


def calculate_excel(excel_path):

    array_handler = import_excel_input(excel_path)
    array_handler.calculate()

    analyzer = MatrixAnalyzer(array_handler.matrix)
    analyzer.solve(array_handler.vector)

    export_solution_to_excel(excel_path, array_handler)