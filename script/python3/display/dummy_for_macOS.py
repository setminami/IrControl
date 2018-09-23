#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def get_device(actual_args=None):
    print('dummy implementation')
    # sd1331
    return device(96, 64)

class device(object):
    def __init__(self, h, w):
        self.height = h
        self.width = w
        pass

class canvas(object):
    """ dummy canvas for 'with' sentense """
    def __init__(self, device):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def ellipse(self, arg, fill='', outline=''):
        """
        e.g.,
        ellipse((left + margin, margin, right - margin, min(device.height, 64) - margin), outline="yellow")
        """
        pass

    def line(self, arg, fill):
        """
        e.g.,
        line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
        """
        pass

    def text(self, arg, msg, fill):
        """
        e.g.,
        text((1.8 * (cx + margin), cy - an_lineheight * 4), 'next:', fill="yellow")
        """
        pass
