import os.path
import json


from pkg_resources import resource_filename

# Este documento contiene información general para el programa Tikon

# El directorio de pase del programa Tikon. Utilizado como referencia para encontrar y escribir documentos.
directorio_base = os.path.dirname(__file__)

# El directorio donde está ubicado cada modelo de cultivo
archivo_ctrls = resource_filename('tikon', 'dirs_mod_cult.json')
with open(archivo_ctrls, 'r', encoding='utf8') as d:
    dirs_modelos = json.load(d)


def espec_dir_modelo_cult(modelo, directorio):

    if modelo not in dirs_modelos.keys():
        raise ValueError('Modelo "{}" no reconocido.'.format(modelo))

    if os.path.exists(dir):
        dirs_modelos[modelo] = directorio

        with open(archivo_ctrls, 'w', encoding='utf8') as d:
            json.dump(dirs_modelos, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo
    else:
        raise ValueError('El directorio especificado ("{}") no existe.'.format(directorio))
