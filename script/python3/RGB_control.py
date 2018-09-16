#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this made for python3

import os, sys, argparse, yaml

from util.env import expand_env
from util.timer import LEDLightDayTimer
from util.remote import Remote

VERSION = "1.0"

_BASE = os.path.dirname(os.path.abspath(__file__))
SETTING = os.path.normpath(os.path.join(_BASE, '../../settings/ledlight.yml'))

DEBUG = True

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

          self.PARAMS = expand_env(params, DEBUG)
        print('>> {}'.format(self.PARAMS))
        timer.timezone = self.PARAMS['TIMEZONE']
        self.myTimer = timer
        self.remotes = {}
        for x in self.PARAMS['KEYCODE']:
            remote = Remote()
            remote.setupKeycode(x)
            self.remotes[x['name']] = remote

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
