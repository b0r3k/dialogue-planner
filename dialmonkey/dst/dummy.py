from ..component import Component


class DummyDST(Component):
    """A basic state tracker that simply copies NLU results into the current dialogue
    state, overwriting any previous values."""

    def __call__(self, dial, logger):
        if dial.nlu:
            dial.state.intent = dial.nlu[0].intent   # assume just one intent
            for dai in dial.nlu:
                if dai.slot:
                    dial.state[dai.slot] = dai.value
        else:
            dial.state.intent = None
        logger.info('State: %s', str(dial.state))
        return dial
