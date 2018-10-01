# -*- coding: utf-8 -*-
# this made for python3
import logging, os

def is_debug(sysname='Darwin'):
    """ for device debug """
    return os.uname().sysname == sysname

def module_logger(modname):
    logger = logging.getLogger(modname)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s | %(name)s | %(levelname)s] %(message)s',
                                    datefmt='%y%m%dT%H%M%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if is_debug() else logging.INFO)
    return logger
