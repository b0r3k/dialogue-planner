#!/usr/bin/env python3

import argparse
import os

from dialmonkey.utils import load_conf, run_for_n_iterations, setup_logging
from dialmonkey.conversation_handler import ConversationHandler


def main(args):
    if not os.path.exists(args.conf):
        print('Provided configuration file "{}" does not exist! Exiting.'.format(args.conf))
        return
    # load configuration
    conf = load_conf(args.conf)

    # setup logging
    if args.logging_level:
        conf['logging_level'] = args.logging_level
    elif 'logging_level' not in conf:
        conf['logging_level'] = 'NOTSET'
    logger = setup_logging(conf['logging_level'])

    # setup input & output streams
    if args.user_stream_type:
        conf['user_stream_type'] = args.user_stream_type
    if args.input_file:
        conf['input_file'] = args.input_file
    if args.output_stream_type:
        conf['output_stream_type'] = args.output_stream_type
    if args.output_file:
        conf['output_file'] = args.output_file
    # run the conversation(s)
    handler = ConversationHandler(conf, logger, should_continue=run_for_n_iterations(args.num_dials))
    handler.main_loop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Dialmonkey system with a specified configuration file')
    parser.add_argument('--conf', type=str, required=True,
                        help='Path to YAML configuration file with system components definition')
    parser.add_argument('-n', '--num-dials', '--num', type=int, default=1,
                        help='Number of dialogues to run')
    parser.add_argument('-v', '--logging-level', '--verbosity', '--log-level', type=str,
                        choices=['ERROR', 'INFO', 'WARN', 'DEBUG', 'NOTSET'],
                        help='Logging level/verbosity (overriding config defaults)')
    parser.add_argument('-I', '--user-stream-type', '--input-stream-type', '--input-type', type=str,
                        help='Component class to use as input stream (overriding config defaults)')
    parser.add_argument('-O', '--output-stream-type', '--output-type', type=str,
                        help='Component class to use as output stream (overriding config defaults)')
    parser.add_argument('-i', '--input-file', type=str,
                        help='Path to input file (argument to input stream class), if applicable')
    parser.add_argument('-o', '--output-file', type=str,
                        help='Path to output file (argument to output stream class), if applicable')

    args = parser.parse_args()
    main(args)
