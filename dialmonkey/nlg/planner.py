from ..component import Component
from ..da import DAI, DA
import json
from random import choice

class PlannerNLG(Component):
    """ Planner NLG that should be able to translate all possible DAs from dial.action that 
    PlannerPolicy produced. """

    def __init__(self, config=None):
        # Load the templates from json file
        filename = "dialmonkey/nlg/templates/planner_nlg_templates.json"
        with open(filename, encoding="utf-8") as f:
            self.templates = json.load(f)

    def __call__(self, dial, logger):
        responses = self.get_responses(dial)
        response = ' '.join(responses)
        dial.set_system_response(response)

        logger.info('Reponse: %s', str(dial.system))
        return dial

    def get_responses(self, dial):
        # Initialize stuff as empty
        responses, event_infos, last_intent = [], [], None
        to_process, current = dict(), []
        action_iterator = iter(dial.action)

        # Transform informing about events straight to responses
        # Get different slots of same intent into a dict[intents] called to_process
        for dai in action_iterator:
            if dai.intent == "inform" and (dai.slot == "event_by_name" or dai.slot == "event_by_date"):
                replacements = dict()
                values_needed = 4 if dai.slot == "event_by_name" else 3
                replacements[dai.slot] = None
                for _ in range(values_needed):
                    next_dai = next(action_iterator)
                    replacements[next_dai.slot] = next_dai.value
                response = choice(self.templates["inform"][','.join(replacements.keys())])
                event_infos.append(response.format(**replacements))
                last_intent = "inform"

            elif (intent := dai.intent) != last_intent and current:
                if intent in to_process:
                    to_process[intent] += current
                else:
                    to_process[intent] = current
                current = [dai]

            else:
                current.append(dai)

        # Join all the event information sentences to something sensible and add it do responses
        if event_infos:
            joints = [", dále ", ", pak ", ", potom "]
            response = choice(joints).join(event_infos)
            beginnings = ["Máte v plánu ", "Máte naplánováno ", "V kalendáři jsem našla "]
            response = choice(beginnings) + response + '.'
            responses.append(response)

        # Go through the unprocessed dais
        for intent, dais in to_process.items():
            all_slots = ','.join(item.slot for item in dais)
            replacements = dict([(item.slot, item.value) for item in dais])
            # Try to find one template which suits all the slots
            if all_slots in self.templates[intent]:
                response = choice(self.templates[intent][all_slots])
                responses.append(response.format(**replacements))
            # Not found, find templates for individual slots
            for item in dais:
                response = choice(self.templates[intent][item.slot])
                responses.append(response.format(**replacements))

        return responses