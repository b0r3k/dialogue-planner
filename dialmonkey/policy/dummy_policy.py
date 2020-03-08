from ..component import Component
from ..utils import choose_one


class DummyPolicy(Component):
    def __init__(self):
        self.greeted = False

    def __call__(self, dial, logger):
        if dial['state'].get('intent') == 'greet':
            if not self.greeted:
                dial.set_system_response(choose_one(['Hello there', 'Hi!', 'G\'day mate', 'Good morning']))
                self.greeted = True
            else:
                dial.set_system_response('I said hello already.')
        elif dial['state'].get('intent')  == 'goodbye':
            dial.set_system_response('See you next time!')
            dial.end_dialogue()
        elif len(dial['user']) == 0:
            dial.set_system_response('Empty input, ending the dialogue!')
            dial.end_dialogue()
        else:
            dial.set_system_response('I don\'t know how to answer. I am just a dummy bot.')
        return dial

    def reset(self):
        self.greeted = False
