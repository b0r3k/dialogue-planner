import logging
import json
import time

from .state import DialogueState
from .utils import dynload_class


class ConversationHandler(object):

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
        # TODO: can be configurable callable
        stream_loaded = False
        if 'user_stream' in self.conf:
            user_stream_cls = dynload_class(self.conf['user_stream'])
            if user_stream_cls is None:
                self.logger.error('Could not find class "%s"', self.conf['user_stream'])
            else:
                self.user_stream = user_stream_cls()
                stream_loaded = True
        if not stream_loaded:
            self.user_stream = lambda _:  input('USER> ').strip().lower()

        self._load_components()
        self._reset()

    def main_loop(self):
        while self.should_continue(self):
            self.logger.debug('Dialogue %d', self.iterations)
            state = DialogueState()
            final_state = self.run_dialogue(state)
            self.history.append(final_state['history'])
            self.iterations += 1
        with open(self.history_fn, 'wt') as of:
            json.dump(self.history, of)

    def run_dialogue(self, state):
        eod = False
        last_system = ""
        for component in self.components:
            state = component.init_state(state)
        while not eod:
            time.sleep(.05)
            user_utterance = self.user_stream(last_system)
            self.logger.info('USER: %s', user_utterance)
            state.set_user_input(user_utterance)
            for component in self.components:
                state = component(state, self.logger)
                ConversationHandler._assert_is_valid_state(state)
            if state['system'] is None:
                logging.error('System response not filled by the pipeline!')
                break
            last_system = state['system']
            print('SYSTEM:', last_system)
            self.logger.info('SYSTEM: %s', last_system)
            state.end_turn()
            # TODO: should we set maximum number of turns?
            eod = state.eod or \
                len(user_utterance) == 0 or \
                any([kw in user_utterance for kw in ['quit', 'exit', 'stop']])
        self.logger.info('Dialogue ended.')
        for component in self.components:
            component.reset()
        return state

    def _reset(self):
        self.iterations = 1
        self.history = []

    def _load_components(self):
        self.components = []
        if 'components' not in self.conf:
            return
        for comp in self.conf['components']:
            component_cls = dynload_class(comp)
            if component_cls is None:
                self.logger.error('Could not find class "%s"', comp)
            else:
                self.components.append(component_cls())

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
    def _assert_is_valid_state(state):
        assert isinstance(state, DialogueState), 'Returned state is not valid'
        for attr in DialogueState.essential_attributes():
            assert hasattr(state, attr), 'Returned state does not have the attribute {}'.format(attr)
