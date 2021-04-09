from ..component import Component
from ..da import DAI
import datetime


class PlannerNLU(Component):
    """A planner NLU that is able to parse commands for manipulating events in calendar and planning commute."""

    def __call__(self, dial, logger):

        # Detection of confirm intent
        if any([w in dial.user for w in ["ano", "jo"]]):
            dial.nlu.append(DAI(intent="confirm", slot="value", value="true"))
        if "ne" in dial.user:
            dial.nlu.append(DAI(intent="confirm", slot="value", value="false"))

        # Detection of task intent
        if any([w in dial.user for w in ["přidávám", "přidat"]]):
            dial.nlu.append(DAI(intent="task", slot="goal", value="add_event"))
        

        # Detection of task intent

        # Detection of inform intent - slot date
        if "zítra" in dial.user:
            value = datetime.date.today() + datetime.timedelta(days=1)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        if "pozítří" in dial.user:
            value = datetime.date.today() + datetime.timedelta(days=2)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        if "včera" in dial.user:
            value = datetime.date.today() + datetime.timedelta(days=-1)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        if "předevčírem" in dial.user:
            value = datetime.date.today() + datetime.timedelta(days=-2)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        # TODO parsing of date in numbers / names of day or months

        logger.info('NLU: %s', str(dial.nlu))
        return dial
