# -*- coding: utf-8 -*-
# this made for  python3.5.3

from .remote import RemoteArgs

class Schedule(object):
    def __init__(self, name, display_info, time, operations):
        self._name = name
        self._display = display_info
        self._time = time
        self._operations = operations

    @property
    def name(self):
        return self._name

    @property
    def display_info(self): return self._display

    @property
    def time(self):
        return self._time

    @property
    def operations(self):
        return [RemoteArgs(x) for x in self._operations]
