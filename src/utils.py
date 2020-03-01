import logging


def load_conf(conf_path):
    return {'logging_level': 'DEBUG'}


def setup_logging(conf):
    logger = logging.getLogger(__name__)
    logging_level = conf['logging_level'] if 'logging_level' in conf else 'NOTSET'
    logging.basicConfig(level=logging_level, format='%(asctime)-15s %(message)s')
    return logger

def run_for_n_iterations(n):
    return lambda handler: handler.iterations < n
