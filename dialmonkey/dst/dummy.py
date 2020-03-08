from ..component import Component


class DummyDST(Component):
    def __call__(self, dial, logger):
        if dial['nlu']:
            dial['state']['intent'] = dial['nlu'][0].intent   # assume just one intent
            for dai in dial['nlu']:
                if dai.slot:
                    dial['state_dict'][dai.slot] = dai.value
        else:
            dial['state']['intent'] = None
        logger.info('State: %s', str(dial['state_dict']))
        return dial
