import os, base64, pyrebase
from EEETools import costants
from cryptography.fernet import Fernet
import xml.etree.ElementTree as ETree


class FernetHandler:

    def __init__(self):

        self.__fernet_key_path = os.path.join(costants.RES_DIR, "Other", "fernet_key.dat")
        self.key = self.__initialize_key_value()

    def __initialize_key_value(self):

        """This method retrieve the cryptographic key stored in 'fernet_key.dat' file. If the key file is not present
        in the local resources, python will try to download it from the firebase storage. If also this last passage
        fails, probably due to a bad internet connection, the application will trow an exception as such key is
        mandatory for the calculations """

        if os.path.isfile(self.__fernet_key_path):

            file = open(self.__fernet_key_path, "rb")
            key = base64.urlsafe_b64encode(file.read())
            file.close()

        else:

            try:
                self.retrieve_key()
                key = self.__initialize_key_value()

            except:

                raise Exception("Unable to reach firebase server, cryptography key can not be retrieved hence the "
                                "application can not be started. Check your internet connection and retry")

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

    def export_key(self):

        firebase = pyrebase.initialize_app(costants.FIREBASE_CONFIG)
        storage = firebase.storage()
        storage.child("res/Other/fernet_key.dat").put(self.__fernet_key_path)

    def retrieve_key(self):

        firebase = pyrebase.initialize_app(costants.FIREBASE_CONFIG)
        storage = firebase.storage()
        storage.child("res/Other/fernet_key.dat").download("", self.__fernet_key_path)