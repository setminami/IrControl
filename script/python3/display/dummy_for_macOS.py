#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from luma.emulator.device import emulator
from PIL import Image, ImageDraw
import pygame

def get_device(actual_args):
    print('dummy implementation')
    # sd1331
    width, height = int(actual_args[-3]), int(actual_args[-1])
    return emulator(width, height, 3, 'RGB', 'none', 6)

class canvas(object):
    """ dummy canvas for 'with' sentense """
    def __init__(self, device):
        self.device = device
        self.image = Image.new('RGB', (96, 64), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def __enter__(self):
        self.device.show()
        return self

    def __exit__(self, type, value, traceback):
        self.device.cleanup()
        pass

    def ellipse(self, arg, fill='white', outline='white'):
        """
        e.g.,
        ellipse((left + margin, margin, right - margin, min(device.height, 64) - margin), outline="yellow")
        """
        self.draw.ellipse(arg, fill=fill, outline=outline)
        pass

    def line(self, arg, fill):
        """
        e.g.,
        line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
        """
        pass

    def text(self, arg, msg, fill, outline='', font=None):
        """
        e.g.,
        text((1.8 * (cx + margin), cy - an_lineheight * 4), 'next:', fill="yellow")
        """
        pass
