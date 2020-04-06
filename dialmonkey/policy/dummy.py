from ..component import Component
from ..utils import choose_one


class DummyPolicy(Component):
    """A dummy example policy that issues direct replies to greetings,
    "I don't know" to everything else."""

    def __init__(self, config=None):
        super(DummyPolicy, self).__init__(config)
        self.greeted = False

    def __call__(self, dial, logger):
        if dial.state.intent == 'greet':
            if not self.greeted:
                dial.set_system_response(choose_one(['Hello there', 'Hi!', 'G\'day mate', 'Good morning']))
                self.greeted = True
            else:
                dial.set_system_response('I said hello already.')
        elif dial.state.intent == 'goodbye':
            dial.set_system_response('See you next time!')
            dial.end_dialogue()
        elif len(dial.user) == 0:
            dial.set_system_response('Empty input, ending the dialogue!')
            dial.end_dialogue()
        else:
            dial.set_system_response('I don\'t know how to answer. I am just a dummy bot.')
        return dial

    def reset(self):
        self.greeted = False


class ReplyWithNLU(Component):
    """A "policy" good for testing a NLU system in a stand-alone setting -- it will only
    copy a textual representation of the NLU result into the system reply."""

    def __call__(self, dial, logger):
        if len(dial.user) == 0:
            dial.end_dialogue()
        dial.set_system_response(dial.nlu.to_cambridge_da_string() or '<EMPTY>')
        return dial


class ReplyWithState(Component):
    """A "policy" good for testing a dialogue state tracker in a stand-alone setting -- it will only
    copy a textual representation of the current dialogue state into the system reply."""

    def __call__(self, dial, logger):
        if len(dial.user) == 0:
            dial.end_dialogue()
        dial.set_system_response(str(dial.state))
        return dial


class ReplyWithSystemAction(Component):
    """A "policy" good for testing a dialogue state tracker in a stand-alone setting -- it will only
    copy a textual representation of the current dialogue state into the system reply."""

    def __call__(self, dial, logger):
        if len(dial.user) == 0:
            dial.end_dialogue()
        dial.set_system_response(dial.action.to_cambridge_da_string() or '<EMPTY>')
        return dial

