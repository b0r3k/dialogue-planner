from ..component import Component
from ..da import DAI
import datetime
import re

class PlannerNLU(Component):
    """A planner NLU that is able to parse commands for manipulating events in calendar and planning commute."""

    def __call__(self, dial, logger):
        # Lower-case the input
        dial.user = dial.user.lower()

        # Detect confirm intent
        get_confirm(dial)

        # Detect undo intent
        get_undo(dial)

        # Detect task intent
        get_task(dial)

        # Detect inform intent - slot date
        get_inform_date(dial)

        # Detect inform intent - slot repeating
        get_inform_repeating(dial)        

        # Detect inform intent - slots place_start and place_end
        get_inform_place_commute(dial)

        # Detect inform intent - slot time
        get_inform_time(dial)

        # Detect inform intent - slot duration
        get_inform_duration(dial)

        # Detect inform intent - slot name
        get_inform_name(dial)

        logger.info('NLU: %s', str(dial.nlu))
        return dial


def get_confirm(dial):
    if re.search(r"\b(an|j)o+\b", dial.user):
        dial.nlu.append(DAI(intent="confirm", slot="value", value="true"))
    if re.search(r"\bne+\b", dial.user):
        dial.nlu.append(DAI(intent="confirm", slot="value", value="false"))

def get_undo(dial):
    if re.search(r"\b(zpět|vr[aá](tit|ť))\b", dial.user):
        dial.nlu.append(DAI(intent="undo"))

def get_task(dial):
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

def get_inform_date(dial):
    # Parsing of stuff like "today" or "tomorrow"
    today = datetime.date.today()
    if re.search(r"\bdne[sš](?!i)\w*\b", dial.user):
        value = today
        dial.nlu.append(DAI(intent="inform", slot="date", value=str(value)))
    elif re.search(r"\bzít[rř]\S*\b", dial.user):
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
    if day_date := re.search(r"\b\d{1,2}(?=.?\s*(led|únor|břez|květ|červ|srp|zář[ií]|říj|listopad|prosin))\w*\b", dial.user):
        day = int(day_date.group())
    # Days from numbers when number month follows
    if not day:
        if day_date := re.search(r"\b\d{1,2}((?=\.\s*\d\b)|(?=\.\s*\d{2}\b)|(?=\.?\s+\d\b)|(?=\.?\s+\d{2}\b))", dial.user):
            day = int(day_date.group())
    # Months from numbers
    if month_date := re.search(r"((?<=\d\.\s)|(?<=\d\.)|(?<=\d\s))\d{1,2}(?=\b)", dial.user):
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

def get_inform_place(dial):
    if re.search(r"\bdoma\b", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="place", value="home"))
            
def get_inform_repeating(dial):
    if re.search(r"(?<=\bkaždý\s)den", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="repeating", value="day"))
    elif re.search(r"(?<=\bkaždý\s)týden", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="repeating", value="week"))
    elif re.search(r"(?<=\bkaždý\s)měsíc", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="repeating", value="month"))
    elif re.search(r"(?<=\bkaždý\s)rok", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="repeating", value="year"))
    
def get_inform_place_commute(dial):
    if re.search(r"\bz\sdomu\b", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="place_start", value="home"))
    if re.search(r"\bdomů\b", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="place_end", value="home"))

def get_inform_time(dial): 
    # Parse time of beginning
    if re.search(r"\bkdykoliv?\b", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="time_start", value="anytime"))
        dial.nlu.append(DAI(intent="inform", slot="time_end", value="anytime"))
    if time_start := re.search(r"((?<=\bv\s)|(?<=\bve\s)|(?<=\bod\s))\d{1,2}(?=\s?)[\s:](?=\s?)\d{2}", dial.user):
        time_start = time_start.group()
        if time_start[2] == ' ':
            time_start[2] == ':'
        dial.nlu.append(DAI(intent="inform", slot="time_start", value=time_start))
    elif time_start := re.search(r"((?<=\bv\s)|(?<=\bve\s)|(?<=\bod\s))\d{1,2}(?=\s(hodin\s)?ráno\b)", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="time_start", value=time_start.group()+":00"))
    elif time_start := re.search(r"((?<=\bv\s)|(?<=\bve\s)|(?<=\bod\s))\d{1,2}(?=\s(hodin\s)?večer\b)", dial.user):
        if (time_start := int(time_start.group())) <= 12:
            time_start = (time_start + 12) % 24
        dial.nlu.append(DAI(intent="inform", slot="time_start", value=str(time_start)+":00"))
    elif time_start := re.search(r"((?<=\bv\s)|(?<=\bve\s)|(?<=\bod\s))\d{1,2}(?=\s(hodin\s)?odpoledne\b)", dial.user):
        if (time_start := int(time_start.group())) <= 12:
            time_start = (time_start + 12) % 24
        dial.nlu.append(DAI(intent="inform", slot="time_start", value=str(time_start)+":00"))
    elif time_start := re.search(r"((?<=\bv\s)|(?<=\bve\s)|(?<=\bod\s))\d{1,2}(?=\b)", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="time_start", value=time_start.group()+":00"))
    # Parse time of end
    if time_start := re.search(r"(?<=\bdo\s)\d{1,2}(?=\s?)[\s:](?=\s?)\d{2}", dial.user):
        time_start = time_start.group()
        if time_start[2] == ' ':
            time_start[2] == ':'
        dial.nlu.append(DAI(intent="inform", slot="time_end", value=time_start))
    elif time_start := re.search(r"(?<=\bdo\s)\d{1,2}(?=\s(hodin\s)?ráno\b)", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="time_end", value=time_start.group()+":00"))
    elif time_start := re.search(r"(?<=\bdo\s)\d{1,2}(?=\s(hodin\s)?večer\b)", dial.user):
        if (time_start := int(time_start.group())) <= 12:
            time_start = (time_start + 12) % 24
    elif time_start := re.search(r"(?<=\bdo\s)\d{1,2}(?=\s(hodin\s)?odpoledne\b)", dial.user):
        if (time_start := int(time_start.group())) <= 12:
            time_start = (time_start + 12) % 24
        dial.nlu.append(DAI(intent="inform", slot="time_end", value=str(time_start)+":00"))
    elif time_start := re.search(r"(?<=\bdo\s)\d{1,2}(?=\b)", dial.user):
        dial.nlu.append(DAI(intent="inform", slot="time_end", value=time_start.group()+":00"))

def get_inform_duration(dial):
    minutes, hours = "00", 0
    # Parse minutes
    if re.search(r"\ba\spůl\b", dial.user):
        minutes = "30"
    elif re.search(r"\ba\spůl\b", dial.user):
        minutes = "15"
    elif re.search(r"\ba\stři\s?čtvrtě\b", dial.user):
        minutes = "45"
    # Parse hours
    if re.search(r"\bhodinu\b", dial.user):
        hours = 1
    elif hours := re.search(r"(?<!v\s)(?<!ve\s)\d(?=\shodiny?\b)", dial.user):
        hours = int(hours.group())
    # Create the DAI
    if minutes != "00" or hours:
        dial.nlu.append(DAI(intent="inform", slot="duration", value=str(hours)+':'+minutes))

def get_inform_name(dial):
    if name := re.search(r"(?<=\bpřid[aáe][jtm]\s)[ěščřžýáíéóúůďťňa-z\s]+(?=[?:!,.\d])", dial.user) or (name := re.search(r"((?<=naplánovat\s)|(?<=naplánuj\s))[ěščřžýáíéóúůďťňa-z\s]+(?=[,.\d])", dial.user)):
        name = name.group()
        name = name.replace("zítra",' ').replace("dlouhodobě",' ').replace("pozítří",' ').strip()
        if name:
            dial.nlu.append(DAI(intent="inform", slot="name", value=name))
    elif name := re.search(r"(?<=\bv\splánu\spříští\s)[ěščřžýáíéóúůďťňa-z\s]+(?=[?!:,.\d])", dial.user) or (name := re.search(r"(?<=\bv\splánu\s)[ěščřžýáíéóúůďťňa-z\s]+(?=[?!:,.\d])", dial.user)):
        name = name.group()
        name = name.replace("zítra",' ').replace("dlouhodobě",' ').replace("pozítří",' ').strip()
        if name:
            dial.nlu.append(DAI(intent="inform", slot="name", value=name))