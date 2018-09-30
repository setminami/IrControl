# -*- coding: utf-8 -*-
# this made for python3

from . import module_logger, is_debug
import re

class ThermoInfo(object):
    """
    call data from 1-wire thermometer
    """
    device_path = '/sys/bus/w1/devices/{}/w1_slave'

    def __init__(self, rom_code, crc):
        self._devfile = self.device_path.format(rom_code)
        self._crc = crc
        self.logger = module_logger(__class__.__name__)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def device(self):
        assert hasattr(self, '_devfile')
        return self._devfile

    @property
    def temperature(self):
        assert hasattr(self, '_temp')
        return self._temp

    def open(self):
        try:
            self._fd = open(self.device, 'r')
        except FileNotFoundError as e:
            self.logger.critical('{} not setuped?'.format(self.device))

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
        if crc == self._crc:
            return None
        else:
            # update is detected
            self._temp = self.temp(self._fd.readline())
            return self.temperature, crc
        pass

    def crc(self, text):
        match = re.match(r".*:\scrc=(..)\sYES", text)
        if match:
            return match.group(1)
        else:
            self.logger.error('1-wire setup not be correctly.')
            exit(1)

    def temp(self, text):
        match = re.match(r".*t=(\d+)", text)
        if match:
            return float(match.group(1)) / 1000 # spec of 1-wire DS18B20
        else:
            self.logger.error('1-wire setup not be correctly.')
            exit(1)
