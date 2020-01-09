import json
import os
import shutil
import tempfile

import numpy as np
from chardet import UniversalDetector


def guardar_archivo(texto, archivo):
    with tempfile.NamedTemporaryFile('w', encoding='UTF-8', delete=False) as arch_temp:
        arch_temp.write(texto)

    asegurar_dir_existe(archivo)
    if os.path.splitdrive(arch_temp.name)[0] == os.path.splitdrive(archivo)[0]:
        os.replace(arch_temp.name, archivo)
    else:
        shutil.move(arch_temp.name, archivo)


def guardar_json(dic, archivo):
    """
    Guarda un diccionario json en un archivo.

    Parameters
    ----------
    dic: dict
        El diccionario para guardar.
    archivo: str
        El archivo.

    """

    txt = json.dumps(jsonificar(dic), ensure_ascii=False, sort_keys=True, indent=2, default=str)
    guardar_archivo(txt, archivo)


def asegurar_dir_existe(archivo):
    dir_ = os.path.split(archivo)[0]
    if dir_ and not os.path.isdir(dir_):  # pragma: sin cobertura
        os.makedirs(os.path.split(archivo)[0])


def asegurar_ext(archivo, ext):
    if ext[0] != '.':
        ext = f'.{ext}'
    ext_ant = os.path.splitext(archivo)[1]
    if ext_ant != ext:
        archivo = archivo + ext
    return archivo


def leer_json(archivo, numpy=True):
    with open(archivo, 'r', encoding='utf8') as d:
        dic = json.load(d)
    if numpy:
        dic = numpyficar(dic)
    return dic


def jsonificar(dic):
    nuevo = {}
    for ll, v in dic.items():
        if isinstance(v, dict):
            nuevo[ll] = jsonificar(v)
        elif isinstance(v, np.ndarray):
            nuevo[ll] = v.tolist()
        else:
            nuevo[ll] = v

    return nuevo


def numpyficar(dic):
    nuevo = {}
    for ll, v in dic.items():
        if isinstance(v, dict):
            nuevo[ll] = numpyficar(v)
        elif isinstance(v, list):
            nuevo[ll] = np.array(v)
        else:
            nuevo[ll] = v
    return nuevo


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


def proc_líms(líms):
    inf = np.inf

    if líms is None:
        return -inf, inf
    return -inf if líms[0] is None else líms[0], inf if líms[1] is None else líms[1]


EJE_PARÁMS = 'paráms'
EJE_ESTOC = 'estoc'
EJE_TIEMPO = 'tiempo'
EJE_PARC = 'parcela'
EJE_DEST = 'dest'
EJE_COORD = 'coord'
