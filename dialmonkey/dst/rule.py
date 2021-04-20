from ..component import Component


class BeliefStateDST(Component):
    """Belief state tracker which copies NLU results into the current dialogue
    state, multiplies probabilities by None and then adds all other probabilities."""

    def __call__(self, dial, logger):
        if dial.nlu:
            dial.state.intent = []
            for value_probs in dial.nlu:
                info = value_probs.pop("info_")
                intent, slot = info["intent"], info["slot"]
                
                if not (intent, slot) in dial.state:
                    dial.state[(intent, slot)] = {None: 1.0}
                
                print(dial.state)
                none_prob = float(value_probs.pop(None))
                for key in dial.state[(intent, slot)]:
                    dial.state[(intent, slot)][key] *= none_prob

                for key in value_probs:
                    if key in dial.state[(intent, slot)]:
                        dial.state[(intent, slot)][key] += value_probs[key]
                    else:
                        dial.state[(intent, slot)][key] = value_probs[key]

        else:
            dial.state.intent = None
        logger.info('State: %s', str(dial.state))
        return dial
