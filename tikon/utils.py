import json
import os
import shutil
import tempfile

_dir_config = os.path.join(os.path.split(__file__)[0], 'config.json')
try:
    with open(_dir_config, 'r', encoding='utf8') as d:
        _config = json.load(d)
except (FileNotFoundError, json.JSONDecodeError, PermissionError):
    _config = {}


def guardar_conf(conf, val):
    _config[conf] = val
    guardar_archivo(json.dumps(_config, ensure_ascii=False, sort_keys=True, indent=2), _dir_config)


def obtener_conf(conf):
    try:
        return _config[conf]
    except KeyError:
        return


def guardar_archivo(texto, archivo):
    with tempfile.NamedTemporaryFile('w', encoding='UTF-8', delete=False) as arch_temp:
        arch_temp.write(texto)

        dir_ = os.path.split(archivo)[0]
        if dir_ and not os.path.isdir(dir_):  # pragma: sin cobertura
            os.makedirs(os.path.split(archivo)[0])

    if os.path.splitdrive(arch_temp.name)[0] == os.path.splitdrive(archivo)[0]:
        os.replace(arch_temp.name, archivo)
    else:
        shutil.move(arch_temp.name, archivo)
