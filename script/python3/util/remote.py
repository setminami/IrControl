# -*- coding: utf-8 -*-
# this made for python3

from itertools import product
import subprocess as sp

from util import module_logger, is_debug


class Remote(object):
    NOTAVAILABLE = 'NA'

    def __init__(self, infrared_cmd, http_cmd, webhook_path, key):
        self._ircmd, self.http_cmd, self._ifttt_path, self._ifttt_key = \
                                    infrared_cmd, http_cmd, webhook_path, key
        self.logger = module_logger(__name__)

    def setup_ir_keycodes(self, keycodes):
        self.name = keycodes['name']
        Remote.set_keys(keycodes)

    def send_IR_key(self, key, repeat=1):
        cmd = f'{self._ircmd} -#{repeat} SEND_ONCE ledlight {key}'
        # WANTFIX: Why it prints many same lines when logger has been called from sched.run??
        self.logger.info(cmd)
        sp.call(cmd, shell=True)

    def send_HTTP_trigger(self, endpoint, repeat=1):
        """
        IFTTT response
        success: Congratulations! You've fired the {event name} event
        failure: { "errors": [{"message": "You sent an invalid key."}] }
        """
        ifttt_path = lambda key: self._ifttt_path.format(endpoint, key)
        blind_key = ifttt_path('********')
        # WANTFIX: Why it prints many same lines when logger has been called from sched.run??
        self.logger.info(f'run {endpoint} {repeat} for {blind_key}')
        for i in range(repeat):
            res, l = "", 0
            while l < 3 and res != f"Congratulations! You've fired the {endpoint} event":
                self.logger.info(f'try {i}-{l}: {blind_key}')
                # noneed to use pycurl or requests, thread unsafe on macOS 10.14.
                res = sp.check_output(f'{self.http_cmd} {ifttt_path(self._ifttt_key)}', shell=True).decode('utf-8')
                self.logger.info(res)
                l += 1

    @property
    def name(self): return self._name

    @name.setter
    def name(self, val): self._name = val

    @classmethod
    def keys(cls, name, position: tuple):
        """ key must be given by 2x2 list """
        assert len(position) == 2
        row, col  = position
        assert isinstance(row, int) and isinstance(col, int)
        my_remote = cls._keys[name]
        return my_remote[row][col]

    @classmethod
    def set_keys(cls, val):
        """
        _keys must be constructed as 2x2 list.
        see also. KEYCODE  0_0, 0_1, .... in yaml
        """
        keys = []
        check = lambda dict, key, default_val: dict[key] if key in dict.keys() else default_val
        for i in range(val['row_max']):
            keys.append([check(val, f'{x}_{y}', cls.NOTAVAILABLE) \
                    for x, y in list(product([i], list(range(val['col_max']))))])
        if not hasattr(cls, '_keys'):
            cls._keys = {val['name'] : keys}
        else:
            cls._keys[val['name']] = keys

    @classmethod
    def _key_as_point(cls, position: str):
        pos = position.split('_')
        assert len(pos) == 2
        return tuple([int(i) for i in pos])


class RemoteArgs(object):
    """ To avoid that be useless instances Remote
          - remote: ledlight | IFTTT (str)
            command: * (str)
            repeat: (int)
    """
    devicefuncs = {'ledlight': 'send_IR_key', 'IFTTT': 'send_HTTP_trigger'}

    def __str__(self):
        return f'{__class__.__name__}(name: {self.function}, args:{self.args})'

    def __init__(self, item):
        self._funcname = item['remote']
        if self._funcname == 'ledlight':
            x = Remote._key_as_point(item['command'])
            item1 = Remote.keys(self._funcname, x)
        else:
            item1 = item['command']
        self._args = (item1, item['repeat'])
        self.logger = module_logger(__name__)

    @property
    def function(self):
        """ I know connectors between yaml and Remote methods. """
        return self.devicefuncs[self._funcname]

    @property
    def priority(self):
        """ priority of the schedule """
        return 1 if self._funcname == 'IFTTT' else 2

    @property
    def args(self):
        return self._args

    @property
    def json(self):
        """ RemoteArgs json schema """
        return {"funcname": self._funcname, "args": list(self.args)}

    def do(self, instance):
        assert isinstance(instance, Remote)
        # WONTFIX: Why it prints many same lines when logger has been called from sched.run??
        print(f'ran RemoteArgs.do: try to eval Remote.{self.function}{self.args}')
        eval(f'instance.{self.function}{self.args}')
