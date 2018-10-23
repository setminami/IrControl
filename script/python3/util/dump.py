from datetime import datetime
from enum import Enum
from json import dumps
from os import path, rename
import pytz

from . import _BASE


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

