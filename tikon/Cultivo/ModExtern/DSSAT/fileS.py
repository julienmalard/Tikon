import re

import numpy as np
import pkg_resources

from tikon.Matemáticas import Ecuaciones as Ec

# Un diccionario para convertir códigos de variables DSSAT a nombres de variables de Tiko'n
DSSAT_a_Tikon = dict([(x['cód_DSSAT'], x) for x in Ec.ecs_suelo if 'cód_DSSAT' in x.keys()])


def cargar_suelo(nombre, archivo):
    """
    Esta función carga la información de un suelo de un archivo en particular.

    :param nombre: El nombre del suelo.
    :type nombre: str

    :param archivo: El archivo en el cuál se ubica este suelo.
    :type archivo: str

    :return: Un tuple de los diccionarios de información y de coeficientes del suelo.
    :rtype: tuple[dict, dict]

    """

    # Abrir el archivo
    with open(archivo) as d:
        doc = d.readlines()

    # Una lista de tuples que indican dónde empieza y termina cada suelo
    princ = next(i for i, l in enumerate(doc) if re.match(r'\*{}'.format(nombre), l))
    fin = (princ + 1) + next(i for i, l in enumerate(doc[princ + 1:])
                             if re.match(r'\n|\*[\w]{10}', l))

    # Decodar la sección correspondiente del documento
    _, info, coefs = decodar(doc[princ:fin])

    # Devolver el diccionario del suelo
    return info, coefs


def cargar_suelos_doc(archivo):
    """
    Esta función carga todos los suelos presentes en un documento de suelos.

    :param archivo: El documento de suelos.
    :type archivo: str

    :return: Un tuple de listas con los nombres, los diccionarios de información y los diccionarios de coeficientes
    de los suelos.
    :rtype: tuple[list[str], list[dict], list[dict]]

    """

    with open(archivo) as d:
        doc = d.readlines()

    # Una lista de tuples que indican dónde empieza y termina cada suelo
    índs_sl = [(n, (n + 1) + next(i for i, l_s in enumerate(doc[n + 1:]) if re.match('\n|\*[\w]{10}', l_s)))
               for n, l in enumerate(doc) if re.match(r'\*[\w\d_]{10}', l)]

    # Listas para guardar los nombres de los suelos y sus coeficientes e inforamción
    l_dics_coefs = []
    l_dics_info = []
    l_nombres = []

    for u in índs_sl:
        # Decodar cada suelo en el documento
        nombre, dic_info, dic_coefs = decodar(doc[u[0]:u[1]])

        # Agregar el nombre y los parámetros del suelo a las listas respectivas
        l_nombres.append(nombre)
        l_dics_info.append(dic_info)
        l_dics_coefs.append(dic_coefs)

    # Devolver la lista de los nombres y la lista de los diccionarios de parámetros de los suelos
    return l_nombres, l_dics_info, l_dics_coefs


def decodar(doc_suelo):
    """
    Esta función decoda las líneas de un documento de suelos que corresponden a un suelo en particular.

    :param doc_suelo: Una lista de las líneas correspondiendo a un suelo en un archivo DSSAT.
    :type doc_suelo: list[str]

    :return: Un tuple con el nombre y los diccionarios de información y de coeficientes del suelo.
    :rtype: tuple[str, dict, dict]

    """

    # El diccionario para contener los valores leídos del documento
    dic_dssat = {}

    # Sacar el nombre y unos variables individuales de la primera línea
    info = {}

    l_1 = doc_suelo[0].replace('\n', '')
    nombre = l_1[1:11]

    info['fuente'] = l_1[13:24].strip()
    info['textura'] = l_1[25:30].strip()
    info['descrip'] = l_1[37:].strip()

    dic_dssat['profund'] = l_1[31:36].strip()

    # Una lista de tuples de las ubicaciones de las varias secciones de variables en el documento de suelo
    índ_sec_suelo = [(n, (n + 1) + next((i for i, l_s in enumerate(doc_suelo[n + 1:])
                                         if re.match('@', l_s)), len(doc_suelo)))
                     for n, l in enumerate(doc_suelo) if re.match(r'@', l)]

    # Decodar cada sección del documento
    for n, ubic_vars in enumerate(índ_sec_suelo):

        # Leer la lista de códigos de variables (para hacer: arreglar)
        l_vars_dssat = [x.strip() for x in doc_suelo[ubic_vars[0]].replace('@', '').replace('\n', '').split()]

        # Las ubicaciones de los valores en la lista de valores
        ubic_vals = np.array([0] + [Ec.ecs_suelo[DSSAT_a_Tikon[v]['tmñ_DSSAT']] for v in l_vars_dssat]).cumsum()

        # Crear las llaves necesarias en el diccionario de valores DSSAT
        for var in l_vars_dssat:
            dic_dssat[var] = []

        # Leer el valor de cada línea de los variables
        for l in doc_suelo[ubic_vars[0] + 1:ubic_vars[1]]:
            vals = [float(l[u:ubic_vals[n + 1]]) for n, u in enumerate(ubic_vals[:-1])]

            for n_v, var in enumerate(l_vars_dssat):
                dic_dssat[var].append(vals[n_v])

    # El diccionario final del suelo
    coefs = {}

    # Convertir los códigos de variables DSSAT a nombres de variables Tiko'n
    for var_DSSAT, val in dic_dssat:
        try:
            var = DSSAT_a_Tikon[var_DSSAT]
            coefs[var] = dic_dssat[var]
        except KeyError:
            pass

    # Convertir listas a números o a matrices numpy, según sus dimensiones.
    for var, val in coefs.items():

        # Detectar valores que faltan
        val = np.array(val)
        val[val == -99] = np.nan

        # Convertir matrices de únicamente un número a un valor numérico
        if len(val) == 1:
            coefs[var] = val[0]

    # Devolver el diccionario decodado
    return nombre, info, coefs


def escribir(archivo, nombre, dic, borrar=False):
    """

    :param archivo:
    :type archivo:

    :param nombre:
    :type nombre:

    :param dic:
    :type dic:

    :param borrar:
    :type borrar:

    """

    ubic_plantilla = pkg_resources.resource_filename('tikon.Cultivo.ModExtern.DSSAT', 'FILES.txt')

    # Abrir la plantilla general.
    with open(ubic_plantilla, 'r') as d:
        plantilla = d.readlines()

    # Las nuevas líneas que hay que agregar al documento
    nuevas_líneas = []

    for l in plantilla:
        # Para cada línea en la plantilla...

        if re.match('@', l):
            # Si es una línea con nombres de variables...
            nuevas_líneas.append(l)
            l_vars = [x.strip() for x in l.replace('@', '').replace('\n', '').split()]

        else:
            # El número de niveles de los variables en esta sección
            n_niveles = len(dic[l_vars[0]])

            # Agregar una nueva línea para cada nivel
            for i in range(n_niveles):
                # Para cada nivel...

                # Hacer un diccionario con los valores del nivel
                dic = dict([(Ec.ecs_suelo[v]['cód_DSSAT'], dic[v][i] if dic[v][i] != np.nan else -99) for v in l_vars])

                # Agregar la línea formateada con los valores
                nuevas_líneas.append(l.format(dic))

    # Guardar el documento
    if borrar:
        with open(archivo, "w") as d:
            d.write(''.join(nuevas_líneas))
    else:

        with open(archivo, "r+") as d:
            doc = d.readlines()

        try:
            ubic_suelo = [(n, (n + 1) + next(i for i, l_s in enumerate(doc[n + 1:]) if re.match('\n|\*[\w]{10}', l_s)))
                          for n, l in enumerate(doc) if re.match(r'\*{}'.format(nombre), l)]
        except StopIteration:
            ubic_suelo = None

        if ubic_suelo is not None:
            doc[ubic_suelo[0]:ubic_suelo[1]] = []

        doc += nuevas_líneas

        with open(archivo, 'w') as d:
            d.write(''.join(doc))
