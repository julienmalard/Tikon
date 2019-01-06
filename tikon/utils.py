import json
import os
import shutil
import tempfile

from chardet import UniversalDetector

_dir_config = os.path.join(os.path.split(__file__)[0], 'config.json')
try:
    with open(_dir_config, 'r', encoding='utf8') as d:
        _config = json.load(d)
except (FileNotFoundError, json.JSONDecodeError, PermissionError):
    _config = {}


def guardar_conf(conf, val):
    _config[conf] = val
    guardar_archivo(json.dumps(_config, ensure_ascii=False, sort_keys=True, indent=2), _dir_config)


def obtener_conf(conf):
    try:
        return _config[conf]
    except KeyError:
        return


def guardar_archivo(texto, archivo):
    with tempfile.NamedTemporaryFile('w', encoding='UTF-8', delete=False) as arch_temp:
        arch_temp.write(texto)

        dir_ = os.path.split(archivo)[0]
        if dir_ and not os.path.isdir(dir_):  # pragma: sin cobertura
            os.makedirs(os.path.split(archivo)[0])

    if os.path.splitdrive(arch_temp.name)[0] == os.path.splitdrive(archivo)[0]:
        os.replace(arch_temp.name, archivo)
    else:
        shutil.move(arch_temp.name, archivo)


def detectar_codif(archivo, máx_líneas=None, cortar=None):
    """
    Detecta la codificación de un fuente. (Necesario porque todavía existen programas dinosaurios que no entienden
    los milagros de unicódigo.)

    Parameters
    ----------
    archivo : str
        La dirección del fuente.
    máx_líneas : int
        El número máximo de líneas para pasar al detector. Por ejemplo, si únicamente la primera línea de tu documento
        tiene palabras (por ejemplo, un fuente .csv), no hay razón de seguir analizando las otras líneas.
    cortar : str
        Hasta dónde hay que leer cada línea. Es útil si tienes un csv donde únicamente la primera columna
        contiene texto.

    Returns
    -------
    str
        La codificación más probable.

    """

    detector = UniversalDetector()
    with open(archivo, 'rb') as d:
        for í, línea in enumerate(d.readlines()):

            if cortar is None or cortar.encode() not in línea:
                detector.feed(línea)  # Pasar la próxima línea al detector
            else:
                detector.feed(línea.split(cortar.encode())[0])

            # Parar si alcanzamos el máximo de líneas
            if máx_líneas is not None and í >= (máx_líneas - 1):
                break

            if detector.done:
                break  # Para si el detector ya está seguro

    detector.close()  # Cerrar el detector

    return detector.result['encoding']  # Devolver el resultado
