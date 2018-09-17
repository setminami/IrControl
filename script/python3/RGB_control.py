#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this made for python3

import os, sys, argparse, yaml, subprocess as sp

from util.env import expand_env
from util.timer import LEDLightDayTimer
from util.remote import Remote
from util.weather_info import WeatherInfo

VERSION = "1.0"

_BASE = os.path.dirname(os.path.abspath(__file__))
SETTING = os.path.normpath(os.path.join(_BASE, '../../settings/ledlight.yml'))

DEBUG = False

class RGBControl(object):

    def __init__(self, timer, setting=None):
        if __name__ == '__main__':
            self.ARGS = RGBControl.ArgParser()
            self.config_path = self.ARGS.configure
        else:
            assert setting is not None
            self.config_path = setting

        with open(self.config_path, "r") as f:
          params = yaml.load(f)
          self.PARAMS = expand_env(params, DEBUG)

        timer.timezone = self.PARAMS['TIMEZONE']
        self.remotes = {}
        # restrict update lircd for runnning
        irsend = sp.check_output(['which', self.PARAMS['IRSEND_CMD']]).decode('utf-8')[:-1]
        ifttt = self.PARAMS['IFTTT']
        for x in self.PARAMS['KEYCODE']:
            remote = Remote(irsend, ifttt['path'], ifttt['key'])
            remote.setup_ir_keycodes(x)
            self.remotes[x['name']] = remote
        timer.remote = self.remotes['ledlight']
        self.myTimer = timer

    def update_settings(self):
        """
        organize yaml settings
        An item which expected realtime update, describe here istead of __init__
        """
        with open(self.config_path, "r") as f:
          params = yaml.load(f)
          self.PARAMS = expand_env(params, DEBUG)

        self.myTimer.weather = WeatherInfo(self.PARAMS['SUNLIGHT_STATUS_API'],
                                            self.PARAMS['TIMESHIFTS'],
                                            self.PARAMS['TIMEZONE'])
        # NOTE: overwrite onetime per day
        self.myTimer.update_time = self.PARAMS['UPDATE_TIME']
        self.myTimer.do_schedule()
        pass

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
    ins.update_settings()
    pass
