# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import sys, logging

from util import is_debug as macOS
from luma.core.render import canvas
from . import IMG_OUTPUT

if macOS():
    from luma.emulator.device import capture  # , pygame
else:
    from luma.core import cmdline, error

# logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)-15s - %(message)s'
)

# ignore PIL debug messages
logging.getLogger('PIL').setLevel(logging.ERROR)


def display_settings(args):
    """
    Display a short summary of the settings.
    :rtype: str
    """
    iface = ''
    display_types = cmdline.get_display_types()
    if args.display not in display_types['emulator']:
        iface = f'Interface: {args.interface}\n'

    lib_name = cmdline.get_library_for_display_type(args.display)
    if lib_name is not None:
        lib_version = cmdline.get_library_version(lib_name)
    else:
        lib_name = lib_version = 'unknown'

    import luma.core
    version = f'luma.{lib_name} {lib_version} (luma.core {luma.core.__version__})'

    return f"Version: {version}\nDisplay: {args.display}\n{iface}Dimensions: \
                        {args.width} x {args.height}\n{'-' * 60}"


def get_device(actual_args=None):
    """
    Create device from command-line arguments and return it.
    """
    if not macOS():
        if actual_args is None:
            actual_args = sys.argv[1:]
        parser = cmdline.create_parser(description='SunlightControl luma display arguments')
        args = parser.parse_args(actual_args)

        if args.config:
            # load config from file
            config = cmdline.load_config(args.config)
            args = parser.parse_args(config + actual_args)

        print(display_settings(args))

        # create device
        try:
            device = cmdline.create_device(args)
        except error.Error as e:
            parser.error(e)

        return device
    else:
        print('dummy implementation')
        # sd1331
        width, height = int(actual_args[-3]), int(actual_args[-1])
        # see also
        # https://github.com/rm-hull/luma.emulator/blob/master/luma/emulator/device.py
        # At this commit, latest pygame 1.9.4 + mojave 14.1 have some trouble that causes system crash.
        # https://github.com/pygame/pygame/issues/555
        return capture(width, height, 3, 'RGB', 'none', 6, file_template=IMG_OUTPUT)


class CustomCanvas(canvas):
    """
    The class is located as IF organizer
    """
    def __init__(self, device, background=None, dither=False):
        super().__init__(device, background, dither)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not macOS():  # TODO: When pygame fixed mojave trouble, remove the debug switch.
            self.image.save(IMG_OUTPUT)
        return super().__exit__(exc_type, exc_val, exc_tb)
