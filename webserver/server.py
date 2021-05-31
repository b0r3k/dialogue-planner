#!/usr/bin/env python3

import time
import uuid
import requests
from flask import Flask, send_from_directory, send_file, session, request, jsonify, abort
from argparse import ArgumentParser


app = Flask(__name__)
app.secret_key = b'445234uedoeh#&$HEDU'  # replace this before using

WORKER_ADDRS = ['http://localhost:8123', 'http://localhost:8124']
TIMEOUT = 60


class Workers:

    def __init__(self):
        self.workers = [{'addr': worker_addr, 'last_used': 0, 'sessid': None}
                        for worker_addr in WORKER_ADDRS]
        self.sessid_to_worker = {}

    def get_worker(self, sessid):
        now = time.time()
        try:
            worker = self.sessid_to_worker[sessid]
        except KeyError:
            worker = None
            for w in self.workers:
                if w['last_used'] < now - TIMEOUT:
                    worker = w
                    break
        if worker:
            if worker['sessid'] in self.sessid_to_worker:
                del self.sessid_to_worker[worker['sessid']]
            self.sessid_to_worker[sessid] = worker
            worker['sessid'] = sessid
            worker['last_used'] = now
            return worker
        return None


workers = Workers()


@app.route('/request', methods=['GET', 'POST'])
def process_request():
    sessid = session.get('sessid', uuid.uuid4())
    session['sessid'] = sessid
    worker = workers.get_worker(sessid)
    if not worker:
        abort(503)
    r = requests.post(worker['addr'], json=request.json)
    if r.status_code != 200:
        abort(r.status_code)
    return jsonify(r.json())


@app.route('/<path:path>')
def return_file(path):
    return send_from_directory('', path)


@app.route('/')
def return_index():
    return send_file('index.html')


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-p', '--port', type=int, default=8122)
    args = ap.parse_args()
    app.run(host='localhost', port=args.port)
