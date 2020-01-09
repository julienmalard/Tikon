import os
from datetime import datetime

from pkg_resources import resource_filename
from tikon.utils import leer_json, guardar_json

ARCH_INFO = 'info.json'


def obt_calib(nombre):
    return resource_filename(__name__, nombre)


def guardar_calib(objs, nombre, autor, correo=None):
    ahora = datetime.now()

    info = {
        'fecha': ahora.strftime('%Y-%m-%d %H:%M:%S'),
        'autor': autor,
        'correo': correo
    }

    dir_ = obt_calib(nombre)
    for obj in objs:
        obj.guardar_calibs(dir_)

    guardar_json(info, os.path.join(dir_, ARCH_INFO))


def obt_ref(nombre):
    dir_ = obt_calib(nombre)
    if os.path.isfile(dir_):
        dir_ = os.path.split(dir_)[0]
    arch = os.path.join(dir_, ARCH_INFO)

    return leer_json(arch, numpy=False)
