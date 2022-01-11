from EEETools.Tools.Other.resource_downloader import update_resource_folder
from cryptography.fernet import Fernet
from EEETools import costants

import xml.etree.ElementTree as ETree
import os, base64


class FernetHandler:

    def __init__(self):

        self.__fernet_key_path = os.path.join(costants.RES_DIR, "Other", "fernet_key.dat")
        self.key = self.__initialize_key_value()

    def __initialize_key_value(self, retrieve_if_necessary=True):

        """This method retrieve the cryptographic key stored in 'fernet_key.dat' file. If the key file is not present
        in the local resources, python will try to download it from the firebase storage. If also this last passage
        fails, probably due to a bad internet connection, the application will trow an exception as such key is
        mandatory for the calculations """

        if os.path.isfile(self.__fernet_key_path):

            file = open(self.__fernet_key_path, "rb")
            key = base64.urlsafe_b64encode(file.read())
            file.close()

        elif retrieve_if_necessary:

            try:

                update_resource_folder()
                key = self.__initialize_key_value(retrieve_if_necessary=False)

            except:

                raise Exception(

                    "Unable to reach resources, cryptography key can not be retrieved hence the "
                    "application can not be started. Check your internet connection and retry"

                )

        else:

            raise Exception(

                "Unable to find resources, cryptography key can not be retrieved hence the "
                "application can not be started. Check your internet connection and retry"

            )

        return key

    def read_file(self, file_path):

        """ This method retrieve the data from the .dat file and convert it back to the original unencrypted xml.
            The method return an xml tree initialized according to the stored data"""

        file = open(file_path, "rb")
        data = file.read()
        file.close()

        fernet = Fernet(self.key)
        data = fernet.decrypt(data)

        return ETree.fromstring(data)

    def save_file(self, file_path, root: ETree.Element):

        """ This method encrypted and save the input xml tree in a .dat file. Encryption is used to prevent users
        from modifying the file manually without going through the editor. """

        str_data = ETree.tostring(root)

        fernet = Fernet(self.key)
        str_data = fernet.encrypt(str_data)

        xml_file = open(file_path, "wb")
        xml_file.write(str_data)
        xml_file.close()