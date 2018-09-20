# -*- coding: utf-8 -*-
# this made for python3
# how to install -> https://www.bluetin.io/displays/oled-display-raspberry-pi-ssd1331/
import os
if os.uname().sysname == 'Darwin':
    print('## the ENV Cannot use luma library ##')
    from .dummy_opts import get_device
else:
    from luma.core.render import canvas
    from .demo_opts import get_device
