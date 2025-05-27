from EEETools.Tools.EconomicModel.PECHandlerModels.AbstratClass import AbstractPECHandler
import typing as t

class NoModel(AbstractPECHandler):

    @classmethod
    def is_usable_for_exergo_environment(cls) -> bool:
        return True

    @classmethod
    def get_model_name(cls) -> str:
        return "no_model"

    def get_cost(self, comp_cost: float) -> float:
        return comp_cost

    @classmethod
    def get_JSON_inputs(cls) -> list:
        return []

    def set_options(self, json_in: t.Any) -> None:
        pass