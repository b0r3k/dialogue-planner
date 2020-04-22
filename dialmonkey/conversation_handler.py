#!/usr/bin/env python3

import logzero
import json
import time

from .dialogue import Dialogue
from .utils import dynload_class
from .component import Component
from .da import DA


class ConversationHandler(object):
    """A helper class that calls the individual dialogue system components and thus
    runs the whole dialogue. Its behavior is defined by the config file, the contents
    of which are passed in the constructor."""

    def __init__(self, config, logger=None, should_continue=None):
        self.config = config
        self.logger = logger if logger is not None else logzero.logger
        self.history_fn = 'history-{}.json'.format(int(time.time())) \
            if 'history_fn' not in self.config else self.config['history_fn']
        self.should_continue = should_continue if should_continue is not None else lambda _: True

        # setup input stream
        if 'user_stream_type' not in self.config:
            self.config['user_stream_type'] = 'dialmonkey.input.text.ConsoleInput'
        try:
            self.user_stream = dynload_class(self.config['user_stream_type'])(self.config)
        except Exception as e:
            self.logger.error('Could not load class "%s"', self.config['user_stream_type'])
            raise e

        # setup output stream
        if 'output_stream_type' not in self.config:
            self.config['output_stream_type'] = 'dialmonkey.output.text.ConsoleOutput'
        try:
            self.output_stream = dynload_class(self.config['output_stream_type'])(self.config)
        except Exception as e:
            self.logger.error('Could not load class "%s"', self.config['output_stream_type'])
            raise e

        self._load_components()
        self._reset()

    def main_loop(self):
        """
        Main loop of the program.
        While `self.should_continue` call returns true, runs the conversation with fresh Dialogue
        and maintains the history.
        :return: None
        """
        class JSONEnc(json.JSONEncoder):
            """Helper class to ensure encoding of DA objects (as strings)."""
            def default(self, obj):
                if isinstance(obj, DA):
                    return obj.to_cambridge_da_string()

        while self.should_continue(self):
            self.logger.debug('Dialogue %d', self.iterations)
            dial = Dialogue()
            final_dial = self.run_dialogue(dial)
            self.history.append(final_dial['history'])
            self.iterations += 1
        with open(self.history_fn, 'wt') as of:
            json.dump(self.history, of, indent=4, ensure_ascii=False, cls=JSONEnc)

    def _init_components(self, dial: Dialogue):
        for component in self.components:
            dial = component.init_dialogue(dial)

    def _reset_components(self):
        for component in self.components:
            component.reset()

    def get_response(self, dial: Dialogue, user_utterance: str):
        is_ok = True
        dial.set_user_input(user_utterance)
        # run the dialogue pipeline (all components from the config)
        for component in self.components:
            dial = component(dial, self.logger)
        if dial['system'] is None or len(dial['system']) == 0:
            self.logger.error('System response not filled by the pipeline!')
            is_ok = False
        system_response = dial['system']
        dial.end_turn()
        eod = dial.eod or\
                ('break_words' in self.config and any([kw in user_utterance for kw in self.config['break_words']]))
        return system_response, not is_ok or eod

    def run_dialogue(self, dial: Dialogue):
        """
        With a given initial Dialogue object, runs the conversation loop until the end of dialogue flag is set.
        First all components are initialized with the given Dialogue object.
        Then subsequently reads the user stream, and calls all the components provided in the configuration.
        The conversation loop is terminated by setting the end of dialogue,
        using a break word or providing empty user input.
        All the components need to be reset after each dialogue, they are NOT INSTANTIATED here.
        :param dial: initial Dialogue
        :return: final Dialogue
        """
        eod = False
        system_response = ""
        self._init_components()

        while not eod:
            # get a user utterance from the input stream
            user_utterance = self.user_stream(system_response)
            if user_utterance is None:
                self.logger.info('Input file ended.')
                break
            self.logger.info('USER: %s', user_utterance)
            system_response, eod = self.get_response(dial, user_utterance)
            self.logger.info('SYSTEM: %s', system_response)
            self.output_stream(system_response)

        self.logger.info('Dialogue ended.')
        self._reset_components()

        return dial

    def _reset(self):
        self.iterations = 1
        self.history = []

    def _load_components(self):
        self.components = []
        if 'components' not in self.config:
            return
        for comp in self.config['components']:
            if isinstance(comp, dict):  # component has some configuration options (key=name, value=options)
                comp_name, comp_params = next(iter(comp.items()))
            else:  # component has no configuration options
                comp_name, comp_params = comp, None
            component_cls = dynload_class(comp_name)
            if component_cls is None:
                self.logger.error('Could not find class "%s"', comp)
            else:
                component = component_cls(comp_params)
                assert isinstance(component, Component),\
                    'Provided component has to inherit from the abstract class components.Component'
                self.components.append(component)
