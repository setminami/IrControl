# -*- coding: utf-8 -*-
# this made for python3

from os import environ, path
from enum import Enum
from PIL import ImageFont

from util import is_debug

_BASE = path.dirname(path.abspath(__file__))
# for avoid virtualenv
SETTING = path.normpath(path.join(_BASE, '../../../settings/ledlight.yml'))
ONEW_DEVICE_PATH = path.normpath('/sys/bus/w1/devices/{}/w1_slave') if not is_debug() else \
                    path.normpath(path.join(_BASE, '../../../environment/w1_demo'))


# out of SunlightControl subPrj.
def schedule_output_path(file_name):
    return path.normpath(path.join(path.join(_BASE, '../../../../outputs'), file_name))


def expand_env(params, verbose=False):
    """ dotenv like function, but not dotenv """
    for key, val in params.items():
        _print(f'try {key}, {val}', verbose)
        if isinstance(val, dict):
            _print('ORDEREDDICT', verbose)
            params[key] = expand_env(val, verbose)
        elif isinstance(val, list):
            _print('LIST', verbose)
            params[key] = [expand_env(x, verbose) for x in val]
        elif isinstance(val, str) and (val.startswith('${') \
                and val.endswith('}')):
            _print('LEAF', verbose)
            env_key = val[2:-1]
            if env_key in list(environ.keys()):
                params[key] = environ[env_key]
                _print(f'Overwrite env value {val} = ***', verbose)
                _print('If not fire IFTTT triggers, Plase re-check your own IFTTT key settings.')
            else:
                _print(f'## {env_key} not exported for {key}. Please check your yaml file and env. ##', verbose)
                _print(f'Env {env_key} vs keys = {list(environ.keys())}', verbose)
                exit(1)
        else:
            _print(f'?? {val} TYPE is {type(val)}', verbose)
    return params

def _print(msg, v=False):
    if v: print(msg)

class DrawType(Enum):
    CLOCK = 'CLOCK'

    def preprocessor(self):
        # TODO: generalize each draw type args
        # write each comment as args tuple and copy'n pasetes for tuple declarations in draw_display
        if self == DrawType.CLOCK: # clock_frame_color express (active, inactive)
            font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf' \
                if not is_debug() else '/System/Library/Fonts/Apple Braille.ttf'
            font_small = ImageFont.truetype(font_path, 8, encoding="unic")
            font_large = ImageFont.truetype(font_path, 12, encoding="unic")
            # an_lineheight, margin, height_max, cx, base_angle, R, sch_plot_R, R_ratio, \
            #   label_text, clock_frame_color, needle_color, sec_needle_color, text_color, font1, font2
            return (8, 4, 64, 30, 270, 30, 3, 0.667, \
                    'Next:', ('#F7FE2E', '#424242'), 'white', '#FE2E2E', 'white', font_small, font_large)
        else:
            return ()

class TemperatureUnits(Enum):
    """
    DS18B20 outputs as Celsius value x 10^3
    Comversion: 1.8C + 32 = F
    """
    C = 'Celsius'
    F = 'Fahrenheit'

    def value_with_mark(self, value, adp=1):
        """
        adp means 'after decimal point'
        return value as appropriate unit, with mark
        """
        form = '{:2.' + str(adp) + 'f}' + ('°' + self.value[0])
        return form.format(self._convert_as_float(value))

    def _convert_as_float(self, value):
        if self == TemperatureUnits.C:
            return float(value)
        elif self == TemperatureUnits.F:
            return float(value) * 1.80 + 32.00
