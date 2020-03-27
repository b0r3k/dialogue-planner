#!/usr/bin/env python3

import sys
from ..component import Component


class ConsoleOutput(Component):
    """Print the output to the console, following a 'SYSTEM:' prompt, one utterance per line."""

    def __init__(self, *args):
        super(ConsoleOutput, self).__init__()

    def __call__(self, utterance, *args, **kwargs):
        print('SYSTEM:', utterance)


class FileOutput:
    """Print output to the given file (default to stdout), one utterance per line."""

    def __init__(self, config, *args):
        super(FileOutput, self).__init__()
        self.config = config
        self.output_fd = sys.stdout
        if config and config.get('output_file', '') not in ['', '-']:
            self.output_fd = open(self.config['output_file'], 'wt')

    def __call__(self, utterance, *args, **kwargs):
        print(utterance, file=self.output_fd)

    def __del__(self):
        self.output_fd.close()
