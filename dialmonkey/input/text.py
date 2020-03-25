#!/usr/bin/env python3

import sys

class ConsoleInput:

    def __call__(self, *args, **kwargs):
        return input('USER INPUT> ').strip().lower()

class FileInput:

    def __call__(self, *args, **kwargs):
        return sys.stdin.readline().strip().lower()
