from EEETools.Tools.EconomicModel.PECHandlerModels.AbstratClass import AbstractPECHandler
import typing as t


class IgnoreDiscountRate(AbstractPECHandler):

    lifetime: float = 20.0  # Default lifetime in years
    cf: float = 0.8  # Default capacity factor (80% utilization)

    @classmethod
    def is_usable_for_exergo_environment(cls) -> bool:
        return True

    @classmethod
    def get_model_name(cls) -> str:
        return "ignore_discount_rate"

    def get_cost(self, comp_cost: float) -> float:
        return comp_cost / (self.lifetime * self.cf * 8760 * 3600)  # Convert cost to €/s assuming lifetime in years

    @classmethod
    def get_JSON_inputs(cls) -> list:
        return [

            { "key": 'lifetime', "label": 'Plant Lifetime [years]', "value": cls.lifetime},
            {"key": 'cf', "label": 'Capacity Factor [%]', "value": cls.cf * 100}

        ]

    def set_options(self, json_in: t.Any) -> None:
        self.cf = float(json_in.get('cf', self.cf * 100)) / 100  # Convert percentage to decimal
        self.lifetime = float(json_in.get('lifetime', self.lifetime))
