#!/usr/bin/env python3


from flask import Flask, send_from_directory, send_file
from flask import jsonify
app = Flask(__name__)


@app.route('/request', methods = ['GET', 'POST'])
def process_request():
    return jsonify({'system': 'Test response'})

@app.route('/<path:path>')
def return_file(path):
    return send_from_directory('', path)

@app.route('/')
def return_index():
    return send_file('index.html')

if __name__ == '__main__':
   app.run()
