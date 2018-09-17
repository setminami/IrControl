# -*- coding: utf-8 -*-
# this made for  python3.5.3

from .remote import RemoteArgs

class Schedule(object):
    def __init__(self, name, time, operations):
        self._name = name
        self._time = time
        self._operations = operations

    @property
    def name(self):
        return self._name

    @property
    def time(self):
        return self._time

    @property
    def operations(self):
        print(self._operations)
        return [RemoteArgs(x) for x in self._operations]
