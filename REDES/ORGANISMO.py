import io
import json
import numpy as np

import REDES.Ecuaciones as Ec


class Organismo(object):
    def __init__(símismo, nombre=None, fuente=None):
        símismo.fuente = fuente
        símismo.nombre = None
        símismo.etapas = {}

        símismo.receta = dict(nombre=nombre,
                              etapas={},
                              config={'ecuaciones': None,
                                      'presas': None}
                              )

        # Si se especificó un archivo para cargar, cargarlo.
        if fuente is not None:
            try:  # Intentar cargar el archivo (con formato UTF-8)
                with open(fuente, 'r', encoding='utf8') as d:
                    nuevo_dic = json.load(d)

                llenar_dic(símismo.receta, nuevo_dic)

                # Convertir listas a matrices numpy en las ecuaciones (coeficientes) de las etapas
                for dic_etp in símismo.receta['etapas']:
                    lista_a_np(dic_etp['ecuaciones'])

            except IOError as e:  # Si no funcionó, hay que quejarse.
                raise IOError(e)

        # Actualizar el insecto
        símismo.actualizar()

    def actualizar(símismo):
        """
        Esta función simplemente se asegura de que todo en el organismo esté actualizado según la configuración
          actual en la receta. Si hay cualquier atributo del organismo que depiende de valore(s) en la receta,
          aquí es el lugar par actualizarlos.
        Esta función se llama automáticamente después de funciones tales como "secome()" y "quitar_etapa()".

        :return: Nada
        """

        # Actualizar el nombre del organismo
        símismo.nombre = símismo.receta['nombre']

        # Actualizar la lista de etapas según el orden cronológico de dichas etapas.
        símismo.etapas = sorted([x for x in símismo.receta['etapas']], key=lambda d: d['posición'])

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

    def aplicar_ecuación(símismo, etapa, tipo_ec):
        """
        Esta función aplica una configuración de ecuaciones a una etapa específica del organismo. No borar otras
          ecuaciones, sino simplemente cambia la ecuación activa usada para calibraciones, simulaciones, etc.

        :param etapa: El nombre de la etapa a cual esta ecuación se aplicará
        :type etapa: str

        :param tipo_ec: Un diccionario del tipo de ecuación que se aplicará. Debe tener el formato
          {categoría: {sub_categoría: opción_ecuación, sub_categoría: opción_ecuación, ...}, categoría: ...}
        :type tipo_ec: dict
        """

        for categ, dic_categ in tipo_ec.items():
            for sub_categ, opción_ec in dic_categ.items():
                símismo.receta['config']['ecuaciones'][etapa][categ][sub_categ] = opción_ec

    def secome(símismo, presa, etps_depred=None, etps_presa=None):
        """
        Esta función establece relaciones de depredador y presa entre organismos.

        :param presa: La presa (usar un objeto Organismo, no el nombre de la presa).
        :type presa: Organismo

        :param etps_depred: Lista de los nombres (cadena de carácteres) de las fases del depredador (este organismo)
          que se comen a la presa. Si se deja como "None", tomará todas las fases.
        :type etps_depred: list

        :param etps_presa: Lista de los nombres (cadena de carácteres) de las fases de la presa que se come el
          depredador (este organismo). Si se deja como "None", tomará todas las fases.
        :type etps_presa: list

        """

        # Si no se especificaron estapas específicas, tomar todas las etapas de los organismos.
        if etps_depred is None:
            etps_depred = [x for x in símismo.receta['etapas']]
        if etps_presa is None:
            etps_presa = [x for x in presa.receta['etapas']]

        # Si se le olvidó al utilisador poner sus etapas en forma de lista, hacerlo aquí
        if type(etps_presa) is str:
            etps_presa = [etps_presa]
        if type(etps_depred) is str:
            etps_depred = [etps_depred]

        # Guardar la relación de deprededor y presa en la configuración del organismo
        for e_depred in etps_depred:
            símismo.receta['config']['presas'][e_depred] = etps_presa

        # Reactualizar el organismo (necesario para asegurarse que las ecuaciones de depredador y prese tienen
        # todos los coeficientes necesarios para la nueva presa
        símismo.actualizar()

    def nosecome(símismo, presa, etps_depred=None, etps_presa=None):
        """
        Esta función borra relaciones de depredador y presa entre organismos.

        :param presa: La presa que ya no se come (usar un objeto Organismo, no el nombre de la presa).
        :type presa: Organismo

        :param etps_depred: Lista de los nombres (cadena de carácteres) de las fases del depredador (este organismo)
          que ya no se comen a la presa. Si se deja como "None", tomará todas las fases.
        :type etps_depred: list

        :param etps_presa: Lista de los nombres (cadena de carácteres) de las fases de la presa que ya no se come el
          depredador (este organismo). Si se deja como "None", tomará todas las fases.
        :type etps_presa: list

        """

        # Si no se especificaron estapas específicas, tomar todas las etapas de los organismos.
        if etps_depred is None:
            etps_depred = [x for x in símismo.receta['etapas']]
        if etps_presa is None:
            etps_presa = [x for x in presa.receta['etapas']]

        # Si se le olvidó al utilisador poner sus etapas en forma de lista, hacerlo aquí
        if type(etps_presa) is str:
            etps_presa = [etps_presa]
        if type(etps_depred) is str:
            etps_depred = [etps_depred]

        # Quitar la relación de deprededor y presa en la configuración del organismo
        for e_depred in etps_depred:  # Para cada etapa especificada del depredador...
            # Quitar cada etapa especificada de la presa
            for e_presa in etps_presa:
                símismo.receta['config']['presas'][e_depred].pop(e_presa)

            # Si ya no quedan estapas del organismo como presas, quitar su nombre del diccionario de presas
            if len(símismo.receta['config']['presas'][e_depred]) == 0:
                símismo.receta['config']['presas'].pop(e_depred)

        # No se reactualiza el organismo; los parámetros de interacciones con la antigua presa se quedan la receta
        # del organismo para uso futuro potencial.

    def guardar(símismo, archivo=''):
        """
        Esta función guardar el organismo para uso futuro
        :param archivo:
        :return:
        """

        # Si no se especificó archivo...
        if archivo == '':
            if símismo.fuente != '':
                archivo = símismo.fuente  # utilizar el archivo existente
            else:
                # Si no hay archivo existente, tenemos un problema.
                raise FileNotFoundError('Hay que especificar un archivo para guardar el organismo.')

        # Guardar el documento de manera que preserve carácteres no latinos (UTF-8)
        for dic_etp in símismo.receta['etapas']:  # Convertir matrices a formato de lista
            np_a_lista(dic_etp['ecuaciones'])

        with io.open(archivo, 'w', encoding='utf8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo


def llenar_dic(d_vacío, d_nuevo):
    """
    Esta función llena un diccionario con los valores de otro diccionario. Es util para situaciones dónde hay que
      asegurarse de que el formato de un diccionario que estamos cargando esté correcto.

    :param d_vacío: El diccionario vacío original para llenar
    :type d_vacío: dict

    :param d_nuevo: El diccionario con cuyas valores hay que llenar el anterior.
    :type d_nuevo: dict

    :return: nada
    """

    for ll, v in d_nuevo.items():
        if isinstance(v, dict):
            llenar_dic(d_vacío[ll], v)
        else:
            try:
                d_vacío[ll] = d_nuevo[ll]
            except KeyError:
                raise Warning('Diccionario pariente no contiene todas las llaves a llenar.')


def gen_ec_inic(dic_ecs, inter=None, d=None):
    """
    Esta función toma un diccionario de especificaciones de parámetros de ecuaciones y lo convierte en un diccionario
      de distribuciones iniciales.

    :param d: Parámetro que siempre se debe dejar a "None" cuando de usa esta función. Está allí para permetir las
      funcionalidades recursivas de la función (que le permite convertir diccionarios de estructura arbitraria).
    :type d: dict

    :param inter: Un diccionario, si se aplica, de las interacciones con otros organismos necesarios para establecer
      las ecuaciones de manera correcta. Un ejemplo común sería el diccionario de las presas de una etapa
      para establecer las ecuaciones de depredación.
    :type inter: dict

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
            gen_ec_inic(v, inter, d)  # y llamar esta función de nuevo

        elif ll == 'límites':  # Si llegamos a la especificación de límites del parámetro

            # Si no hay interacciones con otros organismos para este parámetro...
            if dic_ecs['inter'] is None:
                d[ll] = {}  # Crear el diccionario para contener las calibraciones
                d[ll]['0'] = límites_a_dist(v)  # La distribución inicial siempre tiene el número de identificación '0'.

            # Si hay interacciones con las presas de la etapa...
            elif dic_ecs['inter'] == 'presa':
                try:
                    d[ll] = dict([(p, None) for p in inter['presas']])
                except KeyError:  # Si no hay presas, el parámetro se queda vacío
                    d[ll] = {}
                    continue
                for p in d[ll]:
                    d[ll][p] = dict([(etp, límites_a_dist(v)) for etp in inter['presas'][p]])

            else:
                raise ValueError

        else:
            pass

    return d


def límites_a_dist(límites, cont=True):
    """
    Esta función toma un "tuple" de límites para un parámetro de una función y devuelve una descripción de una
      destribución a priori no informativa (espero) para los límites dados. Se usa en la inicialización de las
      distribuciones de los parámetros de ecuaciones.

    :param límites: Las límites para los valores posibles del parámetro. Para límites infinitas, usar np.inf y
      -np.inf. Ejemplos: (0, np.inf), (-10, 10), (-np.inf, np.inf). No se pueden especificar límites en el rango
      (-np.inf, R), donde R es un número real. En ese caso, usar las límites (R, np.inf) y tomar el negativo del
      variable en las ecuaciones que lo utilisan.
    :type límites: tuple

    :param cont: Determina si el variable es continuo o discreto
    :type cont: bool

    :return: Descripción de la destribución no informativa que conforme a las límites especificadas. Devuelve una
      cadena de carácteres, que facilita guardar las distribuciones de los parámetros. Otras funciones la convertirán
      en distribución de scipy o de pymc donde necesario.
    :rtype: str
    """

    # Sacar el mínimo y máximo de los límites.
    mín = límites[0]
    máx = límites[1]

    # Verificar que máx > mín
    if máx <= mín:
        raise ValueError('El valor máximo debe ser superior al valor máximo.')

    # Pasar a través de todos los casos posibles
    if mín == -np.inf:
        if máx == np.inf:  # El caso (-np.inf, np.inf)
            if cont:
                dist = 'Normal(0, 1e10)'
            else:
                dist = 'DiscrUnif(1e-10, 1e10)'

        else:  # El caso (-np.inf, R)
            raise ValueError('Tikón no tiene funcionalidades de distribuciones a priori en intervalos (-inf, R). Puedes'
                             'crear un variable en el intervalo (R, inf) y utilisar su valor negativo en las '
                             'ecuaciones.')

    else:
        if máx == np.inf:  # El caso (R, np.inf)
            if cont:
                dist = 'Expon({}, 1e10)'.format(mín)
            else:
                loc = mín - 1
                dist = 'Geom(1e-8, {})'.format(loc)

        else:  # El caso (R, R)
            if cont:
                dist = 'Unif~({}, {})'.format(mín, máx)
            else:
                dist = 'DiscrUnif~({}, {})'.format(mín, mín+1)

    return dist


def np_a_lista(d):
    """
    Esta función toma las matrices numpy contenidas en un diccionario de estructura arbitraria y las convierte
      en listas numéricas. Cambia el diccionario in situ, así que no devuelve ningún valor.

    :param d: El diccionario a convertir
    :type d: dict
    :return: nada
    """

    for ll, v in d.items():
        if type(v) is dict:
            np_a_lista(v)
        elif type(v) is list:
            try:
                d[ll] = np.array(v, dtype=float)
            except ValueError:
                pass


def lista_a_np(d):
    """
    Esta función toma las listas numéricas contenidas en un diccionario de estructura arbitraria y las convierte
      en matrices de numpy. Cambia el diccionario in situ, así que no devuelve ningún valor.
    :param d: El diccionario a convertir
    :type d: dict
    :return: nada
    """

    for ll, v in d.items():
        if type(v) is dict:
            lista_a_np(v)
        elif type(v) is np.ndarray:
            d[ll] = v.tolist()
