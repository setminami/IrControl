# -*- coding: utf-8 -*-
# this made for python3
import logging

LOGLV = logging.INFO

def module_logger(modname):
    logger = logging.getLogger(modname)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s | %(levelname)s] %(message)s',
                                    datefmt='%y%M%dT%H%M%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOGLV)
    return logger
