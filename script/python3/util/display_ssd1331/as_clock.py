# -*- coding: utf-8 -*-
# this made for python3
# based on https://github.com/rm-hull/luma.examples/blob/master/examples/clock.py

import math, time, datetime
from multiprocessing import Process, Event

from .. import schedule
import os
if os.uname().sysname == 'Darwin':
    print('## the ENV Cannot use luma library ##')
    from .dummy_opts import get_device
else:
    from luma.core.render import canvas
    from .demo_opts import get_device

class Screen(object):
    def __init__(self, schedules):
        self._device = get_device(['-d', 'ssd1331', '-i', 'spi', '--width', '96', '--height', '64'])
        self._schedules = schedules
        self.stop_event = Event()
        self._thread = Process(target=self.run, args=())

    @property
    def device(self):
        assert hasattr(self, '_device')
        return self._device

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

    def posn(angle, arm_length):
        dx = int(math.cos(math.radians(angle)) * arm_length)
        dy = int(math.sin(math.radians(angle)) * arm_length)
        return (dx, dy)


    def run(self):
        today_last_time = "Unknown"
        device = self.device
        an_lineheight = 8

        while not self.stop_event.is_set():
            now = datetime.datetime.now()
            today_time = now.strftime("%H:%M:%S")
            if today_time != today_last_time:
                today_last_time = today_time
                with canvas(device) as draw:
                    now = datetime.datetime.now()
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
    ins = Screen(None)
    ins.start()
    ins.join()
