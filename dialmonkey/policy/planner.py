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
        goal_known, goal = get_goal(self, dial)

        if goal_known:
            # Try to accomplish the goal
            pass
        else:
             # Goal unknown
             dial.action.append(DAI(intent="error", slot="goal_unknown", value=None))

        return dial

    def get_goal(self, dial):
        found_goal = False
        goal = "unk"
        if "goal_" in dial.state:
            found_goal = True
            goal = dial.state["goal_"]
        return found_goal, goal
            

    def reset(self):
        self.greeted = False
