from ..component import Component
from dialmonkey.da import DA, DAI


class PlannerPolicy(Component):
    """Planner policy that should be able to handle calendar events."""

    def __init__(self, config=None):
        super(PlannerPolicy, self).__init__(config)
        self.asked_confirmation = False
        self.confirmed = False
        self.last_goal = None


    def __call__(self, dial, logger):
        # Create the dial.action as empty DA if it doesn't exist
        dial.action = DA()
        
        # Find the goal of current task
        goal_known, goal = get_goal(dial)

        if goal != self.last_goal:
            # Goal changed, confirmation is invalid
            self.confirmed = False
            self.asked_confirmation = False
            # Save the goal
            self.last_goal = goal
        
        if self.asked_confirmation:
            # If asked for confirmation, check if confirmed, if not it's neccessary to ask again
            if get_confirmation(dial):
                self.confirmed = True
            else:
                self.confirmed = False
                self.asked_confirmation = False


        if goal_known:
            # Try to accomplish the goal, always check if all the slots are filled, ask confirmation when needed
            if goal == "ask_day":
                if not (missing_slots := check_slots(dial, ["date"])):
                    # Call the API and get the events for given day
                    pass
                else:
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))  

            elif goal == "ask_event":
                if not (missing_slots := check_slots(dial, ["name"])):
                    # Call the API and get the event with given name
                    pass
                else:
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))
                
            elif goal == "add_event":
                if not (missing_slots := check_slots(dial, ["name", "date", "time_start", "time_end", "place", "repeating"])):
                    if not self.confirmed:
                        # Let user confirm
                        dial.action.append(DAI(intent="ask", slot="confirm_add", value=None))
                        self.asked_confirmation = True
                    else:
                        # When confirmed, TODO call the API and add the event, infrom the user that successfull
                        self.asked_confirmation, self.confirmed = False, False
                        dial.action.append(DAI(intent="inform", slot="succ_add", value=None))                        
                else:
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))
                
            elif goal == "change_event":
                if not (missing_slots := check_slots(dial, ["id"])):
                    if not self.confirmed:
                        # Let user confirm
                        dial.action.append(DAI(intent="ask", slot="confirm_change", value=None))
                        self.asked_confirmation = True
                    else:
                        # When confirmed, TODO call the API and change the event, infrom the user that successfull
                        self.asked_confirmation, self.confirmed = False, False
                        dial.action.append(DAI(intent="inform", slot="succ_change", value=None))
                else:
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))
                
            elif goal == "delete_event":
                if not (missing_slots := check_slots(dial, ["id"])):
                    # Let user confirm
                    if not self.confirmed:
                        dial.action.append(DAI(intent="ask", slot="confirm_del", value=None))
                        self.asked_confirmation = True
                    else:
                        # When confirmed, TODO call the API and delete the event, infrom the user that successfull
                        self.asked_confirmation, self.confirmed = False, False
                        dial.action.append(DAI(intent="inform", slot="succ_del", value=None))
                else:
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))
                
            else:
                # Goal in dial.state, but handling unknown
                dial.action.append(DAI(intent="error", slot="goal_unimplemented", value=None))   

        else:
             # Goal unknown, ask it
             dial.action.append(DAI(intent="ask", slot="goal", value=None))

        return dial

def get_goal(dial):
    # Get the current user goal (if known) from the dial.state
    
    found_goal = False
    goal = "unk"
    if "goal_" in dial.state:
        found_goal = True
        goal = dial.state["goal_"]
    return found_goal, goal

def get_confirmation(dial):
    # Check if the user confirmed in the last utterance

    confirmed = False
    for da in dial.nlu:
        if da.intent == "confirm" and dial.slot == "value" and dial.value:
            confirmed = True
    return confirmed


def check_slots(dial, slots):
    # Check if the values for asked slots are known with some reasonable probability (0.7)
    # If not, return missing slots

    missing_slots = []

    for slot in slots:
        found = False
        if ("inform", slot) in dial.state:
            probabilities = dial.state[("inform", slot)]
            for value in probabilities:
                if probabilities[value] > 0.7:
                    found = True
        if not found:
            missing_slots.append(slot)
    
    return missing_slots