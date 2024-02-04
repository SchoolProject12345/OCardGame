import logging
from colorlog import ColoredFormatter


def setup_logger():
    formatter = ColoredFormatter(
        "%(log_color)s[%(levelname)s] %(message)s",
        datefmt='%H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
    )
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
