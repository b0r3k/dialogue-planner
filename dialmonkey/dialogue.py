from .da import DA
from .utils import dotdict
import pickle


class Dialogue:
    """A representation of the dialogue -- dialogue history, current state, current system
    and user utterances etc. This object is passed to dialogue components to be changed and
    updated with new information."""

    def __init__(self):
        self.user = ''
        self.system = ''
        self.nlu = DA()
        self.action = DA()
        self.eod = False
        super(Dialogue, self).__setattr__('state', dotdict({}))
        super(Dialogue, self).__setattr__('history', [])

    def end_turn(self):
        """
        Method is called after the turn ends, resets the user and system utterances,
        the nlu and appends to the history.
        :return: None
        """
        self.history.append({
            'user': self.user,
            'system': self.system,
            'nlu': self.nlu.to_cambridge_da_string() if isinstance(self.nlu, DA) else self.nlu,
            'action': self.action.to_cambridge_da_string() if isinstance(self.action, DA) else self.action,
            'state': {k: v for k, v in self.state.items()},
        })
        self.user = ''
        self.system = ''
        self.nlu = DA()
        self.action = DA()

    def serialize(self):
        obj_dict = {
            'system': self.system,
            'user': self.user,
            'nlu': ('DA', self.nlu.to_cambridge_da_string()) if isinstance(self.nlu, DA) else ('list', self.nlu),
            'action': ('DA', self.action.to_cambridge_da_string()) if isinstance(self.action, DA) else ('act', self.action),
            'eod': self.eod,
            'state': {k: v for k, v in self.state.items()},
            'history': self.history
        }
        return pickle.dumps(obj_dict)

    def load_from_serialized(self, serialized_str):
        serialized_dict = pickle.loads(serialized_str)
        self.user = serialized_dict['user']
        self.system = serialized_dict['system']
        if serialized_dict['nlu'][0] == 'DA':
            self.nlu = DA.parse_cambridge_da(serialized_dict['nlu'][1])
        else:
            self.nlu = serialized_dict['nlu'][1]
        if serialized_dict['action'][0] == 'DA':
            self.action = DA.parse_cambridge_da(serialized_dict['action'][1])
        else:
            self.action = serialized_dict['action'][1]
        self.eod = serialized_dict['eod']
        super(Dialogue, self).__setattr__('state', dotdict(serialized_dict['state']))
        super(Dialogue, self).__setattr__('history', serialized_dict['history'])

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
        elif key in ['nlu', 'action']:
            assert isinstance(value, DA), 'Attribute "nlu" has to be a dialmonkey.DA instance.'
        else:
            assert key not in ['history', 'state'],\
                'Direct modification of attribute "{}" is not allowed!'.format(key)
        super(Dialogue, self).__setattr__(key, value)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        else:
            return None
