from ..component import Component
from ..da import DAI


class DummyNLU(Component):

    def __call__(self, dial, logger):
        if any([w in dial['user'] for w in ['hello', 'hey', 'hi', 'ola', 'ciao', 'ahoj']]):
            dial['nlu'].append(DAI.parse('greet()'))
        if any([w in dial['user'] for w in ['bye', 'goodbye', 'good bye', 'see ya', 'see you']]):
            dial['nlu'].append(DAI.parse('goodbye()'))

        logger.info('NLU: %s', str(dial['nlu']))
        return dial
