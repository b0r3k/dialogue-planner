#!/usr/bin/env python3

class ConsoleOutput:

    def __call__(self, utterance, *args, **kwargs):
        print('SYSTEM:', utterance)


class FileOutput:

    def __call__(self, utterance, *args, **kwargs):
        print(utterance)

