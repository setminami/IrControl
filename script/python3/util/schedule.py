# -*- coding: utf-8 -*-
# this made for  python3.5.3

from .remote import RemoteArgs


class Schedule(object):
    def __init__(self, name, display_info, time, operations):
        self._name = name
        self._display = display_info
        self._time = time
        self._operations = operations
        self._msg = 'no Fire'

    @property
    def name(self):
        return self._name

    @property
    def msg(self):
        return self._msg

    @msg.setter
    def msg(self, msg):
        self._msg = msg

    @property
    def display_info(self): return self._display

    @property
    def time(self):
        return self._time

    @property
    def operations(self):
        return [RemoteArgs(x) for x in self._operations]

    @property
    def json(self):
        """ schedule json schema"""
        return {"name": self.name,
                "time": self.time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                "message": self.msg,
                "operations": [x.json for x in self.operations]}