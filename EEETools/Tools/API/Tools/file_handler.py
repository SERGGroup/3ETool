from EEETools.costants import RES_DIR
import os


def get_file_position(file_name):

    file_position = os.path.join(RES_DIR, "Other", file_name)

    if not os.path.isfile(file_position):

        try:

            from EEETools.Tools.Other.resource_downloader import update_resource_folder
            update_resource_folder()

        except:

            return ""

    return file_position