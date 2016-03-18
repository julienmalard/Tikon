import io
import json

import REDES.Ecuaciones as Ec


class Organismo(object):
    def __init__(símismo, nombre=None, fuente=None):
        símismo.archivo = None
        símismo.nombre = None
        símismo.etapas = {}
        símismo.config = {}

        símismo.receta = dict(nombre=nombre,
                              etapas={},
                              config={'ecuaciones': None,
                                      'presas': None}
                              )

        if fuente is not None:
            símismo.cargar(fuente)
        else:
            símismo.actualizar()

    def actualizar(símismo):
        símismo.nombre = símismo.receta['nombre']
        símismo.etapas = sorted([x for x in símismo.receta['etapas']], key=lambda d: d['posición'])
        símismo.receta['config'] =

    def añadir_etapa(símismo, nombre, posición, ecuaciones):
        """
        Esta función añade una etapa al organismo.

        :param nombre: El nombre de la etapa. Por ejemplo, "huevo", "juvenil_1", "pupa", "adulto"
        :type nombre: str

        :param posición: La posición cronológica de la etapa. Por ejemplo, "huevo" tendría posición 1, etc.
        :type posición: int

        :param ecuaciones: Un diccionario con los tipos de ecuaciones para este insecto usa. (Siempre se puede cambiar
        más tarde con la función usar_ecuación()). Notar que los nuevos insectos tendrán TODAS las ecuaciones posibles
        en su diccionario inicial; la especificación de ecuación aquí únicamente determina cual(es) de estas se usarán
        para la calibración, simulación, etc.
        Tiene el formato: {nombre_de_la_etapa_1: {Categoría_1: {subcategoría_1: tipo_de_ecuacion, ...} } }
        :type ecuaciones: dict
        """

        # Crear el diccionario inicial para la etapa
        dic_etapa = dict(nombre=nombre,
                         posición=posición,
                         ecuaciones=gen_ec_inic(Ec.ecuaciones),
                         presas=[]
                         )

        # Guardar el diccionario en la receta del organismo
        símismo.receta['etapas'][nombre] = dic_etapa

        # Copiar la selección de ecuaciones para la etapa a la configuración activa del organismo
        for etp, dic_etp in ecuaciones.items():
            config_etp = símismo.receta['config']['ecuaciones'][etp] = {}
            for categ, dic_categ in dic_etp.items():
                config_etp[categ] = {}
                for subcateg, opción in dic_categ.items():
                    config_etp[categ][subcateg] = opción

        # Crear una lista vaciá para eventualmente guardar las presas (si hay) de la nueva etapa
        símismo.receta['config']['presas'][nombre] = []

        # Aumentar la posición de las etapas que siguen la que añadiste
        for etp, dic_etp in símismo.receta['etapas'].items():
            if dic_etp['posición'] >= posición:
                dic_etp['posición'] += 1

        # Actualizar el organismo
        símismo.actualizar()

    def quitar_etapa(símismo, nombre):
        # Quitar el diccionario de la etapa
        """
        Esta función quita una etapa del insecto.
        :param nombre: El nombre de la etapa a quitar (p. ej., "huevo" o "adulto")
        :type nombre: str
        """

        # Guardar la posición de la etapa a quitar
        posición = símismo.receta['etapas'][nombre]['posición']

        # Disminuir la posición de las etapas que siguen la que acabas de quitar
        for etp, dic_etp in símismo.receta['etapas'].items():
            if dic_etp['posición'] >= posición:
                dic_etp['posición'] -= 1

        # Quitar el diccionario de la etapa de la receta del organismo
        símismo.receta['etapas'].pop(nombre)

        # Quitar las ecuaciones de la etapa de la lista de ecuaciones de la configuración actual del organismo
        símismo.receta['config']['ecuaciones'].pop(nombre)

        # Quitar la lista de presas de esta etapa de la configuración actual del organismo
        símismo.receta['config']['presas'].pop(nombre)

        # Actualizar el organismo
        símismo.actualizar()

    def usar_ecuación(símismo, etapa, categoría_ec, tipo_ec):
        dic_etapa = símismo.receta['etapas'][etapa]
        if tipo_ec not in símismo.receta['etapas']['ecuaciones'][categoría_ec]:
            dist_ec = gen_dic_coefs(categoría_ec, tipo_ec)
            dic_etapa['ecuaciones'][categoría_ec][tipo_ec] = dist_ec

        símismo.receta['config']['ecuaciones'][etapa][categoría_ec] = tipo_ec

    def secome(símismo, presa, etps_depred=None, etps_presa=None):

        for e in etps_depred:
            id_etp_presa =
            símismo.config['presas'][e] = id_etp_presa

    def nosecome(símismo, otro_org, etps_depred=None, etps_presa=None):

        for e in etps_depred:
            símismo.config['presas'][e].pop()

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


def gen_ec_inic(dic_ecs, d=None):
    """
    Esta función toma un diccionario de especificaciones de parámetros de ecuaciones y lo convierte en un diccionario
      de distribuciones iniciales.

    :param d: Parámetro que siempre se debe dejar a "None" cuando de usa esta función. Está allí para permetir las
    funcionalidades recursivas de la función (que le permite convertir diccionarios de estructura arbitraria).
    :type d: dict

    :param dic_ecs: El diccionario de las especificaciones de parámetros para cada tipo de ecuación posible
    :type dic_ecs: dict

    :return: d
    :rtype: dict
    """

    # Si es la primera iteración, crear un diccionario vacío
    if d is None:
        d = {}

    # Para cada llave el en diccionario
    for ll, v in dic_ecs.items():
        # Si v también es un diccionario, crear el diccionario correspondiente en d
        if type(v) is dict:
            d[ll] = {}
            gen_ec_inic(v, d)  # y llamar esta función de nuevo
        elif ll == 'límites':  # Si llegamos a la especificación de límites del parámetro
            d[ll] = {}  # Crear el diccionario para contener las calibraciones
            d[ll]['0'] = límites_a_dist(v)  # La distribución inicial siempre tiene el número de identificación '0'.
        else:
            pass

    return d


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

