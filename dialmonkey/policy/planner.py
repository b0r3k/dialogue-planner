from ..component import Component
from dialmonkey.da import DA, DAI


class PlannerPolicy(Component):
    """Planner policy that should be able to handle calendar events."""

    def __init__(self, config=None):
        super(PlannerPolicy, self).__init__(config)

    def __call__(self, dial, logger):
        # Create the dial.action as empty DA if it doesn't exist
        dial.action = DA()
        
        # Find the goal of current task
        goal_known, goal = get_goal(dial)

        if goal_known:
            # Try to accomplish the goal
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
                    # Let user confirm
                    # When confirmed, call the API and add the event
                    pass
                else:
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))
                
            elif goal == "change_event":
                if not (missing_slots := check_slots(dial, ["id"])):
                    # Let user confirm
                    # When confirmed, call the API and change the event
                    pass
                else:
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))
                
            elif goal == "delete_event":
                if not (missing_slots := check_slots(dial, ["id"])):
                    # Let user confirm
                    # When confirmed, call the API and delete the event
                    pass
                else:
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))
                
            else:
                dial.action.append(DAI(intent="error", slot="goal_unimplemented", value=None))   

        else:
             # Goal unknown
             dial.action.append(DAI(intent="error", slot="goal_unknown", value=None))

        return dial

def get_goal(dial):
    # Get the current user goal (if known) from the dial.state
    
    found_goal = False
    goal = "unk"
    if "goal_" in dial.state:
        found_goal = True
        goal = dial.state["goal_"]
    return found_goal, goal

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