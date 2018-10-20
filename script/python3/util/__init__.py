# -*- coding: utf-8 -*-
# this made for python3
import logging
from os import uname, path
from enum import Enum
from json import dumps
from datetime import datetime


def is_debug(sysname='Darwin'):
    """ for device debug """
    return uname().sysname == sysname


_BASE = path.dirname(path.abspath(__file__))
# for avoid virtualenv
SETTING = path.normpath(path.join(_BASE, '../../../settings/ledlight.yml'))
ONEW_DEVICE_PATH = path.normpath('/sys/bus/w1/devices/{}/w1_slave') if not is_debug() else \
                    path.normpath(path.join(_BASE, '../../../environment/w1_demo'))


def module_logger(modname):
    logger = logging.getLogger(modname)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s | %(name)s | %(levelname)s] %(message)s',
                                    datefmt='%y%m%dT%H%M%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if is_debug() else logging.INFO)
    return logger


# out of SunlightControl subPrj.
def output_path(file_name):
    return path.normpath(path.join(path.join(_BASE, '../../../../outputs'), file_name))


class DumpFile(Enum):
    schedule = output_path('schedules.{}.json')
    live_settings = output_path('livesettings.{}.json')

    def _timestamped_file(self):
        return self.value.format(datetime.now().strftime('%y%m%dT%H%M%S_%f'))

    def dump_json_file(self, obj):
        p = self._timestamped_file()
        with open(self._timestamped_file(), 'w') as f:
            f.write(dumps(obj))


# to control semi-state_fully with IFTTT + tuya Device for Smart plugs
class SmartPlug:
    """ CONTRACT: IFTTT service name must be {plug_name}_{on|off} """

    def __init__(self, name):
        self._name = name
        self._status = self.Status.UNKNOWN
        pass

    @property
    def name(self): return self._name

    @property
    def status(self): return self._status

    @status.setter
    def status(self, state): self._status = state

    class Status(Enum):
        ON, OFF, UNKNOWN = 'on', 'off', 'unknown'