from ..component import Component


class DummyNLU(Component):
    def __call__(self, state, logger, *args, **kwargs):
        if any([w in state['user'] for w in ['hello', 'hey', 'hi', 'ola', 'ciao', 'ahoj']]):
            state['nlu']['greet'] = True
        if any([w in state['user'] for w in ['bye', 'goodbye', 'good bye', 'see ya', 'see you']]):
            state['nlu']['goodbye'] = True
        return state
