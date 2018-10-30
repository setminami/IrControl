#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from luma.emulator.device import emulator
from PIL import Image, ImageDraw
import pygame

pygame.init()
screen = pygame.display.set_mode((1000, 1000))
pygame.display.set_caption('XXX')
TMP_FILE = './tmp.png'

def get_device(actual_args):
    print('dummy implementation')
    # sd1331
    width, height = int(actual_args[-3]), int(actual_args[-1])
    return emulator(width, height, 3, 'RGB', 'none', 6)

class canvas(object):
    """ dummy canvas for 'with' sentense """
    def __init__(self, device: emulator):
        self.device = device

    def __enter__(self):
        self.image = Image.new('RGB', (self.device.width, self.device.height), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        # self.device.show()
        return self

    def __exit__(self, type, value, traceback):
        self.image.save(TMP_FILE)
        img = pygame.image.load(TMP_FILE).convert_alpha()
        screen.blit(img, (0, 0))
        pygame.display.update()
        pass

    def ellipse(self, arg, fill='black', outline='white'):
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
        self.draw.line(arg, fill)
        pass

    def text(self, arg, msg, fill, outline='black', font=None):
        """
        e.g.,
        text((1.8 * (cx + margin), cy - an_lineheight * 4), 'next:', fill="yellow")
        """
        # self.draw.text(arg, msg, fill, outline, font)
        pass
