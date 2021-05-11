from ..component import Component
from dialmonkey.da import DA, DAI
from datetime import datetime, timedelta
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dialmonkey.dialogue import Dialogue
from dialmonkey.utils import dotdict


class PlannerPolicy(Component):
    """Planner policy that should be able to handle calendar events."""

    def __init__(self, config=None):
        super(PlannerPolicy, self).__init__(config)
        self.asked_confirmation = False
        self.confirmed = False
        self.last_goal = None

        # Build the API service
        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('hw7/token.json'):
            creds = Credentials.from_authorized_user_file('hw7/token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'hw7/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('hw7/token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)


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
                slots_needed = ["date"]
                if not (missing_slots := check_slots(dial, slots_needed)):
                    # Call the API and get the events (up to 10) for given day
                    date = datetime.strptime(dial.state["date"], "%Y-%m-%d")
                    # The API needs the datetime in isoformat with timezones
                    time_min = date.astimezone().isoformat('T')
                    time_max = (date + timedelta(days=1)).astimezone().isoformat('T')
                    # Query the events for given day
                    events_result = self.service.events().list(calendarId='primary', timeMin=time_min, timeMax=time_max,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
                    events = events_result.get('items', [])
                    # Append information about each event into system action
                    for event in events:
                        dial.action.append(DAI(intent="inform", slot="event_name", value=event["summary"]))
                        start = datetime.fromisoformat(event["start"]["dateTime"])
                        dial.action.append(DAI(intent="inform", slot="event_start", value=start.strftime("%H:%M")))
                        end = datetime.fromisoformat(event["end"]["dateTime"])
                        dial.action.append(DAI(intent="inform", slot="event_end", value=end.strftime("%H:%M")))

                    # Reset the state
                    super(Dialogue, dial).__setattr__('state', dotdict({}))

                    if len(events) == 1:
                        # If there is only one, save the event id for further use
                        dial.state["id"] = events[0]["id"]
                    if not events:
                        # If there's no event for given day, inform about it
                        dial.action.append(DAI(intent="inform", slot="no_events", value=None))

                else:
                    # Ask about the missing slots
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))  


            elif goal == "ask_event":
                slots_needed = ["name"]
                if not (missing_slots := check_slots(dial, slots_needed)):
                    # Call the API and get the events (up to 10) with given name
                    name = dial.state["name"]
                    events_result = self.service.events().list(calendarId='primary', timeMin=datetime.now().astimezone().isoformat('T'),
                                        maxResults=10, singleEvents=True, q=name,
                                        orderBy='startTime').execute()
                    events = events_result.get('items', [])
                    # Append information about each event into system action
                    for event in events:
                        dial.action.append(DAI(intent="inform", slot="event_name", value=event["summary"]))
                        date = datetime.fromisoformat(event["start"]["dateTime"]).date()
                        dial.action.append(DAI(intent="inform", slot="event_date", value=str(date)))                        
                        start = datetime.fromisoformat(event["start"]["dateTime"])
                        dial.action.append(DAI(intent="inform", slot="event_start", value=start.strftime("%H:%M")))
                        end = datetime.fromisoformat(event["end"]["dateTime"])
                        dial.action.append(DAI(intent="inform", slot="event_end", value=end.strftime("%H:%M")))
                    
                    # Reset the state
                    super(Dialogue, dial).__setattr__('state', dotdict({}))

                    if events:
                        # If there is any, save the event id for further use
                        dial.state["id"] = events[0]["id"]
                    else:
                        # If there's no event with such name, inform about it
                        dial.action.append(DAI(intent="inform", slot="no_events", value=None))

                else:
                    # Ask about the missing slots
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))


            elif goal == "add_event":
                slots_needed = ["name", "date", "time_start", "time_end"]
                if not (missing_slots := check_slots(dial, slots_needed)):
                    if not self.confirmed:
                        # Let user confirm action and all slots
                        dial.action.append(DAI(intent="ask", slot="confirm_add", value=None))
                        ask_confirmation_slots(dial, self, slots_needed)
                        self.asked_confirmation = True
                    else:
                        # When confirmed, create the event
                        if "repeating" in dial.state:
                            event = create_event(dial.state["name"], dial.state["date"], dial.state["time_start"], dial.state["time_end"], dial.state["place"], dial.state["repeating"])
                        else:
                            event = create_event(dial.state["name"], dial.state["date"], dial.state["time_start"], dial.state["time_end"], "Praha", None)

                        # call the API and add the event, infrom the user that successfull
                        event_add = self.service.events().insert(calendarId='primary', body=event).execute()
                        if event_add:
                            dial.action.append(DAI(intent="inform", slot="succ_add", value=None))                        
                        else:
                            dial.action.append(DAI(intent="error", slot="unsucc_add", value=None))
                        
                        # Reset everything, keep the id of the added event
                        self.asked_confirmation, self.confirmed = False, False     
                        super(Dialogue, dial).__setattr__('state', dotdict({}))
                        dial.state["id"] = event_add["id"]

                else:
                    # Ask about the missing slots
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))


            elif goal == "change_event":
                slots_needed = ["id"]
                if not (missing_slots := check_slots(dial, slots_needed)):
                    if not self.confirmed:
                        # Let user confirm action and all slots
                        dial.action.append(DAI(intent="ask", slot="confirm_change", value=None))
                        ask_confirmation_slots(dial, self, slots_needed)
                        slots_possible = ["name", "date", "time_start"]
                        for slot in slots_possible:
                            if slot in dial.state:
                                dial.action.append(DAI(intent="ask", slot="confirm_new_" + slot, value=dial.state[slot]))
                        self.asked_confirmation = True
                    else:
                        # When confirmed, retrieve the event
                        event = self.service.events().get(calendarId='primary', eventId=dial.state["id"]).execute()
                        # Change the values where desired
                        if "name" in dial.state:
                            event["summary"] = dial.state["name"]
                        if "place" in dial.state:
                            event["location"] = dial.state["place"]
                        if "date" in dial.state:
                            orig_start = datetime.fromisoformat(event["start"]["dateTime"])
                            orig_end = datetime.fromisoformat(event["end"]["dateTime"])
                            duration = orig_end - orig_start
                            if "time_start" in dial.state:
                                start = dial.state["date"] + '-' + dial.state["time_start"]
                            else:
                                start = dial.state["date"] + '-' + datetime.fromisoformat(event["start"]["dateTime"]).strftime("%H:%M")
                            start = datetime.strptime(start, "%Y-%m-%d-%H:%M")
                            event["start"]["dateTime"] = start.astimezone().isoformat('T')
                            if "time_end" in dial.state:
                                end = str(orig_end.date()) + '-' + dial.state["time_end"]
                                event["end"]["dateTime"] = datetime.strptime(end, "%Y-%m-%d-%H:%M").astimezone().isoformat('T')
                            else:
                                event["end"]["dateTime"] = (start + duration).astimezone().isoformat('T')
                        elif "time_start" in dial.state:
                            orig_start = datetime.fromisoformat(event["start"]["dateTime"])
                            orig_end = datetime.fromisoformat(event["end"]["dateTime"])
                            duration = orig_end - orig_start
                            start = datetime.strptime((str(orig_start.date()) + '-' + dial.state["time_start"]), "%Y-%m-%d-%H:%M")                            
                            event["start"]["dateTime"] = start.astimezone().isoformat('T')
                            if "time_end" in dial.state:
                                end = str(orig_end.date()) + '-' + dial.state["time_end"]
                                event["end"]["dateTime"] = datetime.strptime(end, "%Y-%m-%d-%H:%M").astimezone().isoformat('T')
                            else:
                                event["end"]["dateTime"] = (start + duration).astimezone().isoformat('T')
                            event["end"]["dateTime"] = (start + duration).astimezone().isoformat('T')

                        # Call the API and insert the updated event, infrom the user that successfull
                        updated_event = self.service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                        if updated_event:
                            dial.action.append(DAI(intent="inform", slot="succ_change", value=None))
                        else:
                            dial.action.append(DAI(intent="error", slot="unsucc_change", value=None))
                        
                        # Reset everything except the id
                        self.asked_confirmation, self.confirmed = False, False
                        id = dial.state["id"]
                        super(Dialogue, dial).__setattr__('state', dotdict({}))
                        dial.state["id"] = id

                else:
                    # Ask about the missing slots
                    for missing_slot in missing_slots:
                        dial.action.append(DAI(intent="ask", slot=missing_slot, value=None))


            elif goal == "delete_event":
                slots_needed = ["id"]
                if not (missing_slots := check_slots(dial, slots_needed)):
                    if not self.confirmed:
                        # Let user confirm action and all slots
                        dial.action.append(DAI(intent="ask", slot="confirm_del", value=None))
                        ask_confirmation_slots(dial, self, slots_needed)
                        self.asked_confirmation = True
                    else:
                        # When confirmed, call the API and delete the event, infrom the user that successfull
                        self.service.events().delete(calendarId='primary', eventId=dial.state["id"]).execute()
                        dial.action.append(DAI(intent="inform", slot="succ_del", value=None))

                        # Reset everything
                        self.asked_confirmation, self.confirmed = False, False
                        super(Dialogue, dial).__setattr__('state', dotdict({}))

                else:
                    # Ask about the missing slots
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
        if da.intent == "confirm" and da.slot == "value" and da.value:
            confirmed = True
    return confirmed

def check_slots(dial, slots):
    # Check if the values for asked slots are known
    # If not, return missing slots

    missing_slots = []

    for slot in slots:
        if not slot in dial.state:
            missing_slots.append(slot)
    
    return missing_slots

def ask_confirmation_slots(dial, policy_object, slots):
    # Confirm the values of the slots
    for slot in slots:
        if slot != "id":
            dial.action.append(DAI(intent="ask", slot=("confirm_" + slot), value=dial.state[slot]))  
        else:
            event = policy_object.service.events().get(calendarId='primary', eventId=dial.state["id"]).execute()
            dial.action.append(DAI(intent="inform", slot="confirm_old_name", value=event["summary"]))
            start = datetime.fromisoformat(event["start"]["dateTime"])
            dial.action.append(DAI(intent="inform", slot="confirm_old_time_start", value=start.strftime("%H:%M")))
            end = datetime.fromisoformat(event["end"]["dateTime"])
            dial.action.append(DAI(intent="inform", slot="confirm_old_time_end", value=end.strftime("%H:%M")))
            dial.action.append(DAI(intent="inform", slot="confirm_old_date", value=str(start.date())))

def create_event(name, date, time_start, time_end, place, repeating):
    start = date + '-' + time_start
    start = datetime.strptime(start, "%Y-%m-%d-%H:%M").astimezone().isoformat('T')
    end = date + '-' + time_end
    end = datetime.strptime(end, "%Y-%m-%d-%H:%M").astimezone().isoformat('T')
    event = {
                'summary': name,
                'location': place,
                'start': {
                    'dateTime': start
                },
                'end': {
                    'dateTime': end
                }
            }
    if repeating == "day":
        event['reccurence'] = ['RRULE:FREQ=DAILY']
    elif repeating == "week":
        event['reccurence'] = ['RRULE:FREQ=WEEKLY']
    elif repeating == "month":
        event['reccurence'] = ['RRULE:FREQ=MONTHLY']
    elif repeating == "year":
        event['reccurence'] = ['RRULE:FREQ=YEARLY']

    return event