import logging
import sys


def setup_logger(module_name: str) -> logging.Logger:
    LOGGER = logging.getLogger(module_name)
    LOGGER.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s: %(message)s - src:%(name)s '
        '[line %(lineno)s]'
    )

    stdout_handler.setFormatter(formatter)
    LOGGER.addHandler(stdout_handler)

    return LOGGER
