from ..component import Component
from dialmonkey.da import DAI


class BeliefStateDST(Component):
    """Belief state tracker which copies NLU results into the current dialogue
    state, multiplies probabilities by None and then adds all other probabilities."""

    def __call__(self, dial, logger):

        if dial.nlu:
            for dai in dial.nlu:
                # If current thing in dial.nlu is DialogActItem
                if isinstance(dai, DAI):
                    intent, slot = dai.intent, dai.slot
                    dial.state[slot] = dict()
                    dial.state[slot] = dai.value
                    if intent == "task" and slot == "goal":
                        dial.state["goal_"] = dai.value

                # Else it is a dictionary with probabilities
                else:
                    value_probs = dai
                    info = value_probs.pop("info_")
                    intent, slot = info["intent"], info["slot"]
                    
                    # Initialize given intent-slot pair
                    if not (intent, slot) in dial.state:
                        dial.state[(intent, slot)] = {None: 1.0}
                    
                    # Multiply existing probabilities by the probability of None
                    none_prob = float(value_probs.pop(None))
                    for key in dial.state[(intent, slot)]:
                        dial.state[(intent, slot)][key] *= none_prob

                    # Add the new probabilities
                    for key in value_probs:
                        if key in dial.state[(intent, slot)]:
                            dial.state[(intent, slot)][key] += value_probs[key]
                        else:
                            dial.state[(intent, slot)][key] = value_probs[key]

        else:
            dial.state.intent = None

        logger.info('State: %s', str(dial.state))
        return dial
