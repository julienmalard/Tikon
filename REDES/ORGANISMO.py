import io
import json


class Organismo(object):
    def __init__(símismo, nombre=None, etapas=None, fuente=None):
        símismo.archivo = None
        símismo.nombre = None
        símismo.etapas = {}
        símismo.config = {}

        símismo.receta = dict(nombre=nombre,
                              etapas=etapas,
                              config=None
                              )

        if fuente is not None:
            símismo.cargar(fuente)
        else:
            símismo.actualizar()

    def actualizar(símismo):
        símismo.nombre = símismo.receta['nombre']
        símismo.etapas = sorted([x for x in símismo.receta['etapas']], key=lambda d: d['posición'])
        símismo.config =

    def añadir_etapa(símismo, nombre, posición, ecuaciones):
        # Crear el diccionario para la etapa
        dic_etapa = dict(nombre=nombre,
                         posición=posición,
                         ecuaciones={'Crecimiento': None,
                                     'Depredación': None,
                                     'Muertes': None,
                                     'Transiciones': None,
                                     'Movimiento': None})

        llenar_dic(dic_etapa['ecuaciones'], ecuaciones)

        # Guardar el diccionario
        símismo.receta['etapas'][nombre] = dic_etapa
        # Actualizar el organismo
        símismo.actualizar()

    def quitar_etapa(símismo, nombre):
        # Quitar el diccionario de la etapa
        símismo.receta['etapas'].pop(nombre)
        # Actualizar el organismo
        símismo.actualizar()

    def poner_ecuación(símismo, etapa, categoría_ec, tipo_ec):
        if tipo_ec not in símismo.receta['etapas']['ecuaciones'][categoría_ec]:
            símismo.receta['etapas']['ecuaciones'][categoría_ec][tipo_ec] =
        símismo.receta['config'][etapa][categoría_ec] = dic_ec



    def secome(símismo, otro_org, etps_símismo=None, etps_otro=None):
        pass

    def nosecome(símismo, otro_org, etps_símismo=None, etps_otro=None):
        pass

    def cargar(símismo, archivo):
        """
        Esta función carga un documento de organismo ya guardado
        :param archivo:
        :return:
        """

        try:  # Intentar cargar el archivo
            with open(archivo, 'r', encoding='utf8') as d:
                nuevo_dic = json.load(d)
            llenar_dic(símismo.receta, nuevo_dic)
            símismo.archivo = archivo  # Guardar la ubicación del archivo activo de la red

            símismo.actualizar()

        except IOError as e:
            raise IOError(e)

    def guardar(símismo, archivo=''):
        """
        Esta función guardar el organismo para uso futuro
        :param archivo:
        :return:
        """

        # Si no se especificó archivo...
        if archivo == '':
            if símismo.archivo != '':
                archivo = símismo.archivo  # utilizar el archivo existente
            else:
                # Si no hay archivo existente, tenemos un problema.
                raise FileNotFoundError('Hay que especificar un archivo para guardar el organismo.')

        # Guardar el documento de manera que preserve carácteres no latinos (UTF-8)
        with io.open(archivo, 'w', encoding='utf8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)


def llenar_dic(d_orig, d_nuevo):
    vaciar_dic(d_orig)
    for ll, v in d_nuevo.items:
        if isinstance(v, dict):
            llenar_dic(d_orig[ll], v)
        else:
            try:
                d_orig[ll] = d_nuevo[ll]
            except KeyError:
                raise Warning('Diccionario pariente no contiene todas las llaves a llenar.')


def vaciar_dic(d):
    """
    Esta función vacía un diccionario y poner cada valor igual a "None". Es muy útil para asegurarse de que un
    diccionario esté vacío antes de llenarlo con nuevas valores.
    :param d: diccionario a vaciar
    :return: nada
    """
    for ll, v in d.items():
        if isinstance(v, dict):
            vaciar_dic(v)
        else:
            d[ll] = None


import scipy.stats as estad
import numpy as np

ecuaciones = dict(Crecimiento={'Modif': {None: None,
                                         'Regular': {'r': (0, np.inf)},
                                         'Log Normal Temperatura':{'t': (0, np.inf),
                                                                   'p': (0, np.inf)},
                                         },
                               'Ecuaciones': {None: None,
                                              'Exponencial': {},
                                              'Logístico': {}}
                               },
                  Depredación={None: None,
                               'Tipo I_Dependiente presa': {'a': (0, np.inf)},
                               'Tipo II_Dependiente presa': {'a': (0, np.inf),
                                                             'b': (0, np.inf)},
                               'Tipo III_Dependiente presa': {'a': (0, np.inf),
                                                             'b': (0, np.inf)},
                               'Tipo I_Dependiente ratio': {'a': (0, np.inf)},
                               'Tipo II_Dependiente ratio': {'a': (0, np.inf),
                                                             'b': (0, np.inf)},
                               'Tipo III_Dependiente ratio': {'a': (0, np.inf),
                                                             'b': (0, np.inf)},
                               'Beddington-DeAngelis': {'a': (0, np.inf),
                                                        'b': (0, np.inf),
                                                        'c': (0, np.inf)},
                               'Tipo I_Hassell-Varley': {'a': (0, np.inf),
                                                         'm': (0, np.inf)},
                               'Tipo II_Hassell-Varley': {'a': (0, np.inf),
                                                          'b': (0, np.inf),
                                                          'm': (0, np.inf)},
                               'Tipo III_Hassell-Varley': {'a': (0, np.inf),
                                                          'b': (0, np.inf),
                                                          'm': (0, np.inf)},
                               'Asíntota Doble': {'a': (0, np.inf),
                                                  'b': (0, np.inf),
                                                  'c': (0, np.inf)}
                               },
                  Muertes=None,
                  Transiciones=None,
                  Movimiento=None
                  )


def límites_a_dist(límites, cont=True):
    mín = límites[0]
    máx = límites[1]
    if abs(mín) == np.inf:
        if abs(máx) == np.inf:
            if cont:
                dist = estad.norm(loc=0, scale=1e10)
            else:
                dist = estad.randint(1e-10, 1e10)
        else:
            if cont:
                dist = NotImplemented
            else:
                dist = NotImplemented

    else:
        if abs(máx) == np.inf:
            if cont:
                dist = estad.expon(loc=mín, scale=1e10)
            else:
                dist = estad.geom(1e-8, loc=mín-1)
        else:
            if cont:
                dist = estad.uniform(mín, máx)
            else:
                dist = estad.randint(mín, mín+1)


    return dist

