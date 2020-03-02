from ..component import Component


class DummyPolicy(Component):
    def __init__(self):
        self.greeted = False

    def __call__(self, state, logger, *args, **kwargs):
        if 'goodbye' in state['state_dict']:
            state.set_system_response('See you next time!')
            state.end_dialogue()
        elif len(state['user']) == 0:
            state.set_system_response('Empty input, ending the dialogue!')
            state.end_dialogue()
        elif 'greet' in state['state_dict']:
            if not self.greeted:
                state.set_system_response('Hello there')
                self.greeted = True
            else:
                state.set_system_response('I said hello already.')
        else:
            state.set_system_response('I don\'t know how to answer. I am just a dummy bot.')
        return state

    def reset(self):
        self.greeted = False
