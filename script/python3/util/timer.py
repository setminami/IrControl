# -*- coding: utf-8 -*-
# this made for python3

from datetime import datetime
import sys, logging, pytz

from sched import scheduler
from multiprocessing import Pool, Process
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
    def schedules(self, schedules):
        self._schedules = schedules

    @property
    def remote(self):
        assert hasattr(self, '_remote')
        return self._remote
    @remote.setter
    def remote(self, remote: Remote):
        self._remote = remote

    def do_schedule(self):
        """
        reset event queue and reschedule and run them
        """
        if not self._sched.empty():
            [self._sched.cancel(ev) for ev in self._sched.queue]
            if hasattr(self, '_p'): self._p.join(0.5)

        now = datetime.now(self.timezone)
        for val in self.schedules.values():
            if val.time >= now:
                msg = 'will fire'
                self._sched.enterabs(time.mktime(val.time.timetuple()), 2,
                                    self._do, argument=(val.name, val.display_info, val.operations, self.remote))
            else:
                msg = 'not scheduled, time had passed'
            self.logger.info('{} {} @ {}: '.format(val.name, msg,
                                                val.time.strftime('%Y-%m-%d %H:%M:%S%z')))
            if msg == 'will fire':
                # expand __str__
                [self.logger.info('- %s'%o) for o in val.operations]
        if not self._sched.empty():
            self._p = Process(name='schedulings', target=self._sched.run, args=()) # just wait in another process, until all schedules were usedup.
            self._p.daemon = True
            self._p.start()
        return self._sched.queue

    def _do(self, name, display_info, ops, ins):
        # name is only Event id, not effective here
        [op.do(ins) for op in ops]
        del self.schedules[name]
