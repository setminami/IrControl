#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from luma.emulator.device import capture #, pygame
from . import IMG_OUTPUT


def get_device(actual_args):
    print('dummy implementation')
    # sd1331
    width, height = int(actual_args[-3]), int(actual_args[-1])
    # see also
    # https://github.com/rm-hull/luma.emulator/blob/master/luma/emulator/device.py
    # At this commit, latest pygame 1.9.4 + mojave 14.1 have some trouble that causes system crash.
    # https://github.com/pygame/pygame/issues/555
    return capture(width, height, 3, 'RGB', 'none', 6, file_template=IMG_OUTPUT)