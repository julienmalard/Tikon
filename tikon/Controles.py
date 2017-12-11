import os.path
import json
import pathvalidate
from warnings import warn as avisar

from pkg_resources import resource_filename

usar_pymc3 = False

# Este documento contiene información general para el programa Tiko'n

# El directorio de pase del programa Tikon. Utilizado como referencia para encontrar y escribir documentos.
directorio_base = os.path.dirname(__file__)

# El directorio para proyectos
dir_proyectos = os.path.join(directorio_base, 'Proyectos')

# El directorio donde está ubicado cada modelo de cultivo
archivo_ctrls = resource_filename('tikon', 'controles.json')
with open(archivo_ctrls, 'r', encoding='utf8') as doc:
    dic_ctrls = json.load(doc)

dirs_modelos = dic_ctrls['dirs_mods_cult']


def espec_dir_modelo_cult(modelo, directorio):

    if modelo not in dirs_modelos.keys():
        raise ValueError('Modelo "{}" no reconocido.'.format(modelo))

    if os.path.exists(directorio):
        dirs_modelos[modelo] = directorio

        with open(archivo_ctrls, 'w', encoding='utf8') as d:
            json.dump(dic_ctrls, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo
    else:
        raise ValueError('El directorio especificado ("{}") no existe.'.format(directorio))


def valid_archivo(archivo):

    direc, nombre = os.path.split(archivo)
    disco, direc = os.path.splitdrive(direc)

    direc = pathvalidate.sanitize_file_path(direc, replacement_text='_')
    nombre = pathvalidate.sanitize_filename(nombre, replacement_text='_')

    if len(direc) >= 260:
        raise ValueError('El archivo siguiente queda demasiado largo...\n\t{}'.format(archivo))

    if len(direc) + len(nombre) > 260:
        avisar('Cortamos el nombre "{}" por ser demasiado largo'.format(nombre))
        nombre = nombre[:len(direc) - 260]

    return os.path.join(disco, direc, nombre)
