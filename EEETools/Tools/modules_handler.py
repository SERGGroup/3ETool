from EEETools.Tools.Other.handler import Handler
from EEETools import costants
import os


class ModulesHandler(Handler):

    def __init__(self):

        super().__init__()

        self.current_folder = os.path.join(costants.ROOT_DIR, "EEETools", "Tools")
        self.subclasses_folder = os.path.join(costants.ROOT_DIR, "EEETools", "BlockSubClasses")
        self.subclass_directory_path = "EEETools.BlockSubClasses"

        self.ignore_subclasses = ["Drawer"]

        self.name_list = self.list_modules()

        self.translationDict = {"Alternatore"                   : "Alternator",
                                "Caldaia"                       : "Boiler",
                                "Camera di Combustione"         : "Combustion Chamber",
                                "Compressore"                   : "Compressor",
                                "Condensatore"                  : "Condenser",
                                "Evaporatore"                   : "Evaporator",
                                "Generico"                      : "Generic",
                                "Ingresso Fuel"                 : "Fuel Input",
                                "Miscelatore"                   : "Mixer",
                                "Pompa"                         : "Pump",
                                "Scambiatore"                   : "Heat Exchanger",
                                "Scambiatore - Multi Fuel"      : "Heat Exchanger",
                                "Scambiatore - Multi Product"   : "Heat Exchanger",
                                "Separatore"                    : "Separator",
                                "Turbina"                       : "Expander",
                                "Uscita Effetto Utile"          : "Usefull Effect",
                                "Valvola Laminazione"           : "Valve"}

    def get_name_index(self, name: str):

        if " " in name:

            __std_name = name

        else:

            __std_name = self.get_std_name(name)

        if __std_name in self.name_list:

            return self.name_list.index(__std_name)

        else:

            return -1

    def check_subclasses_folder(self):

        super().check_subclasses_folder()

        for name in self.name_list:

            folder_name = self.get_module_name(name)
            name_folder_path = os.path.join(self.subclasses_folder, folder_name)

            if not os.path.isdir(name_folder_path):

                try:

                    os.mkdir(name_folder_path)

                except:

                    pass

    def import_correct_sub_class(self, subclass_name):

        try:

            result = super(ModulesHandler, self).import_correct_sub_class(subclass_name)

        except:

            subclass_name = self.__translate_subclass_name(subclass_name)
            result = super(ModulesHandler, self).import_correct_sub_class(subclass_name)

        return result

    def __translate_subclass_name(self, subclass_name):

        if subclass_name in self.translationDict.keys():

            return self.translationDict[subclass_name]

        else:

            return subclass_name

    def get_json_component_description(self) -> list:

        return_list = []
        for module_name in self.raw_name_list:
            return_list.append(self.import_correct_sub_class(module_name).get_json_component_description())

        return return_list


if __name__ == "__main__":

    handler = ModulesHandler()
    input_list = handler.get_json_component_description()
    print(input_list)