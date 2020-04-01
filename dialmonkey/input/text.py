#!/usr/bin/env python3

import sys
import json
from ..component import Component
import time


class ConsoleInput(Component):
    """Input from the console, following a text prompt."""

    def __call__(self, *args, **kwargs):
        time.sleep(.05)
        return input('USER INPUT> ').strip().lower()


class FileInput(Component):
    """Input from a file, default to standard input (one turn per line)."""

    def __init__(self, config=None):
        super(FileInput, self).__init__(config)
        self.input_fd = sys.stdin
        # input is not from standard input
        if self.config and 'input_file' in self.config and self.config['input_file'] not in ['', '-']:
            self.input_fd = open(self.config['input_file'], 'r', encoding='UTF-8')

    def __call__(self, *args, **kwargs):
        line = self.input_fd.readline()
        if line == '':  # EOF hit
            return None
        return line.strip().lower()

    def __del__(self):
        self.input_fd.close()


class SimpleJSONInput(Component):
    """Input from a JSON, expected format: list of dictionaries, using the
    'usr' key to provide as the input."""

    def __init__(self, config=None):
        super(SimpleJSONInput, self).__init__(config)
        with open(self.config['input_file'], 'rt', encoding='UTF-8') as fd:
            self.data = json.load(fd)
        self.gen = self.get_data_gen()

    def get_data_gen(self):
        for x in self.data:
            yield x

    def __call__(self, *args, **kwargs):
        try:
            x = next(self.gen)
            return x['usr']
        except (StopIteration, KeyError):
            return None
