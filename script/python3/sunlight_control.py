#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this made for python3

import os, sys, argparse, yaml, math, time, subprocess as sp
# from multiprocessing import Process, Event
from threading import Thread, Event
from multiprocessing import Pool
from datetime import datetime, timedelta
from enum import Enum

from util.env import expand_env
from util.timer import LEDLightDayTimer
from util.remote import Remote
from util.weather_info import WeatherInfo
from util import module_logger
if os.uname().sysname == 'Darwin':
    print('## the ENV Cannot use luma library ##')
    from display.dummy_for_macOS import get_device, canvas
else:
    from luma.core.render import canvas
    from display.demo_opts import get_device

from time import sleep

__VERSION__ = "1.0"

_BASE = os.path.dirname(os.path.abspath(__file__))
SETTING = os.path.normpath(os.path.join(_BASE, '../../settings/ledlight.yml'))

DEBUG = False
class DrawType(Enum):
    CLOCK = 1

    def preprocessor(self):
        # TODO: generalize each draw type args
        # write each comment as args tuple and copy'n pasetes for tuple declarations in draw_display
        if self == DrawType.CLOCK:
            # an_lineheight, margin, height_max, cx, base_angle, PM_R, AM_R, label_text, clock_frame_color, needle_color, sec_needle_color, text_color
            return (8, 4, 64, 30, 270, 30, 20, 'Next:', 'yellow', 'white', 'red', 'white')
        else:
            return ()

class SunlightControl(Thread):

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

        self._device = get_device(['-d', 'ssd1331', '-i', 'spi', '--width', '96', '--height', '64'])
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
        self.kill_received = False
        self.logger = module_logger(__class__.__name__)
        super().__init__()

    @property
    def timer(self):
        assert hasattr(self, '_timer')
        return self._timer

    @property
    def timezone(self):
        assert hasattr(self.timer, 'timezone')
        return self.timer.timezone

    @property
    def check_per_sec(self):
        assert hasattr(self, '_per_sec')
        return self._per_sec

    # sorted by time
    @property
    def active_schedules(self):
        if hasattr(self, '_active_schedules') and \
            self._active_schedules is not None:
            return sorted([x for x in self._active_schedules if x.time > datetime.now().timestamp()], key = lambda x: x.time)
        else:
            return []
    @active_schedules.setter
    def active_schedules(self, val):
        self._active_schedules = val

    # display control
    @property
    def device(self):
        assert hasattr(self, '_device')
        return self._device

    def posn(self, angle, arm_length):
        dx = int(math.cos(math.radians(angle)) * arm_length)
        dy = int(math.sin(math.radians(angle)) * arm_length)
        return (dx, dy)

    # operate transferred instance
    def _setup_wether_info(self, day):
        # TODO: check memory usage
        TIMESHIFTS = 'TIMESHIFTS' if os.uname().sysname != 'Darwin' else 'TIMESHIFTS_for_debg'
        self._timer.weather = WeatherInfo(day, self.PARAMS['SUNLIGHT_STATUS_API'],
                                            self.PARAMS[TIMESHIFTS],
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

    def core_process(self, draw_type):
        self.active_schedules = None
        today_last_time = "Unknown"
        device = self.device

        args = draw_type.preprocessor()

        self.logger.debug('check {}'.format(self))
        while not self.kill_received:
            now = datetime.now(self.timer.timezone)
            if self.timer.is_usedup():
                day = now
                while len(self.active_schedules) == 0:
                    self.logger.info('Schedules set for day: %s'%day.strftime('%Y-%m-%d'))
                    self.active_schedules = self.update_settings(day)
                    if len(self.active_schedules) > 0:
                        break
                    else:
                        # search active day to fetch astronomy data
                        day += timedelta(days=1)
                        continue
                self.logger.info('Schedules = {}'.format(self.active_schedules))

            today_time = now.strftime('%H:%M:%S') # draw per seconds
            if today_time != today_last_time:
                today_last_time = today_time
                self.draw_display(draw_type, args)

            sleep(0.1)

    def draw_display(self, draw_type, args):
        device = self.device
        with canvas(device) as draw:
            if draw_type == DrawType.CLOCK:
                an_lineheight, margin, height_max, cx, base_angle, PM_R, AM_R, \
                label_text, clock_frame_color, needle_color, sec_needle_color, text_color, \
                    = args
                now = datetime.now(self.timer.timezone)
                today_date = now.strftime("%y%m%d")
                today_time = now.strftime('%H:%M:%S')
                schs = None
                if (self.active_schedules is not None) and \
                        (len(self.active_schedules) > 0):
                    # SunlightControl.active_schedules is ready
                    # head is most recent schedule for future
                    schs = [(x.argument[:2],  datetime.fromtimestamp(x.time, tz=self.timezone)) for x in self.active_schedules if x.time > now.timestamp()]
                else: return

                name, time = schs[0]
                cy = min(device.height, height_max) / 2

                left = cx - cy
                right = cx + cy

                hrs_angle = base_angle + (30 * (now.hour + (now.minute / 60.0)))
                hrs = self.posn(hrs_angle, cy - margin - 7)

                min_angle = base_angle + (6 * now.minute)
                mins = self.posn(min_angle, cy - margin - 2)

                sec_angle = base_angle + (6 * now.second)
                secs = self.posn(sec_angle, cy - margin - 2)
                # dimension ssd1331 96 x 64
                # to see drawer funcs signeture, see. https://pillow.readthedocs.io/en/latest/reference/ImageDraw.html
                # because of luma.core.canvas implementation. (see also)
                # PM circle (x - cx)^2 + (y - cy)^2 = PM_R^2
                origin = (cx, cy)
                draw.ellipse(self._circular(PM_R, origin), outline=clock_frame_color)

                # AM circle, This circle must be concentric with PM circle
                draw.ellipse(self._circular(AM_R, origin), outline='blue')

                draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill=needle_color)
                draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill=needle_color)
                draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill=sec_needle_color)
                # clock origin
                draw.ellipse(self._circular(2, origin), fill="white", outline="white")

                # literal infos
                # print Most Recent Schedule's name & time
                draw.text((1.8 * (cx + margin), cy - an_lineheight * 4), label_text, fill=text_color)
                DISPLAY = 1 # only for readability
                display_name, display_color = name[DISPLAY]['shorten_name'], name[DISPLAY]['color']
                draw.text((1.8 * (cx + margin), cy - an_lineheight * 2.4), display_name, fill=display_color, outline=text_color)
                self.logger.debug(display_name)
                # output most recent schedule's name
                dateform, timeform = '%y%m%d', '%H:%M'
                draw.text((1.8 * (cx + margin), cy - an_lineheight * 1), time.strftime(dateform), fill=text_color)
                self.logger.debug(time.strftime(dateform))
                draw.text((1.9 * (cx + margin), cy), time.strftime(timeform), fill=text_color)
                self.logger.debug(time.strftime(timeform))

                # plot schedules on ellipse
                self._plot_schedule(draw, origin, 0, PM_R, AM_R, schs)

    def _circular(self, r, origin):
        return (tuple([x - r for x in origin]), tuple([x + r for x in origin]))

    def _plot_schedule(self, draw, origin, base_angle, PM_R, AM_R, schedules):
        """ plot schedules on ellipse """
        DISPLAY = 1
        for s in schedules:
            name, time = s
            color = name[DISPLAY]['color']
            R = AM_R if time.hour < 12 else PM_R
            draw.ellipse(self._plot_on_circle(origin, base_angle, R, 1.5, time), fill=color)

    def _plot_on_circle(self, origin, base_angle, R, plot_R, time):
        """
        12h = 720min => 1min as degree = (360/720) = 0.5 = 1/2
                             as radian = (2pi/720) = 2.777778pi * 10^-3
        0:00 -> origin: (Ox, Oy + R)
        0:05 -> origin: (Ox + Rsin(deg:0.5 * 5), Oy + Rcos(deg:0.5 * 5))
        ∴
        N:M -> origin: passed_min=(N * 60 + M), (Ox + Rsin(deg:passed_min/2), Oy + Rcos(deg:passed_min/2))
        (however, origin is left-down )
        """
        Ox, Oy = origin
        h12 = time.hour if time.hour < 12 else (time.hour - 12)
        # as radian
        # passed_min = (h12 * 60 + time.minute) * 0.002777778 * math.pi
        # degree to radian
        passed_min = math.radians((h12 * 60 + time.minute) / 2 + base_angle)
        # here, axis origin is left-up, -> Oy - .... 
        return self._circular(plot_R, (Ox + math.sin(passed_min) * R, Oy - math.cos(passed_min) * R))

    def run(self):
        self.core_process(DrawType.CLOCK)

    def kill(self):
        self.kill_received = True

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

if __name__ == '__main__':
    # use like shared flag
    kill = Event()
    try:
        # ins.setDaemon(True)
        ins = SunlightControl(LEDLightDayTimer(), 30 * 60)
        # ins.setDaemon(True)

        ins.start()
        ins.join()
    except KeyboardInterrupt:
        ins.kill()
        print('Caught KeyboardInterrupt. schedules were cancelled.')
        exit(0)
