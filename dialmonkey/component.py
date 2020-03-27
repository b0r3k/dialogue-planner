from abc import ABC, abstractmethod

from .dialogue import Dialogue


class Component(ABC):
    """A base class for all dialogue system components (NLU, trackers, policies etc.)."""

    def __init__(self, config=None):
        """
        Default constructor: just save the provided configuration.
        """
        self.config = config

    def init_dialogue(self, dial: Dialogue):
        """
        Method that is called before the dialogue starts and can initialize the dialogue object.
        :param dial: Dialogue instance that can be modified
        :return: optionally modified Dialogue instance
        """
        return dial

    @abstractmethod
    def __call__(self, dial: Dialogue, logger):
        """
        This method is called in every turn, takes the Dialogue, optionally modifies it and returns the result.
        :param dial: Dialogue instance
        :param logger: logger reference, can be used for debugging purposes or verbose mode
        :return: optionally modified Dialogue instance
        """
        pass

    def reset(self):
        """
        Called after the end of the dialogue.
        Resets the component's optional flags and other properties, if any.
        :return: None
        """
        return None
