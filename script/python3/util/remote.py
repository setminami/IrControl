# -*- coding: utf-8 -*-
# this made for python3

from itertools import product
import subprocess as sp
import requests, http.client

from . import logger, is_debug
from .device import SmartPlug


# donot output barer IFTTT Key
http.client.HTTPConnection.debuglevel = 0
http.client.HTTPSConnection.debuglevel = 0


class Remote(object):
    NOTAVAILABLE = 'NA'

    def __init__(self, infrared_cmd, webhook_path, key):
        self._ircmd, self._ifttt_path, self._ifttt_key = infrared_cmd, webhook_path, key
        self.logger = logger.getChild(__name__)

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
        def ifttt_path(key): return self._ifttt_path.format(endpoint, key)
        blind_key = ifttt_path('********')
        # WONTFIX: Why it prints many same lines when logger has been called from sched.run??
        self.logger.info(f'run {endpoint} {repeat} for {blind_key}')
        assert hasattr(self, '_smart_plugs')
        if self.get_smart_plug_state(endpoint).value != endpoint.split('_')[1]:
            response = None
            for i in range(repeat):
                try_time = 0
                while try_time < 3:
                    self.logger.info(f'try {i}-{try_time}: {blind_key}')
                    response = requests.get(ifttt_path(self._ifttt_key))
                    self.logger.info(response)
                    if response.status_code == 200:
                        self.set_smart_plug_state(endpoint)
                        break
                    try_time += 1
                if response.status_code == 200:
                    # ignore left trial
                    break

    @property
    def name(self): return self._name

    @name.setter
    def name(self, val): self._name = val

    @property
    def smart_plugs(self):
        assert hasattr(self, '_smart_plugs')
        assert isinstance(self._smart_plugs, dict)
        return self._smart_plugs
    @smart_plugs.setter
    def smart_plugs(self, vals: list):
        self._smart_plugs = {v.name: v for v in vals}

    def get_smart_plug_state(self, service_name: str):
        plug_name, _ = service_name.split('_')
        try:
            return self.smart_plugs[plug_name].status
        except KeyError:
            self.logger.error(f'The plug name not Found!: {plug_name} in {service_name}')

    def set_smart_plug_state(self, service_name: str):
        plug_name, status = service_name.split('_')
        assert isinstance(status, str)
        self.smart_plugs[plug_name].status = SmartPlug.Status(status)

    @classmethod
    def keys(cls, name, position: tuple):
        """ key must be given by 2x2 list """
        assert len(position) == 2
        row, col = position
        assert isinstance(row, int) and isinstance(col, int)
        my_remote = cls._keys[name]
        return my_remote[row][col]

    @classmethod
    def set_keys(cls, val):
        """
        _keys must be constructed as 2x2 list.
        see also. KEY_CODE  0_0, 0_1, .... in yaml
        """
        keys = []
        check = lambda dict, key, default_val: dict[key] if key in dict.keys() else default_val
        for i in range(val['row_max']):
            keys.append([check(val, f'{x}_{y}', cls.NOTAVAILABLE) \
                    for x, y in list(product([i], list(range(val['col_max']))))])
        if not hasattr(cls, '_keys'):
            cls._keys = {val['name']: keys}
        else:
            cls._keys[val['name']] = keys

    @classmethod
    def _key_as_point(cls, position: str):
        pos = position.split('_')
        assert len(pos) == 2
        return tuple([int(i) for i in pos])


class RemoteArgs(object):
    """
    Like as The device command's preprocessor
    To avoid that be useless instances Remote
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
        self.logger = logger.getChild(__name__)

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
