class DummyNLU:
    def __call__(self, state, logger, *args, **kwargs):
        if any([w in state['user'] for w in ['hello', 'hey', 'hi', 'ola']]):
            state['nlu']['greet'] = True
        return state
