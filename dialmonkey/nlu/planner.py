from ..component import Component
from ..da import DAI
import datetime
import re

class PlannerNLU(Component):
    """A planner NLU that is able to parse commands for manipulating events in calendar and planning commute."""

    def __call__(self, dial, logger):

        # Detection of confirm intent
        if re.search(r"\b(an|j)o+\b", dial.user):
            dial.nlu.append(DAI(intent="confirm", slot="value", value="true"))
        if re.search(r"\bne+\b", dial.user):
            dial.nlu.append(DAI(intent="confirm", slot="value", value="false"))

        # Detection of task intent
        if re.search(r"\bpřid[aáe]\S*\b", dial.user):
            dial.nlu.append(DAI(intent="task", slot="goal", value="add_event"))
        if re.search(r"\bs?ma[zž]\S*\b", dial.user) or re.search(r"\bodeb[er]\S*\b", dial.user):
            dial.nlu.append(DAI(intent="task", slot="goal", value="delete_event"))

        # Detection of inform intent - slot date
        if re.search(r"\bzít[rř]\S*\b", dial.user):
            value = datetime.date.today() + datetime.timedelta(days=1)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        if re.search(r"\bpozít[rř]\S*\b", dial.user):
            value = datetime.date.today() + datetime.timedelta(days=2)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        if re.search(r"\bvčer\S*\b", dial.user):
            value = datetime.date.today() + datetime.timedelta(days=-1)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        if re.search(r"\bpřede?vč(e|í)r\S*\b", dial.user):
            value = datetime.date.today() + datetime.timedelta(days=-2)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        # TODO parsing of date in numbers / names of day or months

        logger.info('NLU: %s', str(dial.nlu))
        return dial
