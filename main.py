import argparse
import logging
from src.utils import load_conf, run_for_n_iterations
from src.handler import Handler

def main(args):
    logger = logging.getLogger(__name__)
    conf = load_conf(args.conf)
    logging_level = conf['logging_level'] if 'logging_level' in conf else 'NOTSET'
    logging.basicConfig(level=logging_level, format='%(asctime)-15s %(message)s')

    handler = Handler(conf, logger, should_continue=run_for_n_iterations(5))
    handler.main_loop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', type=str, required=True)
    args = parser.parse_args()
    main(args)
