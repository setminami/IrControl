#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this made for python3

import os, sys, argparse
import yaml

from timer import LEDLightDayTimer
from remote import Remote

VERSION = "1.0"

_BASE = os.path.dirname(os.path.abspath(__file__))
SETTING = os.path.normpath(os.path.join(_BASE, '../../settings/ledlight.yml'))

class RGBControl(object):

    def __init__(self, timer, setting=None):
        if __name__ == '__main__':
            self.ARGS = RGBControl.ArgParser()
            config_path = self.ARGS.configure
        else:
            assert setting is not None
            config_path = setting

        with open(config_path, "r") as f:
          params = yaml.load(f)
          self.PARAMS = self.expand_env(params)
        print(self.PARAMS)
        timer.timezone = self.PARAMS['TIMEZONE']
        self.myTimer = timer
        self.remotes = {}
        for x in self.PARAMS['KEYCODE']:
            remote = Remote()
            remote.setupKeycode(x)
            self.remotes[x['name']] = remote

    def expand_env(self, params):
        for key, val in params.items():
            print('try %s, %s'%(key, val))
            if isinstance(val, dict):
                print('ORDEREDDICT')
                return self.expand_env(val)
            elif isinstance(val, list):
                print('LIST')
                return [self.expand_env(x) for x in val]
            elif isinstance(val, str) and (val.startswith('${') \
                    and val.endswith('}')):
                print('LEAF')
                env_key = val[2:-1]
                if env_key in os.environ.keys():
                    params[key] = os.environ[val[2:-1]]
                    msg = f('Overwrite env value {val} = {params[key]}')
                    print(msg)
                return params
            else:
                print('?? TYPE is %s'%type(val))

    def organize_settings(self):
        """
        organize yaml settings
        """
        self.rgb_light = self.remotes['ledlight']
        self.weather = WeatherInfo(self.PARAMS['SUNLIGHT_STATUS_API'], self.PARAMS['TIMEZONE'])
        today_sunrise, today_sunset = self.weather.sunrize, self.weather.sunset

    @staticmethod
    def ArgParser():
        argParser = argparse.ArgumentParser(prog=__file__,
            description='Control ledlight with infra-red remote',
            usage='%s -v -c [setting file name by yaml]'%__file__)
        # Version desctiprtion
        argParser.add_argument('-v', '--version',
            action='version',
            version='%s'%VERSION)
        argParser.add_argument('-c', '--configure',
            nargs='?', type=str, default=SETTING,
            help='config file that wrote by yaml describe params, see default=%s'%SETTING)
        return argParser.parse_args()

if __name__ == '__main__':
    ins = RGBControl(LEDLightDayTimer())
    pass
