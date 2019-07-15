import os

import bibtexparser
from pkg_resources import resource_filename

ARCH_REF = 'ref.txt'


def obt_datos(nombre):
    return resource_filename(__name__, nombre)


def obt_ref(nombre):
    dir_ = obt_datos(nombre)
    if os.path.isfile(dir_):
        dir_ = os.path.split(dir_)[0]
    arch = os.path.join(dir_, ARCH_REF)

    with open(arch, encoding='utf8') as bibtex_file:
        return bibtexparser.load(bibtex_file)
