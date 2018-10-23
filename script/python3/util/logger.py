import logging
from os import path
from pythonjsonlogger import jsonlogger

from . import is_debug, _BASE


# for avoid virtualenv
JSON_LOGGING_PATH = path.normpath(path.join(_BASE, '../../../../log/SunLight.json'))


def module_logger(modname):
    log = logging.getLogger(modname)
    handler = logging.StreamHandler()
    json_handler = logging.FileHandler(JSON_LOGGING_PATH)
    formatter = logging.Formatter('[%(asctime)s | %(name)s | %(levelname)s] %(message)s', datefmt='%y%m%dT%H%M%S')
    handler.setFormatter(formatter)
    json_formatter = jsonlogger.JsonFormatter()
    json_handler.setFormatter(json_formatter)
    log.addHandler(handler)
    log.addHandler(json_handler)
    log.setLevel(logging.DEBUG if is_debug() else logging.INFO)
    return log

