# 📅 Dialogue planner
Task-oriented dialogue system for calendar management in Czech language based on [Dialmonkey framework](https://gitlab.com/ufal/dsg/dialmonkey), [MorphoDiTa](https://ufal.mff.cuni.cz/morphodita) is used for lemmatization.

## Usage
First make sure all [requirements](/requirements.txt) are satisfied, this can be accomplished by running `pip install -r requirements.txt`, prefereably in _venv_ or something similar.

The best way to try Planner out is to run `python3 webserver/server.py` and then access `localhost:8122` in the web browser, all the instructions are provided there.

Another option is to try it out in console, run `python3 run_dialmonkey.py --conf conf/planner.yaml`. Then input czech text with diacritics and interpunction, e.g.: _„co mám v plánu zítra?“_ The casing of letters does not matter.

### Authentication
Since the Planner uses [Google Calendar API](https://developers.google.com/calendar/overview) to communicate with the calendar, authentication to the google account is necessary. The app is in the test mode, so only accounts listed as testers can authenticate. You can either contact me or use dialogue.planner.testing@gmail.com with password being the first heading of this README (without the emoji and using `-` instead of space).

## How it works
The Planner has 4 units cooperating:
- NLU (natural language understanding) takes the user input and tries to extract the meaning in triples intent-slot-value from the natural language.
- DST (dialogue state tracker) remembers the slot-values from previous utterances, possibly updates them.
- DP (dialogue policy) decides what action to take based on the state and current output of NLU.
- NLG (natural language generation) is template-driven - it uses output of DP and slot-values from state to fill in a template with sentences in natural language, possibly combining more templates. Then it fills in the system response.

## Examples
Examples of behaviour of each unit can be found in [examples-testing](/examples-testing).