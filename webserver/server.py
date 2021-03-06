#!/usr/bin/env python3

import pickle
import time
import uuid
from flask import Flask, send_from_directory, send_file, session, request, abort
from argparse import ArgumentParser
from collections import defaultdict
from google_auth_oauthlib.flow import Flow
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from copy import deepcopy



from dialmonkey.conversation_handler import ConversationHandler
from dialmonkey.utils import load_conf
from dialmonkey.dialogue import Dialogue


app = Flask(__name__)
app.secret_key = b'445234uedoeh#&$HEDU'  # replace this before using

@app.route('/request', methods=['GET', 'POST'])
def process_request():
    global config, dialogues
    # handle the session id
    sessid = session.get('sessid', uuid.uuid4())
    session['sessid'] = sessid

    rqst = request.json
    print(rqst)
    response = None
    now = time.time()
    if "authenticate" in rqst:
        # Create flow object and save it
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        flow = Flow.from_client_secrets_file('examples-testing/credentials.json', scopes=SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        dialogues[sessid]["flow"] = flow
        # Get the authorization link and give it to the user
        link = flow.authorization_url()
        response = f"Pro autorizaci prosím otevřete <a href={link[0]}>tento link</a> v nové záložce a kód vložte do vstupního pole."

    elif "start_session" in rqst:
        # Retrieve the code from user input and the saved flow object
        user_code = rqst["user"]
        flow = dialogues[sessid]["flow"]
        # Try to fetch the token
        try:
            flow.fetch_token(code=user_code)
        except OAuth2Error:
            response = "Bohužel, tento kód se mi nepovedlo ověřit, systém nebude fungovat. Začněte znovu obnovením stránky."
            del dialogues[sessid]
        else:
            config = deepcopy(config)
            # Find the Policy component
            index = next(i for i, comp in enumerate(config["components"]) if "dialmonkey.policy.planner_server.PlannerPolicy" in comp)
            # Dump the credentials as a config for the Policy component
            config["components"][index]["dialmonkey.policy.planner_server.PlannerPolicy"]["creds"] = pickle.dumps(flow.credentials)
            response = "Úspěšně ověřeno! Nyní můžete manipulovat s kalendářem."
            # Delete the flow object, not needed anymore
            del dialogues[sessid]["flow"]

            # new session, start new dialog
            dial = Dialogue()
            handler = ConversationHandler(config)
            dialogues[sessid]["handler"] = handler
            dialogues[sessid]["dial"] = dial.serialize()
            dialogues[sessid]["last_used"] = now

            # check all the dialogues, delete older than cca 3 minutes
            to_delete = []
            for dial in dialogues:
                if dialogues[dial]["last_used"] < now - 180:
                    to_delete.append(dial)
            for dial in to_delete:
                del dialogues[dial]
            
    elif "end_session" in rqst:
        if sessid in dialogues:
            del dialogues[sessid]
        response = "Nashledanou!"

    elif "user" in rqst:
        if sessid in dialogues:
            dial = Dialogue()
            dial.load_from_serialized(dialogues[sessid]["dial"])
            handler = dialogues[sessid]["handler"]
            response, _ = handler.get_response(dial, rqst["user"])
            dialogues[sessid]["dial"] = dial.serialize()
            dialogues[sessid]["last_used"] = now

    if not response:
        abort(500)

    return {"system": response}


@app.route('/')
def return_index():
    return send_file('index.html')


if __name__ == '__main__':
    config = load_conf("conf/planner_server.yaml")
    dialogues = defaultdict(dict)

    ap = ArgumentParser()
    ap.add_argument('-p', '--port', type=int, default=8122)
    args = ap.parse_args()
    app.run(host='localhost', port=args.port)
