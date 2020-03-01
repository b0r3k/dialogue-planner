import argparse
import logging
from src.utils import load_conf, run_for_n_iterations, setup_logging
from src.conversation_handler import ConversationHandler

def main(args):
    conf = load_conf(args.conf)
    logger = setup_logging(conf)
    handler = ConversationHandler(conf, logger, should_continue=run_for_n_iterations(5))
    handler.main_loop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', type=str, required=True)
    args = parser.parse_args()
    main(args)
