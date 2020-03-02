from abc import ABC, abstractmethod

from ..state import DialogueState


class Component(ABC):
    def init_state(self, state: DialogueState):
        """
        Method that is called before the dialogue starts and can initialize the state object.
        :param state: DialogueState instance that can be modified
        :return: optionally modified DialogueState instance
        """
        return state

    @abstractmethod
    def __call__(self, state: DialogueState, logger, *args, **kwargs):
        """
        This method is called in every turn, takes the DialogueState, optionally modifies it and returns the result.
        :param state: DialogueState instance
        :param logger: logger reference, can be used for debugging purposes or verbose mode
        :param args: not passed
        :param kwargs: not passed
        :return: optionally modified DialogueState instance
        """
        pass

    def reset(self):
        """
        Resets the component's optional flags and other properties, if any
        :return: None
        """
        return None
