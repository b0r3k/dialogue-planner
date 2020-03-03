from ..component import Component


class DummyDST(Component):
    def __call__(self, state, logger):
        for k, v in state['nlu'].items():
            state['state_dict'][k] = v
        logger.info('State: %s', str(state['state_dict']))
        return state
