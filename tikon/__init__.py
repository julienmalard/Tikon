from pkg_resources import resource_filename


__author__ = 'Julien Malard'

with open(resource_filename('tikon', 'versión.txt')) as archivo_versión:
    versión = archivo_versión.read().strip()

__version__ = versión
