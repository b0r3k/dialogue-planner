#!/usr/bin/env python3

import sys
import time
import json
from abc import ABC

from ..component import Component


class ConsoleInput(Component):
    """Input from the console, following a text prompt."""

    def __call__(self, *args, **kwargs):
        time.sleep(.05)
        return input('USER INPUT> ').strip().lower()


class FileInput(Component, ABC):
    def __len__(self):
        raise NotImplementedError


class PlainFileInput(FileInput):
    """Input from a file, default to standard input (one turn per line)."""

    def __init__(self, config=None):
        super(PlainFileInput, self).__init__(config)
        self.input_fd = sys.stdin
        # input is not from standard input
        if self.config and 'input_file' in self.config and self.config['input_file'] not in ['', '-']:
            self.input_fd = open(self.config['input_file'], 'r', encoding='UTF-8')
            self._len = sum(1 for _ in self.input_fd)
            self.input_fd.fd.seek(0)

    def __call__(self, *args, **kwargs):
        line = self.input_fd.readline()
        if line == '':  # EOF hit
            return None
        return line.strip().lower()

    def __len__(self):
        return self._len

    def __del__(self):
        self.input_fd.close()


class SimpleJSONInput(FileInput):
    """Input from a JSON, expected format: list of dictionaries, using the
    'usr' key to provide as the input."""

    def __init__(self, config=None):
        super(SimpleJSONInput, self).__init__(config)

        with open(self.config['input_file'], 'rt', encoding='UTF-8') as fd:
            self.data = json.load(fd)
            self._len = len(self.data)
        self.gen = self.get_data_gen()

    def __len__(self):
        return self._len

    def get_data_gen(self):
        for x in self.data:
            yield x

    def __call__(self, *args, **kwargs):
        try:
            x = next(self.gen)
            return x['usr']
        except (StopIteration, KeyError):
            return None
