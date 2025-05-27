from EEETools.Tools.EconomicModel.PECHandlerModels.AbstratClass import AbstractPECHandler
import numpy as np
import typing as t

class ManfridaModel(AbstractPECHandler):

    lifetime: float = 20.0  # Default lifetime in years
    cf: float = 0.85  # Default capacity factor (85% utilization)
    i_rate: float = 0.05  # Default interest rate (5%)
    om_ratio: float = 0.015  # Default O&M ratio (1.5% of capital cost)

    piping_cost: float = 0.07  # Default cost of piping (7% of capital cost)
    installation_cost: float = 0.06  # Default installation cost (6% of capital cost)
    instrumentation_cost: float = 0.04  # Default instrumentation cost (4% of capital cost)

    land_cost: float = 0.00  # Default civil works cost (0% of capital cost)
    civil_works_cost: float = 0.07  # Default civil works cost (7% of capital cost)

    eng_cost: float = 0.06  # Default civil works cost (6% of capital cost)
    constr_cost: float = 0.03  # Default construction cost (3% of capital cost)

    cont_cost: float = 0.08  # Default contingency cost (8% of the fixes capital investment)
    su_cost: float = 0.01  # Default startup cost (1% of capital cost)
    working_capital_cost: float = 0.03  # Default working capital cost (3% of capital cost)

    @classmethod
    def is_usable_for_exergo_environment(cls) -> bool:
        return False

    @classmethod
    def get_model_name(cls) -> str:
        return "manfrida_et_al"

    def get_cost(self, comp_cost: float) -> float:
        """
            From Manfrida et Al. (2023):
            Exergo-economic and exergo-environmental assessment of two
            large CHP geothermal power plants
        """
        self.dc = self.piping_cost + self.instrumentation_cost + self.installation_cost
        self.dc += self.land_cost + self.civil_works_cost
        self.ic = self.eng_cost + self.constr_cost

        self.fci = (1 + self.dc + self.ic) / (1 - self.cont_cost)
        self.tci = self.fci * (1 + self.su_cost + self.working_capital_cost)

        if self.i_rate == 0:
            # If interest rate is zero, alpha = lifetime (which is lim i_rate->0)
            self.alpha = self.lifetime
        else:
            self.alpha = (1 - np.power(1 + self.i_rate, -self.lifetime)) / self.i_rate

        self.tpc = self.tci * (1 + self.alpha * self.om_ratio) / self.alpha * self.lifetime
        return comp_cost * self.tpc / (self.lifetime * self.cf * 8760 * 3600)

    @classmethod
    def get_JSON_inputs(cls) -> list:
        return [

            {"key": 'lifetime', "label": 'Plant Lifetime [years]', "value": cls.lifetime},
            {"key": 'cf', "label": 'Capacity Factor [%]', "value": cls.cf * 100},
            {"key": 'i_rate', "label": 'Yearly Interest Rate [%]', "value": cls.i_rate* 100},
            {"key": 'om_ratio', "label": 'Yearly Maintenance Ratio [%]', "value": cls.om_ratio * 100},

            {"key": 'piping_cost', "label": 'Piping Cost [%]', "value": cls.piping_cost * 100},
            {"key": 'installation_cost', "label": 'Installation Cost [%]', "value": cls.installation_cost * 100},
            {"key": 'instrumentation_cost', "label": 'Instrumentation Cost [%]', "value": cls.instrumentation_cost * 100},

            {"key": 'land_cost', "label": 'Land Acquisition Cost [%]', "value": cls.land_cost * 100},
            {"key": 'civil_works_cost', "label": 'Civil Work Cost [%]', "value": cls.civil_works_cost* 100},

            {"key": 'eng_cost', "label": 'Engineering Cost [%]', "value": cls.eng_cost * 100},
            {"key": 'constr_cost', "label": 'Installation Cost [%]', "value": cls.constr_cost * 100},

            {"key": 'cont_cost', "label": 'Contingency Cost [%]', "value": cls.cont_cost * 100},
            {"key": 'su_cost', "label": 'Startup Cost [%]', "value": cls.su_cost * 100},
            {"key": 'working_capital_cost', "label": 'Working Capital Cost [%]', "value": cls.working_capital_cost * 100}

        ]

    def set_options(self, json_in: t.Any) -> None:

        self.cf = float(json_in.get('cf', self.cf * 100)) / 100  # Convert percentage to decimal
        self.lifetime = float(json_in.get('lifetime', self.lifetime))
        self.i_rate = float(json_in.get('i_rate', self.i_rate * 100)) / 100
        self.om_ratio = float(json_in.get('om_ratio', self.om_ratio * 100)) / 100

        self.piping_cost = float(json_in.get('piping_cost', self.piping_cost * 100)) / 100
        self.installation_cost = float(json_in.get('installation_cost', self.installation_cost * 100)) / 100
        self.instrumentation_cost = float(json_in.get('instrumentation_cost', self.instrumentation_cost * 100)) / 100

        self.land_cost = float(json_in.get('land_cost', self.land_cost * 100)) / 100
        self.civil_works_cost = float(json_in.get('civil_works_cost', self.civil_works_cost * 100)) / 100

        self.eng_cost = float(json_in.get('eng_cost', self.eng_cost * 100)) / 100
        self.constr_cost = float(json_in.get('constr_cost', self.constr_cost * 100)) / 100

        self.cont_cost = float(json_in.get('cont_cost', self.cont_cost * 100)) / 100
        self.su_cost = float(json_in.get('su_cost', self.su_cost * 100)) / 100
        self.working_capital_cost = float(json_in.get('working_capital_cost', self.working_capital_cost * 100)) / 100
