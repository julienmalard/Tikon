import json
import os.path

from warnings import warn as avisar
from pkg_resources import resource_filename


__author__ = 'Julien Malard'

with open(resource_filename('tikon', 'versión.txt')) as archivo_versión:
    versión = archivo_versión.read().strip()

__version__ = versión


# Buscar directorios de modelos de cultivos, si necesario
archivo_ctrls = resource_filename('tikon', 'dirs_mod_cult.json')
with open(archivo_ctrls, 'r', encoding='utf8') as d:
    dirs_modelos = json.load(d)

if not os.path.exists(dirs_modelos['DSSAT']):
    dir_auto = "C:\\DSSAT46"
    if os.path.exists(dir_auto):
        dirs_modelos['DSSAT'] = dir_auto
    else:
        avisar('Directorio DSSAT no encontrado. No se pueden usar modelos de DSSAT en esta sessión de Tiko\'n.')

    with open(archivo_ctrls, 'w', encoding='utf8') as d:
        json.dump(dirs_modelos, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo
