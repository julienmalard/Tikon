import numpy as np

from pkg_resources import resource_filename

with open(resource_filename('tikon', 'versión.txt')) as archivo_versión:
    __versión__ = __version__ = archivo_versión.read().strip()

__autor__ = 'Julien Malard-Adam'
__correo__ = 'julien.malard@mail.mcgill.ca'
