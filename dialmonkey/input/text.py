#!/usr/bin/env python3

import sys
import json


class ConsoleInput(object):

    def __init__(self, *args):
        super(ConsoleInput, self).__init__()

    def __call__(self, *args, **kwargs):
        return input('USER INPUT> ').strip().lower()


class FileInput(object):

    def __init__(self, *args):
        super(FileInput, self).__init__()

    def __call__(self, *args, **kwargs):
        return sys.stdin.readline().strip().lower()


class SimpleJSONInput(object):

    def __init__(self, config, *args):
        super(SimpleJSONInput, self).__init__()
        self.config = config
        with open(self.config['input_data_fn'], 'rt') as fd:
            self.data = json.load(fd)
        self.gen = self.get_data_gen()

    def get_data_gen(self):
        for x in self.data:
            yield x

    def __call__(self, *args, **kwargs):
        x = next(self.gen)
        if x is not None:
            return x['usr']
        else:
            return ''
