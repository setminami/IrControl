# -*- coding: utf-8 -*-
# this made for python3

from os import environ

def expand_env(params, verbose=False):
    """ dotenv like function, but not dotenv """
    for key, val in params.items():
        _print('try %s, %s'%(key, val), verbose)
        if isinstance(val, dict):
            _print('ORDEREDDICT', verbose)
            params[key] = expand_env(val, verbose)
        elif isinstance(val, list):
            _print('LIST', verbose)
            params[key] = [expand_env(x, verbose) for x in val]
        elif isinstance(val, str) and (val.startswith('${') \
                and val.endswith('}')):
            _print('LEAF', verbose)
            env_key = val[2:-1]
            if env_key in list(environ.keys()):
                params[key] = environ[env_key]
                _print('Overwrite env value {} = {}'.format(val, params[key]), verbose)
            else:
                _print('## {} not exported for {}. Please check your yaml file and env. ##'.format(env_key, key), verbose)
                _print('Env {} vs keys = {}'.format(env_key, list(environ.keys())), verbose)
                exit(1)
        else:
            _print('?? %s TYPE is %s'%(val, type(val)), verbose)
    return params

def _print(msg, v=False):
    if v: print(msg)
