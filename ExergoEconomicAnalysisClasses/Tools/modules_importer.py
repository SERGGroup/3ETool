from datetime import date, datetime
import math
import pandas
import os

from ExergoEconomicAnalysisClasses.MainModules.main_module import ArrayHandler
from ExergoEconomicAnalysisClasses.Tools.Other.fernet_handler import FernetHandler


def calculate_excel(excel_path):

    array_handler = import_excel_input(excel_path)
    array_handler.calculate()
    export_solution_to_excel(excel_path, array_handler)


def calculate_dat(dat_path):

    array_handler = import_dat(dat_path)
    array_handler.calculate()
    write_csv_solution(dat_path, array_handler)


def convert_excel_to_dat(excel_path: str):

    array_handler = import_excel_input(excel_path)

    if ".xlsm" in excel_path:

        dat_path = excel_path.replace(".xlsm", ".dat")

    elif ".xlsx" in excel_path:

        dat_path = excel_path.replace(".xlsx", ".dat")

    else:

        dat_path = excel_path.replace(".xls", ".dat")

    export_dat(dat_path, array_handler)


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

    result_df = get_result_data_frames(array_handler)

    # generation of time stamps for excel sheet name
    today = date.today()
    now = datetime.now()
    today_str = today.strftime("%d %b")
    now_str = now.strftime("%H.%M")

    with pandas.ExcelWriter(excel_path, mode="a") as writer:

        for key in result_df.keys():

            pandas_df = pandas.DataFrame(data=result_df[key])
            pandas_df.to_excel(writer, sheet_name=(key + " - " + today_str + " - " + now_str))


def export_dat(dat_path, array_handler: ArrayHandler):

    fernet = FernetHandler()
    fernet.save_file(dat_path, array_handler.xml)


def import_dat(dat_path) -> ArrayHandler:

    array_handler = ArrayHandler()
    fernet = FernetHandler()
    root = fernet.read_file(dat_path)
    array_handler.xml = root

    return array_handler


def write_csv_solution(dat_path, array_handler):

    result_df = get_result_data_frames(array_handler)

    # generation of time stamps for excel sheet name
    today = date.today()
    now = datetime.now()
    today_str = today.strftime("%d %b")
    now_str = now.strftime("%H.%M")

    dir_path = os.path.dirname(dat_path)

    for key in result_df.keys():

        csv_path = key + " - " + today_str + " - " + now_str + ".csv"
        csv_path = os.path.join(dir_path, csv_path)

        pandas_df = pandas.DataFrame(data=result_df[key])
        pandas_df.to_csv(path_or_buf= csv_path, sep="\t")


def get_result_data_frames(array_handler: ArrayHandler):

    # Stream Solution Data frame generation
    stream_data = {"Stream": list(),
                   "Name": list(),
                   "Exergy Value [kW]": list(),
                   "Specific Cost [Euro/kJ]": list(),
                   "Specific Cost [Euro/kWh]": list(),
                   "Total Cost [Euro/s]": list()}

    for conn in array_handler.connection_list:

        if not conn.is_internal_stream:

            stream_data["Stream"].append(conn.index)
            stream_data["Name"].append(conn.name)
            stream_data["Exergy Value [kW]"].append(conn.exergy_value)
            stream_data["Specific Cost [Euro/kJ]"].append(conn.rel_cost)
            stream_data["Specific Cost [Euro/kWh]"].append(conn.rel_cost*3600)
            stream_data["Total Cost [Euro/s]"].append(conn.rel_cost * conn.exergy_value)

    # Output Stream Data frame generation
    useful_data = {"Stream": list(),
                   "Name": list(),
                   "Exergy Value [kW]": list(),
                   "Specific Cost [Euro/kJ]": list(),
                   "Specific Cost [Euro/kWh]": list(),
                   "Total Cost [Euro/s]": list()}

    for conn in array_handler.useful_effect_connections:

        useful_data["Stream"].append(conn.index)
        useful_data["Name"].append(conn.name)
        useful_data["Exergy Value [kW]"].append(conn.exergy_value)
        useful_data["Specific Cost [Euro/kJ]"].append(conn.rel_cost)
        useful_data["Specific Cost [Euro/kWh]"].append(conn.rel_cost * 3600)
        useful_data["Total Cost [Euro/s]"].append(conn.rel_cost * conn.exergy_value)

    return {"Stream Out": stream_data,
            "Eff Out": useful_data}
