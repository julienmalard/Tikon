import json
import os

from tikon.utils import guardar_json

arch_config = os.path.join(os.path.split(__file__)[0], 'config.json')
try:
    with open(arch_config, 'r', encoding='utf8') as a:
        _conf = json.load(a)
except (FileNotFoundError, json.JSONDecodeError, PermissionError):
    _conf = {}


def poner_config(var, val):
    _conf[var] = val
    guardar_json(_conf, arch_config)


def obt_config(var):
    try:
        return _conf[var]
    except KeyError:
        return
