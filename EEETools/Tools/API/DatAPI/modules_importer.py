from EEETools.Tools.API.Tools.main_tools import get_result_data_frames
from EEETools.Tools.Other.fernet_handler import FernetHandler
from EEETools.MainModules import ArrayHandler
from datetime import date, datetime
import os, pandas


def calculate_dat(dat_path):

    array_handler = import_dat(dat_path)
    array_handler.calculate()
    write_csv_solution(dat_path, array_handler)


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
        pandas_df.to_csv(path_or_buf=csv_path, sep="\t")