# -*- coding: utf-8 -*-
# this made for python3

from enum import Enum
import re

from .device import OneWire


class ThermoInfo(OneWire):
    """
    call data from 1-wire Thermo Meter
    """

    def dev_depends_f(self, text):
        match = re.match(r".*t=(\d+)", text)
        if match:
            return float(match.group(1)) / 1000  # spec of 1-wire DS18B20
        else:
            self.logger.error('1-wire device not setuped.')
            exit(1)


class TempState(Enum):
    safe = 'safe'
    too_hot = 'too_hot'
    too_cold = 'too_cold'

    def match(self, val: str) -> bool:
        value = TempState(val)
        assert isinstance(value, TempState)
        return self == value
