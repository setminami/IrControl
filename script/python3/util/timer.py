# -*- coding: utf-8 -*-
# this made for python3

from threading import Thread
from datetime import datetime
import sys, logging, pytz

from sched import scheduler
import time
# sched is not support datetime but time
# TypeError: unsupported operand type(s) for +: 'datetime.datetime'

from util.weather_info import WeatherInfo
from util.remote import Remote
from . import module_logger

class LEDLightDayTimer(object):
    """ a simple day timer """

    def __init__(self):
        self._sched = scheduler(time.time, time.sleep)
        self.logger = module_logger(__name__)

    def is_usedup(self):
        return self._sched.empty()

    @property
    def timezone(self):
        assert hasattr(self, '_TZ')
        return self._TZ

    @timezone.setter
    def timezone(self, val):
        assert val in pytz.all_timezones, "Timezone not valid."
        self._TZ = pytz.timezone(val)

    @property
    def weather(self):
        return self._weather
    @weather.setter
    def weather(self, val:WeatherInfo):
        self._weather = val
        self.schedules = self._weather.timeshift_today

    @property
    def schedules(self):
        assert hasattr(self, '_schedules')
        return self._schedules

    @schedules.setter
    def schedules(self, schedules: list):
        self._schedules = schedules

    @property
    def remote(self):
        assert hasattr(self, '_remote')
        return self._remote

    @remote.setter
    def remote(self, remote: Remote):
        self._remote = remote

    def do_schedule(self):
        """ reset event queue and run """
        if not self._sched.empty():
            [self._sched.cancel(ev) for ev in self._sched.queue]
        now = datetime.now(self.timezone)
        for val in self.schedules.values():
            if val.time >= now:
                msg = 'will fire'
                self._sched.enterabs(time.mktime(val.time.timetuple()), 2,
                                    self._do, argument=(val.operations, self.remote))
            else:
                msg = 'not scheduled time had passed'
            self.logger.info('{} {} @ {}: '.format(val.name, msg,
                                                val.time.strftime('%Y-%m-%d %H:%M:%S%z')))
            if msg == 'will fire':
                # expand __str__
                [self.logger.info('- %s'%o) for o in val.operations]
        self._sched.run()

    def _do(self, ops, ins):
        [op.do(ins) for op in ops]
