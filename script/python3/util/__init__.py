# -*- coding: utf-8 -*-
# this made for python3
import logging, pytz
from os import uname, path, rename
from enum import Enum
from json import dumps
from datetime import datetime
from pythonjsonlogger import jsonlogger


def is_debug(sysname='Darwin'):
    """ for device debug """
    return uname().sysname == sysname


_BASE = path.dirname(path.abspath(__file__))
# for avoid virtualenv
SETTING = path.normpath(path.join(_BASE, '../../../config/ledlight.yml'))
ONEW_DEVICE_PATH = path.normpath('/sys/bus/w1/devices/{}/w1_slave') if not is_debug() else \
                    path.normpath(path.join(_BASE, '../../../environment/w1_demo'))
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


logger = module_logger('sunlight_control')


# out of SunlightControl subPrj.
def output_path(file_name):
    return path.normpath(path.join(path.join(_BASE, '../../../../outputs'), file_name))


class DumpFile(Enum):
    schedule = output_path('schedules.json')
    live_settings = output_path('livesettings.json')

    def _timestamped_file(self):
        return self.value.replace('.json', datetime.now(pytz.utc).strftime('%y%m%dT%H%M%S_%f%Z') + '.json')

    def dump_json_file(self, obj):
        ts = datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        key = 'timestamp'
        if isinstance(obj, list):
            obj.append({key: ts})
        elif isinstance(obj, dict):
            obj[key] = ts
        else:
            assert True, f'Unknown obj has encountered {obj}'

        if path.exists(self.value):
            rename(self.value, self._timestamped_file())
        with open(self.value, 'w') as f:
            f.write(dumps(obj))
