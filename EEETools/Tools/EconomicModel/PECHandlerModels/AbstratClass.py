from abc import ABC, abstractmethod
import typing as t


class AbstractPECHandler(ABC):
    """
    Abstract class for PEC Handler models.
    This class defines the interface for PEC Handler models.
    The general goal of the model is to returns the cost in €/s for
    each component starting from the sum of the cost of the main
    component (PEC) of the system.

    The class will also have a method to define which are the required
    inputs to calculate the cost of the component. to be used by the frontend
    JSON app to display the user the required inputs to calculate the cost.
    """

    @classmethod
    @abstractmethod
    def is_usable_for_exergo_environment(cls) -> bool:
        """
        Method to check if the PEC Handler model is usable for exergo environment.
        :return: True if the model is usable for exergo environment, False otherwise
        """
        return True

    @classmethod
    @abstractmethod
    def get_model_name(cls) -> str:
        """
        Name of the PEC Handler model.
        :return: name of the PEC Handler model
        """
        pass

    @abstractmethod
    def get_cost(self, comp_cost: float) -> float:
        """
        Method to calculate the cost of the component.
        :param comp_cost: cost of the component in €
        :return: cost of the component in €/s
        """
        pass

    @classmethod
    @abstractmethod
    def get_JSON_inputs(cls) -> list:
        """
        Method to return the required inputs to calculate the cost of the component.
        :return: list of required inputs
        """
        pass

    @abstractmethod
    def set_options(self, json_in: t.Any) -> None:

        pass



