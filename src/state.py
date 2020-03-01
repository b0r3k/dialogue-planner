class DialogueState:

    def __init__(self, logger):
        self.logger = logger
        self.user = ''
        self.system = ''
        self.nlu = {}
        self.eod = False
        super(DialogueState, self).__setattr__('state_dict', {})
        super(DialogueState, self).__setattr__('history', [])

    def end_turn(self):
        self.history.append({
            'user': self.user,
            'system': self.system,
            'nlu': self.nlu,
            'state_dict': self.state_dict
        })
        self.user = ''
        self.system = ''
        self.nlu = {}

    def __setattr__(self, key, value):
        if key == 'user':
            assert isinstance(value, str), 'Attribute "user" has to be of type "string"'
            # TODO: should we normalize the utterance here?
        elif key == 'system':
            assert isinstance(value, str), 'Attribute "system" has to be of type "string"'
        elif key == 'nlu':
            assert isinstance(value, dict), 'Attribute "nlu" has to be of type "dict"'
        elif key == 'eod':
            assert isinstance(value, bool), 'Attribute "eod" has to be of type "bool"'
        else:
            assert key not in DialogueState.essential_attributes(),\
                'Modification of attribute "{}" is not allowed!'.format(key)
        super(DialogueState, self).__setattr__(key, value)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        else:
            self.logger.warning('Attribute "{}" not found!'.format(item))
            return None

    @staticmethod
    def essential_attributes():
        return ['user', 'system', 'nlu', 'state_dict', 'history', 'eod']
