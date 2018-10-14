# -*- coding: utf-8 -*-
# this made for python3

import pytz, time
from datetime import datetime

from json import dumps
from sched import scheduler
from multiprocessing import Process
# sched is not support datetime but time
# TypeError: unsupported operand type(s) for +: 'datetime.datetime'

from util.weather_info import WeatherInfo
from util.remote import Remote
from . import module_logger
from util.env import schedule_output_path

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
        self._schedules = self._weather.timeshift_today

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
        FIRE, DISSMISS = 'will fire', 'not scheduled, time had passed'
        if not self._sched.empty():
            [self._sched.cancel(ev) for ev in self._sched.queue]
            if hasattr(self, '_p'):
                self.logger.info(f"try to join() Process. {self._p}")
                self._p.join(0.5)
                if not self._p.is_alive():
                    self.logger.info("joined Process.")
                else:
                    self.logger.info("is alive yet.")
                self._p.terminate()

        now = datetime.now(self.timezone)
        for val in self._schedules.values():
            if val.time >= now:
                msg = FIRE
                self._sched.enterabs(time.mktime(val.time.timetuple()), 2,
                                     self._do, argument=(val.name, val.display_info, val.operations, self.remote))
            else:
                msg = DISSMISS

            val.msg = msg
            t = val.time.strftime('%Y-%m-%d %H:%M:%S%z')
            self.logger.info(f'{val.name} {msg} @ {t}: ')
            if msg == FIRE:
                # expand __str__
                [self.logger.info(f'- {o}') for o in val.operations]
        self.output_schedule(schedule_output_path(now.strftime('%y%m%dT%H%M%S_%f') + '.sch'),
                             [v.json for v in self._schedules.values()])

        if not self._sched.empty():
            # just wait in another process, until all schedules were usedup.
            self._p = Process(name='schedulings', target=self._sched.run, args=())
            self._p.daemon = True
            self._p.start()
            self.logger.info(f'Process @{self._p} {self._p.pid} has (re)started.')
        return self._sched.queue

    def output_schedule(self, path, obj):
        with open(path, 'w') as f:
            f.write(dumps(obj))

    def _do(self, name, display_info, ops, ins):
        # name and display_info are only Event id, not effective here
        self.logger.debug(f'&&&&&&&&&&&&& len(ops) = {len(ops)} &&&&&&&&&&&&&&&')
        for op in ops:
            op.do(ins)
        del self._schedules[name]
