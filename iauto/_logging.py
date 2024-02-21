import logging
import os

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN
FATAL = logging.FATAL


def get_level(name: str):
    if name is None:
        return logging.INFO

    name = name.strip().upper()
    if name == 'DEBUG':
        return logging.DEBUG
    elif name == 'INFO':
        return logging.INFO
    elif name == 'WARN' or name == 'WARNING':
        return logging.WARN
    elif name == 'ERROR':
        return logging.ERROR
    elif name == 'FATAL' or name == 'CRITICAL':
        return logging.FATAL
    else:
        return logging.NOTSET


def get_logger(name, level=None):
    level = level or os.environ.get("IA_LOG_LEVEL") or "INFO"
    log_level = get_level(level) or logging.INFO
    logger = logging.getLogger(name=name)
    logger.setLevel(level=log_level)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s'))
    handler.setLevel(level=log_level)
    logger.addHandler(handler)

    return logger


logger = get_logger("ia", level=os.environ.get("IA_LOG_LEVEL") or "INFO")
