#!/usr/bin/env python3

import logging
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

    def __init__(self, conf, logger, should_continue=None):
        self.conf = conf
        self.logger = logger
        self.logging_level = 'DEBUG' if 'logging_level' not in self.conf else self.conf['logging_level']
        self.history_fn = 'history-{}.json'.format(int(time.time())) \
            if 'history_fn' not in self.conf else self.conf['history_fn']
        self._setup_logging()
        if should_continue is not None:
            self.should_continue = should_continue
        else:
            self.should_continue = lambda _: True

        # setup input stream
        if 'user_stream' not in self.conf:
            self.conf['user_stream'] = 'dialmonkey.input.text.ConsoleInput'
        try:
            self.user_stream = dynload_class(self.conf['user_stream'])(self.conf)
        except Exception as e:
            print(e)
            self.logger.error('Could not load class "%s"', self.conf['user_stream'])

        # setup output stream
        if 'output_stream' not in self.conf:
            self.conf['output_stream'] = 'dialmonkey.output.text.ConsoleOutput'
        try:
            self.output_stream = dynload_class(self.conf['output_stream'])(self.conf)
        except:
            self.logger.error('Could not load class "%s"', self.conf['output_stream'])

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
        last_system = ""
        for component in self.components:
            dial = component.init_dialogue(dial)
        while not eod:
            # get a user utterance from the input stream
            time.sleep(.05)
            user_utterance = self.user_stream(last_system)
            self.logger.info('USER: %s', user_utterance)
            dial.set_user_input(user_utterance)
            # run the dialogue pipeline (all components from the config)
            for component in self.components:
                dial = component(dial, self.logger)
                ConversationHandler._assert_is_valid_dial(dial)
            if dial['system'] is None or len(dial['system']) == 0:
                # TODO: should be assert here?
                logging.error('System response not filled by the pipeline!')
                break
            # print system response to the output stream
            last_system = dial['system']
            self.logger.info('SYSTEM: %s', last_system)
            self.output_stream(last_system)
            dial.end_turn()
            # TODO: should we set maximum number of turns?
            eod = dial.eod or \
                ('break_words' in self.conf and any([kw in user_utterance for kw in self.conf['break_words']]))
        self.logger.info('Dialogue ended.')
        for component in self.components:
            component.reset()
        return dial

    def _reset(self):
        self.iterations = 1
        self.history = []

    def _load_components(self):
        self.components = []
        if 'components' not in self.conf:
            return
        for comp in self.conf['components']:
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

    def _setup_logging(self):
        """
        Setup logger level and formatting.
        if `logging_fn` is set, logger output is forked to the respective file.
        :return:
        """
        if 'logging_fn' in self.conf:
            file_handler = logging.FileHandler(self.conf['logging_fn'])
            self.logger.addHandler(file_handler)
        for handler in self.logger.handlers:
            handler.setLevel(getattr(logging, self.logging_level))

    @staticmethod
    def _assert_is_valid_dial(dial):
        assert isinstance(dial, Dialogue), 'Returned Dialogue object is not valid'
        for attr in Dialogue.essential_attributes():
            assert hasattr(dial, attr), 'Returned dialogue does not have the attribute {}'.format(attr)
