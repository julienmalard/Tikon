import os

from pkg_resources import resource_filename
from tikon.utils import leer_json
from datetime import datetime
ARCH_REF = 'ref.json'


def obt_calib(nombre):
    return resource_filename(__name__, nombre)


def guardar_calib(nombre, autor, correo=None):
    ahora = datetime.now()

    raise NotImplementedError


def obt_ref(nombre):
    dir_ = obt_calib(nombre)
    if os.path.isfile(dir_):
        dir_ = os.path.split(dir_)[0]
    arch = os.path.join(dir_, ARCH_REF)

    return leer_json(arch, numpy=False)
