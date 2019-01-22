from pkg_resources import resource_filename


with open(resource_filename('tikon', 'versión.txt')) as archivo_versión:
    __versión__ = archivo_versión.read().strip()
