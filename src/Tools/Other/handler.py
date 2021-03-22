import importlib, inspect
from src import costants


class Handler:

    """This is the base class for classes that have to handle a group of subclasses collected in a specific folder:

            - Import_correct_sub_class method return the correct subclass element from a given name
            - Other methods are related with handling of the format for module and class names

        !!!ATTENTION!!! In creating the sub-classes the user must care to overload:

            - "self.data_folder" variable with the path to the folder containing the subclasses (e.g.
            "src\BlockSubClasses")

            - "self.subclass_directory_path" variable variable with the path to the folder containing the subclasses
            using dots as separators ( e.g. "src.BlockSubClasses") """

    def __init__(self):

        self.current_folder = costants.ROOT_DIR
        self.data_folder = self.current_folder

        self.__subclass_directory_path = ""
        self.__subclass_folder_path = ""

    @property
    def subclass_directory_path(self):

        return self.__subclass_directory_path

    @subclass_directory_path.setter
    def subclass_directory_path(self, input_path):

        self.__subclass_directory_path = input_path
        self.__subclass_folder_path = input_path + "."

    def import_correct_sub_class(self, subclass_name):

        """This method import the correct block subclass.

        Subclasses modules must be placed inside "src.BlockSubClasses" Package. Subclasses
        name must be capitalized. In addition, subclass module name must be the same but without capital letters e.g
        subClasses "Expander" must be in module "expander". The static function called "__get_subclass_module_names"
        generates from "subclass_name" the correct "__module_name" and "__subclass_name" """

        __tmp_result = self.__get_subclass_module_names(subclass_name)
        __module_name = __tmp_result[0]
        __subclass_name = __tmp_result[1]

        __importString = self.__subclass_folder_path + __module_name
        __blockModule = importlib.import_module(__importString)
        return getattr(__blockModule, __subclass_name)

    def get_module_name(self, std_name: str):

        return self.__get_subclass_module_names(std_name)[0]

    def check_data_folder(self):
        pass

    def list_modules(self) -> list:

        raw_names = self.__get_raw_names()

        for i in range(len(raw_names)):

            name = raw_names[i]

            if "_" in name:

                __tmp_list = name.split("_")
                new_name = __tmp_list[0].capitalize()

                for __tmp_array in __tmp_list[1:]:
                    new_name += " " + __tmp_array.capitalize()

            else:

                new_name = name.capitalize()

            raw_names[i] = new_name

        return raw_names

    def __get_raw_names(self) -> list:

        member_list = list()
        __members = inspect.getmembers(importlib.import_module(self.__subclass_directory_path))

        for __member in __members:

            if "__" not in __member[0] and __member[0].islower():
                member_list.append(__member[0])

        return member_list

    @staticmethod
    def get_std_name(input_name: str):

        # This method performs the reverse operation with respect to "__get_subclass_module_names" module.
        # "input_name" could have two format:
        #
        # "__module_name" format:
        #
        #       - in case of multi-word names (e.g. "Heat Exchanger") the words is connected by an underscore ("_")
        #       - each word must be lowercase
        #       - for example: "Heat Exchanger" -> "heat_exchanger"
        #
        # "__subclass_name" format:
        #
        #       - in case of multi-word names (e.g. "Heat Exchanger") the space is removed
        #       - each word must be capitalized
        #       - for example: "Heat Exchanger" -> "HeatExchanger"
        #
        # The method returns the name in the standard format:
        #
        #       - in case of multi-word names (e.g. "Heat Exchanger") the words are separeted by a space (" ")
        #       - each word must be capitalized
        #       - for example: "heat_exchanger" -> "Heat Exchanger"
        #
        # Whatever the input format the program scrolls the string searching for "_" or for uppercase letters:
        #
        #       - if "_" is found, it is replaced with a space " "
        #       - if an uppercase letter is found, a space " " is inserted in the string before the letter.
        #       - otherwise the letter is simply copied into "__std_name" string

        __name_index = list(input_name)
        __std_name = str(__name_index[0]).capitalize()
        capitalize_next = False

        for letter in __name_index[1:]:

            if letter == "_":

                __std_name += " "
                capitalize_next = True

            elif letter.isupper():

                __std_name += " " + str(letter)

            else:

                if capitalize_next:
                    __std_name += str(letter).capitalize()
                    capitalize_next = False

                else:
                    __std_name += str(letter)

        return __std_name

    @staticmethod
    def __get_subclass_module_names(input_name: str):

        # this method generates from "input_name" the correct "__module_name" and "__subclass_name".
        #
        # "__module_name" must have the following format:
        #
        #       - in case of multi-word names (e.g. "Heat Exchanger") the words must be connected by an underscore ("_")
        #       - each word must be lowercase
        #       - for example: "Heat Exchanger" -> "heat_exchanger"
        #
        # "__subclass_name" must have the following format:
        #
        #       - in case of multi-word names (e.g. "Heat Exchanger") the space must be removed
        #       - each word must be capitalized
        #       - for example: "Heat Exchanger" -> "HeatExchanger"

        __tmp_list = input_name.split(" ")

        if len(__tmp_list) == 1:

            __module_name = input_name.lower()
            __subclass_name = input_name.lower().capitalize()

        else:

            __module_name = __tmp_list[0].lower()
            __subclass_name = __tmp_list[0].lower().capitalize()

            for string in __tmp_list[1:]:
                __module_name += "_" + string.lower()
                __subclass_name += string.lower().capitalize()

        return [__module_name.strip(), __subclass_name]