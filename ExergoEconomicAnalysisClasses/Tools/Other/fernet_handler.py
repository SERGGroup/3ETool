import os, base64
from res import costants
from cryptography.fernet import Fernet
import xml.etree.ElementTree as ETree


class FernetHandler:

    def __init__(self):

        self.key = self.__initialize_key_value()

    @staticmethod
    def __initialize_key_value():

        __fernet_key_path = os.path.join(costants.ROOT_DIR, "res", "Other", "fernet_key.dat")

        if os.path.isfile(__fernet_key_path):

            file = open(__fernet_key_path, "rb")
            key = base64.urlsafe_b64encode(file.read())
            file.close()

        else:

            key = Fernet.generate_key()

            file = open(__fernet_key_path, "wb")
            file.write(base64.urlsafe_b64decode(key))
            file.close()

        return key

    def read_file(self, file_path):

        # This method retrieve the correlation data from the .dat file. The file must be decrypted in order to access
        # the xml tree containing the data. Xml file format can change for different cost correlation classes but the
        # decryption process remains the same.

        # After the decryption of the data the method reads the name of the correlation class from the xml file and
        # use it to initialize the correct subclass

        file = open(file_path, "rb")
        data = file.read()
        file.close()

        fernet = Fernet(self.key)
        data = fernet.decrypt(data)

        return data

    def save_file(self, file_path, root: ETree.Element):

        # This method save the correlation data to a .dat file containing an encrypted xml tree. Encryption is useful in
        # order to prevent the user from modifying the file manually without going through the editor.
        # Data format can change for different cost correlation classes but the encryption process remains the same.

        str_data = ETree.tostring(root)

        fernet = Fernet(self.key)
        str_data = fernet.encrypt(str_data)

        xml_file = open(file_path, "wb")
        xml_file.write(str_data)
        xml_file.close()