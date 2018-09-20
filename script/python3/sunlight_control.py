#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this made for python3

import os, sys, argparse, yaml, subprocess as sp, threading
from datetime import datetime, timedelta

from util.env import expand_env
from util.timer import LEDLightDayTimer
from util.remote import Remote
from util.weather_info import WeatherInfo
from util import module_logger
from util.display_ssd1331.as_clock import Screen

from time import sleep

__VERSION__ = "1.0"

_BASE = os.path.dirname(os.path.abspath(__file__))
SETTING = os.path.normpath(os.path.join(_BASE, '../../settings/ledlight.yml'))

DEBUG = False

class SunlightControl(object):

    def __init__(self, timer, per_sec, setting=None):
        if __name__ == '__main__':
            self.ARGS = SunlightControl.ArgParser()
            self.config_path = self.ARGS.configure
        else:
            assert setting is not None
            self.config_path = setting

        with open(self.config_path, "r") as f:
          params = yaml.load(f)
          self.PARAMS = expand_env(params, DEBUG)

        self._per_sec = per_sec # to check every _perse
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

        self.stop_event = threading.Event()
        self._thread = threading.Thread(target=self.run, args=())
        self._thread.setDaemon(True)

    @property
    def timer(self):
        assert hasattr(self, '_timer')
        return self._timer

    @property
    def check_per_sec(self):
        assert hasattr(self, '_per_sec')
        return self._per_sec

    @property
    def active_schedules(self):
        i = 0
        while not hasattr(self, '_active_schedules'):
            if i == 500:
                print('cannot set active schedule')
                exit(1)
            else:
                i += 1
            sleep(0.1)
        return self._active_schedules
    @active_schedules.setter
    def active_schedules(self, val):
        self._active_schedules = val

    @property
    def thread(self):
        assert hasattr(self, '_thread')
        return self._thread

    def start(self):
        assert hasattr(self, '_thread')
        self._thread.start()
        return self

    def kill(self):
        assert hasattr(self, 'stop_event')
        self.stop_event.set()

    # operate transferred instance
    def _setup_wether_info(self, day):
        # TODO: check memory usage
        self._timer.weather = WeatherInfo(day, self.PARAMS['SUNLIGHT_STATUS_API'],
                                            self.PARAMS['TIMESHIFTS'],
                                            self.PARAMS['TIMEZONE'])

    def _scheduling(self):
        return self._timer.do_schedule()


    def update_settings(self, day):
        """
        organize yaml settings
        An item which expected realtime update, describe here istead of __init__
        """
        with open(self.config_path, "r") as f:
          params = yaml.load(f)
          self.PARAMS = expand_env(params, DEBUG)

        self._setup_wether_info(day)
        return self._scheduling()

    def run(self):
        day = datetime.now(self.timer.timezone)
        self.active_schedules = None
        while not self.stop_event.is_set():
            if self.timer.is_usedup():
                self.logger.info('Schedules set for day: %s'%day.strftime('%Y-%m-%d'))
                self.active_schedules = self.update_settings(day)
                self.logger.info('Schedules = {}'.format(self.active_schedules))

            if self.active_schedules is not None:
                sleep(self.check_per_sec) # check new schedules per
            else:
                # search active day to fetch astronomy data
                day += timedelta(days=1)
                continue

    @staticmethod
    def ArgParser():
        argParser = argparse.ArgumentParser(prog=__file__,
            description='Control ledlight with infra-red remote',
            usage='%s -v -c [setting file name by yaml]'%__file__)
        # Version desctiprtion
        argParser.add_argument('-v', '--version',
            action='version',
            version='%s'%__VERSION__)
        argParser.add_argument('-c', '--configure',
            nargs='?', type=str, default=SETTING,
            help='config file that wrote by yaml describe params, see default=%s'%SETTING)
        return argParser.parse_args()

def kill_thread(threading_instance):
    if threading_instance.thread.isAlive():
        threading_instance.kill()

if __name__ == '__main__':
    ins = None
    try:
        ins = SunlightControl(LEDLightDayTimer(), 30 * 60).start()
        print('XXX')
        ins2 = Screen(ins.active_schedules)
        ins.thread.join()
    except KeyboardInterrupt:
        if ins is not None: kill_thread(ins)
        print('Caught KeyboardInterrupt. schedules were cancelled.')
