#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this made for python3

import os, sys, argparse, yaml, math, time, subprocess as sp
# from multiprocessing import Process, Event
from threading import Thread, Event
from datetime import datetime, timedelta

from util.env import expand_env
from util.timer import LEDLightDayTimer
from util.remote import Remote
from util.weather_info import WeatherInfo
from util import module_logger
if os.uname().sysname == 'Darwin':
    print('## the ENV Cannot use luma library ##')
    from display.dummy_opts import get_device
else:
    from luma.core.render import canvas
    from display.demo_opts import get_device

from time import sleep

__VERSION__ = "1.0"

_BASE = os.path.dirname(os.path.abspath(__file__))
SETTING = os.path.normpath(os.path.join(_BASE, '../../settings/ledlight.yml'))

DEBUG = False

class SunlightControl(Thread):

    def __init__(self, timer, per_sec, update_event, setting=None):
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
        self._update_event = update_event
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
        super().__init__()

    @property
    def updated(self):
        assert hasattr(self, '_update_event')
        return self._update_event

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
        assert hasattr(self, '_active_schedules')
        return self._active_schedules
    @active_schedules.setter
    def active_schedules(self, val):
        self._active_schedules = val

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
        while True:
            if self.timer.is_usedup():
                self.logger.info('Schedules set for day: %s'%day.strftime('%Y-%m-%d'))
                self.active_schedules = self.update_settings(day)
                self.updated.set() # new schedules were setuped
                self.logger.info('Schedules = {}'.format(self.active_schedules))

            if len(self.active_schedules) > 0:
                sleep(self.check_per_sec) # check new schedules per
            else:
                # search active day to fetch astronomy data
                day += timedelta(days=1)

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


class Screen(Thread):
    def __init__(self, update_event, sunctrl):
        self._device = get_device(['-d', 'ssd1331', '-i', 'spi', '--width', '96', '--height', '64'])
        self._update_event = update_event
        self._sunctrl = sunctrl
        super().__init__()

    @property
    def updated(self):
        assert hasattr(self, '_update_event')
        return self._update_event

    @property
    def device(self):
        assert hasattr(self, '_device')
        return self._device

    def posn(self, angle, arm_length):
        dx = int(math.cos(math.radians(angle)) * arm_length)
        dy = int(math.sin(math.radians(angle)) * arm_length)
        return (dx, dy)


    def run(self):
        today_last_time = "Unknown"
        device = self.device
        an_lineheight = 8

        while True:
            now = datetime.now()
            today_time = now.strftime("%H:%M:%S")
            if today_time != today_last_time:
                today_last_time = today_time
                with canvas(device) as draw:
                    now = datetime.now()
                    schs = None
                    if self.updated.is_set():
                        # SunlightControl.active_schedules is ready
                        # get most recent schedule for future
                        schs = ins.active_schedules
                        self.updateed.clear()
                    if (schs is not None) and len(schs) > 0:
                        print('Schedules = {}'.format(schs))

                    today_date = now.strftime("%y%m%d")

                    margin = 4

                    cx = 30
                    cy = min(device.height, 64) / 2

                    left = cx - cy
                    right = cx + cy

                    hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
                    hrs = self.posn(hrs_angle, cy - margin - 7)

                    min_angle = 270 + (6 * now.minute)
                    mins = self.posn(min_angle, cy - margin - 2)

                    sec_angle = 270 + (6 * now.second)
                    secs = self.posn(sec_angle, cy - margin - 2)
                    # dimension ssd1331 96 x 64
                    draw.ellipse((left + margin, margin, right - margin, min(device.height, 64) - margin), outline="yellow")
                    draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
                    draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
                    draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="cyan")
                    draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill="white", outline="white")

                    # literal infos
                    draw.text((1.8 * (cx + margin), cy - an_lineheight * 4), 'next:', fill="yellow")
                    draw.text((1.8 * (cx + margin), cy - an_lineheight * 2), today_date, fill="yellow")
                    draw.text((2 * (cx + margin), cy), today_time, fill="yellow")
            time.sleep(0.1)

if __name__ == '__main__':
    # use like shared flag
    update = Event()
    try:
        # preprocess
        print('#####')

        ins = SunlightControl(LEDLightDayTimer(), 30 * 60, update)
        ins.setDaemon(True)
        ins2 = Screen(update, ins)
        ins2.setDaemon(True)
        print('%%%%%')
        # ins.start()
        # ins.join(5)
        print('XXX')
        ins2.start()
        ins.start()
        # ins2.join()
    except KeyboardInterrupt:
        ins.join(1)
        ins2.join(1)
        print('Caught KeyboardInterrupt. schedules were cancelled.')
