# -*- coding: utf-8 -*-
# this made for python3

from itertools import product
import subprocess as sp

class Remote(object):
    NOTAVAILABLE = 'NA'

    def __init__(self, infrared_cmd, webhook_path, key):
        self._ircmd, self._ifttt_path, self._ifttt_key = infrared_cmd, webhook_path, key

    def setup_ir_keycodes(self, keycodes):
        self.name = keycodes['name']
        self.keys = keycodes

    def send_IR_key(self, key, repeat=1):
        sp.call('%s -#%d SEND_ONCE ledlight %s'%(self._ircmd, repeat, key), shell=True)

    def send_HTTP_trigger(self, endpoint, repeat=1):
        ifttt_path = self._ifttt_path.format(endpoint, self._ifttt_key)
        print('**** run {} {} for {} ****'.format(endpoint, repeat, ifttt_path))
        for i in range(repeat):
            cmd = 'curl %s'%ifttt_path
            print('try %d: %s'%(i, cmd))
            # noneed to use pycurl
            sp.call(cmd, shell=True)

    @property
    def name(self): return self._name

    @name.setter
    def name(self, val): self._name = val

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
        return {'ledlight': 'send_IR_key',
                'IFTTT': 'send_HTTP_trigger'}[self._funcname]

    @property
    def args(self):
        return self._args

    def do(self, instance):
        assert isinstance(instance, Remote)

        print('RemoteArgs.do ran : try to eval Remote.{}{}'.format(self.name, self.args))
        eval('instance.{}{}'.format(self.name, self.args))
