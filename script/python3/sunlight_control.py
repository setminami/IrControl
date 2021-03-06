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
from util.thermo_info import ThermoInfo
from util import module_logger, is_debug

if is_debug():
    print('## the ENV Cannot use luma library ##')
    from display.dummy_for_macOS import get_device, canvas
else:
    from luma.core.render import canvas
    from display.demo_opts import get_device

from PIL import ImageFont
from time import sleep

__VERSION__ = "1.0"

_BASE = os.path.dirname(os.path.abspath(__file__))
# for avoid virtualenv
SETTING = os.path.normpath(os.path.join(_BASE, '../../settings/ledlight.yml')) \
                if not is_debug() else os.path.expanduser('~/Github/SunlightControl/settings/ledlight.yml')

DEBUG = False

class DrawType(Enum):
    CLOCK = 1

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

_SLEEP = 0.5
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
          self.PARAMS = expand_env(params, True)

        self._device = get_device(['-d', 'ssd1331', '-i', 'spi', '--width', '96', '--height', '64'])
        self._per_sec = per_sec # to check every _perse
        timer.timezone = self.PARAMS['TIMEZONE']
        self.remotes = {}
        # restrict update lircd for runnning
        irsend, httpcmd = 'echo' if is_debug() \
            else sp.check_output(['which', self.PARAMS['IRSEND_CMD']]).decode('utf-8')[:-1], \
            '{} -sl'.format(sp.check_output(['which', 'curl']).decode('utf-8')[:-1])
        ifttt = self.PARAMS['IFTTT']
        for x in self.PARAMS['KEYCODE']:
            remote = Remote(irsend, httpcmd, ifttt['path'], ifttt['key'])
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

    def is_usedup(self):
        return len(self.active_schedules) == 0

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
        TIMESHIFTS = 'TIMESHIFTS' if not is_debug() else 'TIMESHIFTS_for_debg'
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
          self.PARAMS = expand_env(params, True)

        self._setup_wether_info(day)
        return self._scheduling()

    def core_process(self, draw_type):
        if DEBUG:
            import tracemalloc
            tracemalloc.start()

        self.active_schedules = None
        today_last_time = "Unknown"
        tank_temp = None

        args = draw_type.preprocessor()

        self.logger.debug('check {}'.format(self))
        # Debug
        display_name, dateform, timeform, sch_len = "", "", "", 0

        while not self.kill_received:
            if DEBUG:
                snap1 = tracemalloc.take_snapshot()
            now = datetime.now(self.timer.timezone)
            if self.is_usedup():
                self.logger.debug('########### is_usedup() ################')
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
            else:
                if sch_len != len(self.active_schedules):
                    self.logger.debug('num of remaining schedules = {}'.format(len(self.active_schedules)))
                    sch_len = len(self.active_schedules)

            crc = tank_temp[1] if tank_temp is not None else None
            with ThermoInfo('28-0417004c49ff', crc) as thermo: _tank_temp = thermo.check()
            tank_temp = _tank_temp if _tank_temp is not None else tank_temp

            today_time = now.strftime('%H:%M:%S') # draw per seconds
            if today_time != today_last_time:
                today_last_time = today_time
                literal_outputs = self.draw_display(self.device,
                                                    draw_type,
                                                    args,
                                                    u'%2.1fC'%tank_temp[0], is_debug())
                if is_debug() and (literal_outputs != (display_name, dateform, timeform)):
                    display_name, dateform, timeform = literal_outputs
                    self.logger.debug(display_name)
                    self.logger.debug(dateform)
                    self.logger.debug(timeform)
            if DEBUG:
                snap2 = tracemalloc.take_snapshot()
                stats = snap2.compare_to(snap1, 'lineno')
                [print(s) for s in stats]
            sleep(_SLEEP)

    def draw_display(self, device, draw_type, args, temperature, is_debug):
        with canvas(device) as draw:
            if draw_type == DrawType.CLOCK:
                an_lineheight, margin, height_max, cx, base_angle, \
                R, sch_plot_R, R_ratio, label_text, \
                clock_frame_color, needle_color, sec_needle_color, text_color, \
                font1, font2 \
                    = args
                now = datetime.now(self.timer.timezone)
                today_date = now.strftime("%y%m%d")
                today_time = now.strftime('%H:%M:%S')
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
                ampm_color = lambda time, ampm: clock_frame_color[0] \
                        if time.strftime('%p') == ampm else clock_frame_color[1]
                # dimension ssd1331 96 x 64
                # to see drawer funcs signeture, see. https://pillow.readthedocs.io/en/latest/reference/ImageDraw.html
                # because of luma.core.canvas implementation. (see also)
                origin = (cx, cy)

                # SPEC: e.g., If now AM -> AM frame set active, PM frame inactive
                # PM circle (x - cx)^2 + (y - cy)^2 = R^2
                draw.ellipse(self._circular(R, origin), outline=ampm_color(now, 'PM'))

                # AM circle, This circle must be concentric with PM circle
                draw.ellipse(self._circular(R * R_ratio, origin), outline=ampm_color(now, 'AM'))

                draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill=needle_color)
                draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill=needle_color)
                draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill=sec_needle_color)
                # clock origin
                draw.ellipse(self._circular(2, origin), fill=needle_color, outline=needle_color)

                # literal infos
                # print Most Recent Schedule's name & time
                draw.text((1.8 * (cx + margin), cy - an_lineheight * 4), label_text, fill=text_color, font=font1)
                DISPLAY = 1 # only for readability
                display_name, display_color = name[DISPLAY]['shorten_name'], name[DISPLAY]['color']
                draw.text((1.8 * (cx + margin), cy - an_lineheight * 2.4), display_name, fill=display_color, outline=text_color, font=font1)
                # output most recent schedule's name
                dateform, timeform = time.strftime('%y%m%d'), time.strftime('%H:%M')
                draw.text((1.8 * (cx + margin), cy - an_lineheight), dateform, fill=text_color, font=font1)
                draw.text((1.9 * (cx + margin), cy), timeform, fill=text_color, font=font1)
                draw.text((1.75 * (cx + margin), cy + an_lineheight * 2), temperature, fill=clock_frame_color[1], font=font2)

                # plot schedules on ellipse
                self._plot_schedule(draw, origin, R, sch_plot_R, R_ratio, schs)
                return display_name, dateform, timeform

    def _circular(self, r, origin):
        return (tuple([x - r for x in origin]), tuple([x + r for x in origin]))

    def _plot_schedule(self, draw, origin, R, plot_R, R_ratio, schedules):
        """ plot schedules on ellipse """
        DISPLAY = 1
        for i, s in enumerate(schedules):
            name, time = s
            color = name[DISPLAY]['color']
            r = lambda r, x: r * R_ratio if x else r
            draw.ellipse(self._plot_on_circle(origin, r(R, time.hour < 12), r(plot_R, i!=0), time), fill=color)

    def _plot_on_circle(self, origin, R, plot_R, time):
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
        passed_min = math.radians((h12 * 60 + time.minute) / 2)
        # here, axis origin is left-up, -> Oy - Rcos...
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

# @profile
def main():
    """ for memory_profile """
    try:
        ins = SunlightControl(LEDLightDayTimer(), 30 * 60)

        ins.start()
        ins.join()
    except KeyboardInterrupt:
        ins.kill()
        print('Caught KeyboardInterrupt. schedules were cancelled.')
        exit(0)

if __name__ == '__main__':
    main()
