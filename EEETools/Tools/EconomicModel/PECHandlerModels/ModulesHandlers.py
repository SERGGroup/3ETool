from EEETools.Tools.EconomicModel.PECHandlerModels.AbstratClass import AbstractPECHandler
from EEETools.Tools.Other.handler import Handler
import typing as t
import os

class EconomicModulesHandler(Handler):

    """This class handles the economic modules for PEC Handler models.

    It extends the Handler class to manage the economic modules in the specified folder.
    """

    def __init__(self):
        super().__init__()
        self.current_folder = os.path.dirname(__file__)
        self.subclasses_folder = os.path.join(self.current_folder, "subclasses")
        self.subclass_directory_path = "EEETools.Tools.EconomicModel.PECHandlerModels.subclasses"
        self.list_modules()

    def convert_raw_names(self, raw_names:list, class_list:list) -> list:

        names = super().convert_raw_names(raw_names, class_list)
        for i, cls in enumerate(class_list):
            if hasattr(cls, 'get_model_name'):
                names[i] = cls.get_model_name()

        return names

    def init_subclass(self, json_in: t.Any) -> t.Union[AbstractPECHandler, None]:

        """
        Method to set the options for the PEC Handler model.
        This method will be used to set the options from the JSON input.
        :param json_in: JSON input containing the options
        :return: subclass of AbstractPECHandler
        """
        topology_options = json_in.get('options', None)
        if topology_options is None:
            raise ValueError("Topology options not provided in the JSON input.")

        model_name = topology_options.get('economic_model', None)
        model_params = topology_options.get('economic_model_params', {})

        if model_name is None:
            raise ValueError("Model name not provided in the JSON input.")

        pec_handler = None
        for cls in self.classes_list:
            if cls.get_model_name() == model_name:
                pec_handler = cls()
                break
        if pec_handler is not None:
            pec_handler.set_options(model_params)

        return pec_handler

    def get_json_inputs_dict(self) -> dict:

        return_dict = dict()
        for cls in self.classes_list:
            name = cls.get_model_name()
            return_dict.update({name: {

                "is_usable_for_exergo_environment": cls.is_usable_for_exergo_environment(),
                "params": cls.get_JSON_inputs()

            }})
        return return_dict


if __name__ == "__main__":

    handler = EconomicModulesHandler()
    input_list = handler.get_json_inputs_dict()
    print("Economic Modules Handler initialized.")
    print("Available modules:", handler.name_list)
    print("Current folder:", handler.current_folder)
    print("Subclass directory path:", handler.subclass_directory_path)