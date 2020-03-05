from copy import deepcopy
from .da import DA


# TODO: should we rename DialogueState -> Environment, state_dict -> dialogue_state ?
# XXX: OD: yes, sounds better :-)
class DialogueState:

    def __init__(self):
        self.user = ''
        self.system = ''
        self.nlu = DA()
        self.eod = False
        super(DialogueState, self).__setattr__('state_dict', {})
        super(DialogueState, self).__setattr__('history', [])

    def end_turn(self):
        """
        Method is called after the turn ends, resets the user and system utterances,
        the nlu and appends to the history.
        :return: None
        """
        self.history.append({
            'user': self.user,
            'system': self.system,
            'nlu': self.nlu,
            'state_dict': deepcopy(self.state_dict)
        })
        self.user = ''
        self.system = ''
        self.nlu = DA()

    def set_system_response(self, response):
        self.system = response

    def set_user_input(self, inp):
        self.user = inp

    def end_dialogue(self):
        self.eod = True

    def __setattr__(self, key, value):
        if key in ['user', 'system']:
            assert isinstance(value, str), f'Attribute "{key}" has to be of type "string"'
        elif key == 'eod':
            assert isinstance(value, bool), 'Attribute "eod" has to be of type "bool"'
        elif key == 'nlu':
            assert isinstance(value, DA), 'Attribute "nlu" has to be a dialmonkey.DA instance.'
        else:
            assert key not in ['history', 'state_dict'],\
                'Modification of attribute "{}" is not allowed!'.format(key)
        super(DialogueState, self).__setattr__(key, value)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        else:
            return None

    @staticmethod
    def essential_attributes():
        """
        Essential attributes that has to be present in the valid DialogueState instance.
        :return: list of essential attributes
        """
        return ['user', 'system', 'nlu', 'state_dict', 'history', 'eod']
