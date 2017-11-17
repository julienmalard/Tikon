import json
import os.path

from warnings import warn as avisar
from pkg_resources import resource_filename


__author__ = 'Julien Malard'
__email__ = 'julien.malard@mail.mcgill.ca'

with open(resource_filename('tikon', 'versión.txt')) as archivo_versión:
    versión = archivo_versión.read().strip()

__version__ = versión


# Buscar directorios de modelos de cultivos, si necesario
archivo_ctrls = resource_filename('tikon', 'controles.json')
with open(archivo_ctrls, 'r', encoding='utf8') as d:
    dic_ctrls = json.load(d)

dirs_modelos = dic_ctrls['dirs_mods_cult']
dirs_auto = {
    'DSSAT': "C:\\DSSAT46",
}
mods_faltan = []

ctrls_cambiados = False
for mod in dirs_modelos:
    if not os.path.exists(dirs_modelos[mod]):

        if mod in dirs_auto and os.path.exists(dirs_auto[mod]):
            dirs_modelos[mod] = dirs_auto[mod]
            ctrls_cambiados = True

        else:
            mods_faltan.append(mod)

if ctrls_cambiados:
    with open(archivo_ctrls, 'w', encoding='utf8') as d:
        json.dump(dic_ctrls, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo

if len(mods_faltan):
    avisar('Directorios no encontrados para los modelos de cultivo %s. '
           'No se pueden usar estos modelos de cultivos en esta sesión de Tiko\'n.' % ', '.join(mods_faltan)
           )
