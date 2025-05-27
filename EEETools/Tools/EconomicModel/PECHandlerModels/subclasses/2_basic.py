from EEETools.Tools.EconomicModel.PECHandlerModels.AbstratClass import AbstractPECHandler
import numpy as np
import typing as t

class BasicModel(AbstractPECHandler):

    lifetime: float = 20.0  # Default lifetime in years
    cf: float = 0.8  # Default capacity factor (80% utilization)
    i_rate: float = 0.05  # Default interest rate (5%)
    om_ratio = 0.02  # Default O&M ratio (2% of capital cost)

    @classmethod
    def is_usable_for_exergo_environment(cls) -> bool:
        return False

    @classmethod
    def get_model_name(cls) -> str:
        return "basic_model"

    def get_cost(self, comp_cost: float) -> float:
        """
            From Ungar et Al. (2024):
            Thermo-economic comparison of CO2 and water as a heat carrier for
            long-distance heat transport from geothermal sources:
             A Bavarian case study
        """
        if self.i_rate == 0:
            # If interest rate is zero, alpha = lifetime (which is lim i_rate->0)
            alpha = self.lifetime
        else:
            alpha = (1 - np.power(1 + self.i_rate, -self.lifetime)) / self.i_rate
        beta = (1 + alpha * self.om_ratio) / (alpha * self.cf * 8760 * 3600)
        return comp_cost * beta

    @classmethod
    def get_JSON_inputs(cls) -> list:
        return [

            {"key": 'lifetime', "label": 'Plant Lifetime [years]', "value": cls.lifetime},
            {"key": 'cf', "label": 'Capacity Factor [%]', "value": cls.cf * 100},
            {"key": 'i_rate', "label": 'Yearly Interest Rate [%]', "value": cls.i_rate* 100},
            {"key": 'om_ratio', "label": 'Yearly Maintenance Ratio [%]', "value": cls.om_ratio * 100}

        ]

    def set_options(self, json_in: t.Any) -> None:
        self.cf = float(json_in.get('cf', self.cf * 100)) / 100  # Convert percentage to decimal
        self.lifetime = float(json_in.get('lifetime', self.lifetime))
        self.i_rate = float(json_in.get('i_rate', self.i_rate * 100)) / 100
        self.om_ratio = float(json_in.get('om_ratio', self.om_ratio * 100)) / 100