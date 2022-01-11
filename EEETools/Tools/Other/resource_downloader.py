from google_drive_downloader import GoogleDriveDownloader as gdd
from EEETools.costants import GOOGLE_DRIVE_RES_IDs, ROOT_DIR, RES_DIR
from EEETools.version import VERSION
import os, shutil


def __download_resource_folder(file_position, version, failure_possible):

    if os.path.exists(file_position):

        try:

            shutil.rmtree(file_position)

        except:

            pass

    try:

        gdd.download_file_from_google_drive(

            file_id=GOOGLE_DRIVE_RES_IDs[version],
            dest_path=file_position,
            overwrite=True,
            unzip=True

        )

    except:

        warning_message = "\n\n<----------------- !ERROR! ------------------->\n"
        warning_message += "Unable to download the resources!\n"
        warning_message += "Check your internet connection and retry!\n"

        if not failure_possible:
            raise RuntimeError(warning_message)

        else:
            print(warning_message)


def update_resource_folder(version=VERSION, failure_possible=True):

    file_position = os.path.join(ROOT_DIR, "new_res.zip")

    if not version in GOOGLE_DRIVE_RES_IDs.keys():

        version = list(GOOGLE_DRIVE_RES_IDs.keys())[0]

    if not os.path.isdir(RES_DIR):

        __download_resource_folder(file_position, version, failure_possible=False)

    else:

        __version_file = os.path.join(RES_DIR, "res_version.dat")

        if not os.path.isfile(__version_file):

            __download_resource_folder(file_position, version, failure_possible=failure_possible)

        else:

            with open(__version_file) as file:

                resource_version = str(file.readline()).strip()

            if not (resource_version == version):

                __download_resource_folder(file_position, version, failure_possible=failure_possible)