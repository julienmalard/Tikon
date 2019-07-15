import os
import shutil

import bibtexparser
from pkg_resources import resource_filename
from tikon.utils import guardar_json

_ARCH_REF = 'ref.txt'
_EXT_INFO = '.info.json'


def obt_datos(nombre):
    return resource_filename(__name__, nombre)


def obt_ref(nombre):
    dir_ = obt_datos(nombre)
    if os.path.isfile(dir_):
        dir_ = os.path.split(dir_)[0]
    arch = os.path.join(dir_, _ARCH_REF)

    with open(arch, 'r', encoding='utf8') as arch_bibtex:
        return bibtexparser.load(arch_bibtex)


def guardar_datos(datos, nombre, módulo, variable, unidades, ref=None):
    nombre_datos = os.path.split(datos)[1]
    dir_ = obt_datos(nombre)

    if not os.path.isdir(dir_):
        os.makedirs(dir_)
    shutil.copy(src=datos, dst=os.path.join(dir_, nombre_datos))

    info = {
        "módulo": módulo,
        "variable": variable,
        "unidades": unidades
    }
    guardar_json(info, os.path.join(dir_, os.path.splitext(nombre_datos)[0] + _EXT_INFO))

    if ref:
        with open(os.path.join(dir_, _ARCH_REF), 'w', encoding='utf8') as arch_bibtex:
            return bibtexparser.load(arch_bibtex)
