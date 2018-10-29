# -*- coding: utf-8 -*-
# this made for python3

from enum import Enum
from . import logger, is_debug, ONEW_DEVICE_PATH
import re


# to control semi-state_fully with IFTTT + tuya Device for Smart plugs
class SmartPlug:
    """ CONTRACT: IFTTT service name must be {plug_name}_{on|off} """

    def __init__(self, name):
        self._name = name
        self._status = self.Status.UNKNOWN
        pass

    @property
    def name(self): return self._name

    @property
    def status(self): return self._status

    @status.setter
    def status(self, state): self._status = state

    class Status(Enum):
        ON, OFF, UNKNOWN = 'on', 'off', 'unknown'


class OneWire(object):
    """
    call data from 1-wire device
    """
    device_path = ONEW_DEVICE_PATH

    def __init__(self, rom_code, prev):
        self._devfile = self.device_path.format(rom_code) \
                            if not is_debug() else self.device_path
        self._prev_temp, self._prev_crc = prev
        self.logger = logger.getChild(__name__)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def device(self):
        assert hasattr(self, '_devfile')
        return self._devfile

    def open(self):
        try:
            self._fd = open(self.device, 'r')
        except FileNotFoundError as e:
            self.logger.critical(f'{self.device} not setuped?')

    def close(self):
        try:
            self._fd.close()
        except:
            self.logger.critical('device file couldn\'t close.')

    def check(self):
        """
        e.g.,
        $ cat /sys/bus/w1/devices/28-XXX/w1_slave
        8a 01 4b 46 7f ff 0c 10 cb : crc=cb YES
        8a 01 4b 46 7f ff 0c 10 cb t=24625

        if caught same crc with prev, donot read temperature data(t=), and return None
        caught different crc, read temperature, and return (t/1000 as float, crc).
        """
        crc = self.crc(self._fd.readline())
        if crc == self._prev_crc:
            return self._prev_temp, crc
        else:
            # update is detected
            return self.dev_depends_f(self._fd.readline()), crc

    def dev_depends_f(self, *args):
        """ Children must impl"""
        assert True, f'Not Impl Concrete function {args}'

    def crc(self, text):
        match = re.match(r".*:\scrc=(..)\sYES", text)
        if match:
            return match.group(1)
        else:
            self.logger.error('1-wire setup not be correctly.')
            exit(1)


