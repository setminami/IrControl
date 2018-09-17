# -*- coding: utf-8 -*-
# this made for python3

from itertools import product
import subprocess as ap

class Remote(object):

    NOTAVAILABLE = 'NA'
    def setup_ir_keycodes(self, keycodes):
        self.name = keycodes['name']
        self.keys = keycodes

    def send_key(self, key, repeat=1):
        sp.call('irsend -#%d SEND_ONCE ledlight %s'%(repeat, key), shell=True)

    def ifttt(self, endpoint, repeat=1):
        print('**** run {} {} ****'.format(endpoint, repeat))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def keys(self, position: tuple):
        """ key must be given by 2x2 list """
        assert(len(position) == 2)
        row, col  = position
        return self._keys[row][col]

    @keys.setter
    def keys(self, val):
        """
        _keys must be constructed as 2x2 list.
        see also. KEYCODE  0_0, 0_1, .... in yaml
        """
        self._keys = []
        check = lambda dict, key, default_val: dict[key] if key in dict.keys() else default_val
        for i in range(val['row_max']):
            self._keys.append([check(val, '{}_{}'.format(x, y), self.NOTAVAILABLE) \
            for x, y in list(product([i], list(range(val['col_max']))))])

class RemoteArgs(object):
    """ To avoid that be useless instances Remote
          - remote: ledlight | IFTTT (str)
            command: * (str)
            repeat: (int)
    """

    def __init__(self, item):
        self._funcname = item['remote']
        self._args = (item['command'], item['repeat'])

    @property
    def name(self):
        """ I know connectors between yaml and Remote methods. """
        if self._funcname == 'ledlight':
            return 'send_key'
        elif self._funcname == 'IFTTT':
            return 'connect_ifttt'

    @property
    def args(self):
        return self._args

    def do(self, instance):
        assert isinstance(instance, Remote)
        eval('instance.{}{}'.format(self.name, self.args))
