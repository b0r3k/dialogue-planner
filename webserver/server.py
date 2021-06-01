#!/usr/bin/env python3

import time
import uuid
from flask import Flask, send_from_directory, send_file, session, request, abort
from argparse import ArgumentParser
from collections import defaultdict

from dialmonkey.conversation_handler import ConversationHandler
from dialmonkey.utils import load_conf
from dialmonkey.dialogue import Dialogue


app = Flask(__name__)
app.secret_key = b'445234uedoeh#&$HEDU'  # replace this before using

# WORKER_ADDRS = ['http://localhost:8123', 'http://localhost:8124']
# TIMEOUT = 60


# class Workers:

#     def __init__(self):
#         self.workers = [{'addr': worker_addr, 'last_used': 0, 'sessid': None}
#                         for worker_addr in WORKER_ADDRS]
#         self.sessid_to_worker = {}

#     def get_worker(self, sessid):
#         now = time.time()
#         try:
#             worker = self.sessid_to_worker[sessid]
#         except KeyError:
#             worker = None
#             for w in self.workers:
#                 if w['last_used'] < now - TIMEOUT:
#                     worker = w
#                     break
#         if worker:
#             if worker['sessid'] in self.sessid_to_worker:
#                 del self.sessid_to_worker[worker['sessid']]
#             self.sessid_to_worker[sessid] = worker
#             worker['sessid'] = sessid
#             worker['last_used'] = now
#             return worker
#         return None


# workers = Workers()


@app.route('/request', methods=['GET', 'POST'])
def process_request():
    global handler, dialogues
    # handle the session id
    sessid = session.get('sessid', uuid.uuid4())
    session['sessid'] = sessid

    rqst = request.json
    response = None
    now = time.time()
    if "start_session" in rqst:
        # new session, start new dialog
        dial = Dialogue()
        response, _ = handler.get_response(dial, "pomoc")
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
        print(rqst["user"])
        if sessid in dialogues:
            dial = Dialogue()
            dial.load_from_serialized(dialogues[sessid]["dial"])
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
    config = load_conf("conf/planner.yaml")
    handler = ConversationHandler(config)
    dialogues = defaultdict(dict)

    ap = ArgumentParser()
    ap.add_argument('-p', '--port', type=int, default=8122)
    args = ap.parse_args()
    app.run(host='localhost', port=args.port)
