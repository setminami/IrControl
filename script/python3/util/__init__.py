# -*- coding: utf-8 -*-
# this made for python3
from os import uname, path


def is_debug(sysname='Darwin'):
    """ for device debug """
    return uname().sysname == sysname


_BASE = path.dirname(path.abspath(__file__))
ONEW_DEVICE_PATH = path.normpath('/sys/bus/w1/devices/{}/w1_slave') if not is_debug() else \
                    path.normpath(path.join(_BASE, '../../../environment/w1_demo'))
SETTING = path.normpath(path.join(_BASE, '../../../config/ledlight.yml'))
# for avoid virtualenv
JSON_LOGGING_PATH = path.normpath(path.join(_BASE, '../../../../log/SunLight.json'))

from . import logger
logger = logger.module_logger('sunlight_control')