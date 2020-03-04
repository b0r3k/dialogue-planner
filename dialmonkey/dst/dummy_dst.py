from ..component import Component


class DummyDST(Component):
    def __call__(self, state, logger):
        if state['nlu']:
            state['state_dict']['intent'] = state['nlu'][0].intent   # assume just one intent
            for dai in state['nlu']:
                if dai.slot:
                    state['state_dict'][dai.slot] = dai.value
        else:
            state['state_dict']['intent'] = None
        logger.info('State: %s', str(state['state_dict']))
        return state
