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


        # Detection of undo intent
        if re.search(r"\b(zpět|vr[aá](tit|ť))\b", dial.user):
            dial.nlu.append(DAI(intent="undo"))


        # Detection of task intent
        if re.search(r"\bdo(prav|sta|je[td])(?![črv])\S*\b", dial.user):
            dial.nlu.append(DAI(intent="task", slot="goal", value="plan_commute"))
        elif re.search(r"\b(co|jak\w)\b.*\?", dial.user):
            dial.nlu.append(DAI(intent="task", slot="goal", value="ask_day"))
        elif re.search(r"\bpřid[aáe]\S*\b", dial.user) or re.search(r"(?<!v\s)(na)?plán(?!k)[ouy]?\S*\b", dial.user):
            dial.nlu.append(DAI(intent="task", slot="goal", value="add_event"))
        elif re.search(r"\bs?ma[zž]\S*\b", dial.user) or re.search(r"\bodeb[er]\S*\b", dial.user):
            dial.nlu.append(DAI(intent="task", slot="goal", value="delete_event"))
        elif re.search(r"\bz?mě(ni|ň)\S*\b", dial.user):
            dial.nlu.append(DAI(intent="task", slot="goal", value="change_event"))
        elif re.search(r"\bkd[ye].*\b(bud[ue](?![jln])\w*|mám)\b.*\?", dial.user):
            dial.nlu.append(DAI(intent="task", slot="goal", value="ask_event"))


        # Detection of inform intent - slot date
        today = datetime.date.today()
        if re.search(r"\bzít[rř]\S*\b", dial.user):
            value = today + datetime.timedelta(days=1)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        elif re.search(r"\bpozít[rř]\S*\b", dial.user):
            value = today + datetime.timedelta(days=2)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        elif re.search(r"\bvčer\S*\b", dial.user):
            value = today + datetime.timedelta(days=-1)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        elif re.search(r"\bpřede?vč(e|í)r\S*\b", dial.user):
            value = today + datetime.timedelta(days=-2)
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
        # Parsing of date in numbers / names of day or months
        day, month, year = 0, 0, 0
        # Days from numbers when text month follows
        day_date = re.search(r"\b\d{1,2}(?=.?\s*(led|únor|břez|květ|červ|srp|zář[ií]|říj|listopad|prosin))\w*\b", dial.user)
        if day_date:
            day = int(day_date.group())
        # Days from numbers when number month follows
        if not day:
            day_date = re.search(r"\b\d{1,2}((?=.?\s*\d\b)|(?=.?\s*\d{2}\b))", dial.user)
            if day_date:
                day = int(day_date.group())
        # Months from numbers
        month_date = re.search(r"((?<=\d\.\s)|(?<=\d\.)|(?<=\d\s))\d{1,2}(?=\b)", dial.user)
        if month_date:
            month = int(month_date.group())
        # Months from text
        if re.search(r"\bled(en|na|nu)\b", dial.user):
            month = 1
        elif re.search(r"\búnor[au]?\b", dial.user):
            month = 2
        elif re.search(r"\bbřez(en|na|nu|nem)\b", dial.user):
            month = 3
        elif re.search(r"\bdub(en|na|nu)\b", dial.user):
            month = 4
        elif re.search(r"\bkvět(en|na|nu)\b", dial.user):
            month = 5
        elif re.search(r"\bčerv(en|na|nu)\b", dial.user):
            month = 6
        elif re.search(r"\bčerven(ec|ce|ci)\b", dial.user):
            month = 7
        elif re.search(r"\bsrp(en|na|nu)\b", dial.user):
            month = 8
        elif re.search(r"\bzáří\b", dial.user):
            month = 9
        elif re.search(r"\bříj(en|na|nu)\b", dial.user):
            month = 10
        elif re.search(r"\blistopadu?\b", dial.user):
            month = 11
        elif re.search(r"\bprosin(ec|ce|ci)\b", dial.user):
            month = 12
        # Year
        year_date = re.search(r"((?<=\d\.\s)|(?<=\d\.)|(?<=\d\s))\d{4}(?=\b)", dial.user)
        if year_date:
            year = int(year_date.group())
        # Get the DAI
        if day or month or year:
            day = day if day else today.day
            month = month if month else today.month
            year = year if year else today.year
            value = datetime.datetime(year, month, day).date()
            dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))


        

        logger.info('NLU: %s', str(dial.nlu))
        return dial
