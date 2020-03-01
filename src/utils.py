def load_conf(conf_path):
    return {'logging_level': 'DEBUG'}


def run_for_n_iterations(n):
    return lambda handler: handler.iterations < n
