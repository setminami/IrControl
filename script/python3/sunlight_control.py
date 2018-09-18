#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this made for python3

import os, sys, argparse, yaml, subprocess as sp
from datetime import datetime, timedelta

from util.env import expand_env
from util.timer import LEDLightDayTimer
from util.remote import Remote
from util.weather_info import WeatherInfo
from util import module_logger

from time import sleep

VERSION = "1.0"

_BASE = os.path.dirname(os.path.abspath(__file__))
SETTING = os.path.normpath(os.path.join(_BASE, '../../settings/ledlight.yml'))

DEBUG = False

class SunlightControl(object):

    def __init__(self, timer, setting=None):
        if __name__ == '__main__':
            self.ARGS = SunlightControl.ArgParser()
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
        irsend = 'echo' if os.uname().sysname == 'Darwin' \
            else sp.check_output(['which', self.PARAMS['IRSEND_CMD']]).decode('utf-8')[:-1]
        ifttt = self.PARAMS['IFTTT']
        for x in self.PARAMS['KEYCODE']:
            remote = Remote(irsend, ifttt['path'], ifttt['key'])
            remote.setup_ir_keycodes(x)
            self.remotes[x['name']] = remote
        timer.remote = self.remotes['ledlight']
        self._timer = timer
        self.logger = module_logger(__name__)

    @property
    def timer(self):
        return self._timer

    # operate transferred instance
    def _setup_wether_info(self, day):
        # TODO: check memory usage
        self._timer.weather = WeatherInfo(day, self.PARAMS['SUNLIGHT_STATUS_API'],
                                            self.PARAMS['TIMESHIFTS'],
                                            self.PARAMS['TIMEZONE'])

    def _scheduling(self):
        self._timer.do_schedule()


    def update_settings(self, day):
        """
        organize yaml settings
        An item which expected realtime update, describe here istead of __init__
        """
        with open(self.config_path, "r") as f:
          params = yaml.load(f)
          self.PARAMS = expand_env(params, DEBUG)

        self._setup_wether_info(day)
        self._scheduling()

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
    ins = SunlightControl(LEDLightDayTimer())
    day = datetime.now(ins.timer.timezone)
    while True:
        if ins.timer.is_usedup():
            ins.logger.info('Schedules set:')
            x = ins.update_settings(day)
            ins.logger.info(x)

        if x is not None:
            sleep(30 * 60) # check per 30min
        else:
            day += timedelta(days=1)
            continue
    pass
