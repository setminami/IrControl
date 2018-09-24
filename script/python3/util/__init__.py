# -*- coding: utf-8 -*-
# this made for python3
import logging, os

LOGLV = logging.DEBUG if os.uname().sysname == 'Darwin' else logging.INFO

def module_logger(modname):
    logger = logging.getLogger(modname)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s | %(name)s | %(levelname)s] %(message)s',
                                    datefmt='%y%m%dT%H%M%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOGLV)
    return logger
