#!/usr/bin/env python3


class ConsoleOutput(object):

    def __init__(self, *args):
        super(ConsoleOutput, self).__init__()

    def __call__(self, utterance, *args, **kwargs):
        print('SYSTEM:', utterance)


class FileOutput:

    def __init__(self, config, *args):
        super(FileOutput, self).__init__()
        self.config = config
        self.out_fd = open(self.config['output_fn'], 'wt')

    def __call__(self, utterance, *args, **kwargs):
        print(utterance, file=self.out_fd)

    def __del__(self):
        self.out_fd.close()

