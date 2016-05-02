import os
import io
import warnings
import json
from datetime import datetime as ft
import matplotlib.pyplot as dib
import numpy as np
import pymc

from INCERT.NuevaCALIB import Experimento, ModBayes
from INCERT import Distribuciones as Ds


class Coso(object):

    # La extensión para guardar recetas de este tipo de objeto
    ext = NotImplemented

    def __init__(símismo, nombre, fuente=None):

        # En 'coefs', ponemos todos los coeficientes del modelo (se pueden organizar en diccionarios). En 'estr',
        # pondremos la información estructural del modelo.

        símismo.receta = dict(coefs={},
                              estr={}
                              )

        # Acordarse de dónde vamos a guardar este Coso
        símismo.fuente = fuente

        # También el nombre, para referencia fácil
        símismo.nombre = nombre

        # Si se especificó un archivo para cargar, cargarlo.
        if fuente is not None:
            símismo.cargar(fuente)

    def guardar(símismo, archivo=''):
        """
        Esta función guarda el Coso para uso futuro
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
        prep_json(símismo.receta['Coefs'])  # Convertir matrices a formato de lista y quitar objetos PyMC, si quedan

        with io.open(archivo, 'w', encoding='utf8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo

    def cargar(símismo, fuente):
        """
        Esta función carga un archivo de receta para crear el Coso.

        :param fuente:
        :type fuente: str

        :return:
        """

        # Si necesario, agregar la extensión y el directorio
        if os.path.splitext(fuente)[1] != '.org':
            fuente += '.org'
        if os.path.split(fuente)[0] == '':
            fuente = os.path.join(os.path.split(__file__)[0], 'Archivos', 'Organismos', fuente)

        # Intentar cargar el archivo (con formato UTF-8)
        try:
            with open(fuente, 'r', encoding='utf8') as d:
                nuevo_dic = json.load(d)

        except IOError as e:  # Si no funcionó, quejarse.
            raise IOError(e)

        else:  # Si se cargó el documento con éxito, usarlo
            # Copiar el documento a la receta de este organismo
            símismo.receta.clear()
            llenar_dic(símismo.receta, nuevo_dic)

            # Convertir listas a matrices numpy en las ecuaciones (coeficientes)
            lista_a_np(símismo.receta['coefs'])


class Simulable(Coso):
    """
    Una subclase de Coso para objetos que se pueden simular y calibrar. (Por ejemplo, una Red AgroEcológica, pero NO
      un Insecto.
    """

    def __init__(símismo, nombre, fuente=None):

        # Primero, llamamos la función de inicio de la clase pariente 'Coso'
        super().__init__(nombre=nombre, fuente=fuente)

        if 'Calibraciones' not in símismo.receta:
            símismo.receta['Calibraciones'] = {'0': 'A prioris no informativos generados automáticamente por TIKON.'}

        símismo.listo = False

        # Contendrá el objeto de modelo Bayesiano para la calibración
        símismo.modelo = None
        símismo.id_calib = None

        símismo.observ = {}

    def actualizar(símismo):
        """

        :return:
        """

        símismo.listo = True

    def prep_simul(símismo, n_pasos, rep_parám, rep_estoc, n_parcelas, calibs):
        """
        Esta funcion prepara las
        :return:
        """
        raise NotImplementedError

    def simular(símismo, vals_inic, paso=1, tiempo_final=120, rep_parám=100, rep_estoc=1, extrn=None, mov=True,
                calibs='Todos'):

        # Actualizar el objeto, si necesario. Si ya se ha actualizado el objeto una vez, no se actualizará
        # automáticamente aquí (y no tendrá en cuenta cambios al objeto desde la última calibración).
        if not símismo.listo:
            símismo.actualizar()

        # Preparar matrices para guardar los resultados de la simulación
        n_parcelas = valid_vals_inic(vals_inic)
        n_pasos = tiempo_final // paso

        símismo.prep_simul(n_pasos=n_pasos, rep_parám=rep_parám, rep_estoc=rep_estoc, n_parcelas=n_parcelas,
                           calibs=calibs)

        # Para cada paso de tiempo, incrementar el modelo
        for i in range(0, tiempo_final // paso):
            símismo.incrementar(paso, i=i + 1, extrn=extrn, mov=mov)

    def incrementar(símismo, paso, i, extrn, mov):
        """

        :param paso: El paso con cual incrementar el modelo
        :type paso: int

        :param i: El número de este incremento en la simulación
        :type i: int

        :param extrn: Un diccionario de valores externos al modelo, si necesario
        :type extrn: dict

        """

        # Dejamos la implementación del incremento del modelo a las subclases individuales.
        raise NotImplementedError

    def prep_calib(símismo, exper):
        """
        Prepara
        :type exper: list

        :return:
        :rtype: (np.ndarray, dict, dict)
        """

        raise NotImplementedError

    def simul_calib(símismo, paso=1, extrn=None):

        """
        Esta es la función que se calibrará cuando se calibra el modelo. Debe devolver las predicciones del modelo
          correspondiendo a los valores observados, y eso en el mismo orden.

        :return: Matriz unidimensional Numpy de las predicciones del modelo correspondiendo a los valores observados.
        :rtype: np.ndarray

        """

        raise NotImplementedError

    def calibrar(símismo, nombre=None, aprioris=None, exper=None, descrip=''):
        """

        :param aprioris:
        :type aprioris: int | str | list | None

        :param exper: Los experimentos vinculados al objeto a usar para la calibración. exper=None lleva al uso de
          todos los experimentos disponibles.
        :type exper: list | Experimento

        """

        # Si se especificó un nombre para la calibración, asegurarse de que no existe en la lista de calibraciones
        # existentes
        if nombre is not None and nombre in símismo.receta['Calibraciones']:
            raise ValueError('Nombre de calibración ya existe en el objeto. Escoger otro nombre y volver a intentar.')

        # Si no se especificó nombre para la calibración, generar un número de identificación aleatorio.
        if nombre is None:
            nombre = int(np.random.uniform() * 1e10)

            # Evitar el caso muy improbable que el código aleatorio ya existe
            while nombre in símismo.receta['Calibraciones']:
                nombre = int(np.random.uniform() * 1e10)

        símismo.id_calib = nombre  # Guardar el nombre para uso futuro (en particular, si guardamos la calibración

        if type(exper) is Experimento:
            exper = [exper]

        obs, dic_parám, dic_líms = símismo.prep_calib(exper=exper)

        # Preparar la lista de distribuciones a priori
        if type(aprioris) is int:
            aprioris = [str(aprioris)]
        elif type(aprioris) is str:
            aprioris = [aprioris]

        símismo.modelo = ModBayes(función=símismo.simul_calib,
                                  obs=obs,
                                  dic_parám=dic_parám,
                                  lista_apriori=aprioris,
                                  dic_líms=dic_líms,
                                  id_calib=nombre)

    def guardar_calib(símismo, descrip):

        if símismo.modelo is None:
            raise ValueError('No hay calibraciones para guardar')

        # Guardar la descripción de esta calibración en el diccionario del objeto
        ahora = ft.now().strftime('%Y-%m-%d %H:%M:%S')
        nb = símismo.id_calib
        símismo.receta['Calibraciones'][nb] = dict(Descripción=descrip,
                                                   Fecha=ahora,
                                                   Config=símismo.receta['estr'].deepcopy())

        # Guardar los resultados de la calibración
        símismo.modelo.guardar()

        # Borrar el objeto de modelo, ya que no se necesita
        símismo.modelo = None

    def añadir_exp(símismo, experimento, corresp, categ):

        """

        :param experimento:
        :type experimento: Experimento

        :param corresp:
        :type corresp: dict

        """
        dic_datos = símismo.observ[experimento.nombre] = corresp.copy()

        llenar_obs(d=dic_datos, exp=experimento, categ=categ)

    def validar(símismo, experimentos, calibs=None, paso=1, rep_parám=100, rep_estoc=100, dibujar=True):


        if not type(experimentos) is list:
            experimentos = [experimentos]

        # Si no se especificaron calibraciones para validar, tomamos la calibración activa, si hay, y en el caso
        # contrario tomamos el conjunto de todas las calibraciones anteriores.
        if calibs is None:
            if símismo.modelo is None:
                calibs = 'Todos'
            else:
                calibs = símismo.modelo.id

        for nombre_exp in experimentos:
            vals_inic =
            tiempo_final =
            extrn =
            mov =


            símismo.simular(vals_inic, paso=paso, tiempo_final=tiempo_final,
                            rep_parám=rep_parám, rep_estoc=rep_estoc,
                            extrn=extrn, mov=mov,
                            calibs=calibs)

            if dibujar:
                símismo.dibujar()

    def dibujar(símismo, mostrar=True, archivo=''):
        """
        Una función para generar gráficos de los resultados del objeto.
        """
        raise NotImplementedError


def llenar_obs(d, exp, categ):

    for ll, v in d.items():
        print (ll, v)
        if type(v) is dict:
            llenar_obs(d=v, exp=exp, categ=categ)

        elif type(v) is list:

            matriz_datos = np.stack([exp.datos[categ]['obs'][x] for x in v])

            d[ll] = matriz_datos.sum(axis=0)


def llenar_dic(d_vacío, d_nuevo):
    """
    Esta función llena un diccionario con los valores de otro diccionario. Es util para evitar quebrar referencias a
      un diccionario mientras tienes que cargarlo de nuevo.

    :param d_vacío: El diccionario vacío original para llenar
    :type d_vacío: dict

    :param d_nuevo: El diccionario con cuyas valores hay que llenar el anterior.
    :type d_nuevo: dict

    """

    for ll, v in d_nuevo.items():  # Para cada itema (llave, valor) en el nuevo diccionario...

        if isinstance(v, dict):  # Si el valor es otro diccionario...

            if ll not in d_vacío.keys():
                d_vacío[ll] = {}

            llenar_dic(d_vacío[ll], v)  # ... llamar esta misma función con el nuevo diccionario

        else:  # Si el valor NO era otro diccionario...

            # Copiar el nuevo valor a la llave
            d_vacío[ll] = d_nuevo[ll]


def lista_a_np(d):
    """
    Esta función recursiva toma las matrices numpy contenidas en un diccionario de estructura arbitraria y las
      convierte en listas numéricas. Cambia el diccionario in situ, así que no devuelve ningún valor.
      Una nota importante: esta función puede tomar diccionarios de estructura arbitraria, pero no convertirá
      exitosamente diccionarios que contienen listas que a su turno contienen otras listas para convertir a matrices
      numpy. No hay problema con listas compuestas representando matrices multidimensionales.

    :param d: El diccionario a convertir
    :type d: dict

    """

    for ll, v in d.items():  # Para cada itema (llave, valor) del diccionario
        if type(v) is dict:  # Si el itema era otro diccionario...
            prep_json(v)  # Llamar esta función de nuevo
        elif type(v) is list:  # Si el itema era una lista...
            try:
                d[ll] = np.array(v, dtype=float)  # Ver si se puede convertir a una matriz numpy
            except ValueError:
                pass  # Si no funcionó, pasar al siguiente


def prep_json(d):
    """
    Esta función recursiva toma las listas numéricas contenidas en un diccionario de estructura arbitraria y las
      convierte en matrices de numpy. También quita variables de typo PyMC que no sa han guardado en forma de matriz.
      Cambia el diccionario in situ, así que no devuelve ningún valor.
      Una nota importante: esta función puede tomar diccionarios de estructura arbitraria, pero no convertirá
      exitosamente diccionarios que contienen listas.

    :param d: El diccionario para convertir
    :type d: dict

    """

    for ll, v in d.items():  # Para cada itema (llave, valor) del diccionario
        if type(v) is dict:  # Si el itema era otro diccionario...
            lista_a_np(v)  # ...llamar esta función de nuevo con el nuevo diccionario

        elif type(v) is np.ndarray:  # Si el itema era una matriz numpy...
            d[ll] = v.tolist()  # ...convertir la matriz al formato de lista.

        elif isinstance(v, pymc.Stochastic):  # Si el itema es un variable de PyMC...
            d.pop(ll)  # ... borrarlo


def valid_vals_inic(d, n=None):

    for ll, v in d.items():
        if type(v) is dict:
            valid_vals_inic(v, n)
        elif type(v) is np.ndarray:
            n_parcelas = v.shape()[0]
            if n is None:
                n = n_parcelas
            elif n_parcelas != n:
                raise ValueError('Error en el formato de los datos iniciales')

    return n


def filtrar_comunes(lista_paráms):
    """
    Esta función devuelve los nombres de las calibraciones que están en común entre todos los parámetros de una lista
      de diccionarios de parámetros.

    :param lista_paráms: El diccionario con los parámetros.
    :type lista_paráms: list

    """

    # Crear una lista con únicamente los nombres de las calibraciones de cada parámetro, sin cualquier otra
    # estructura de diccionario. La lista final tiene la forma:
    #   [[calib1, calib2, calib3], [calib2, calib3, calib4], [calib1, calib4], ...]

    lista_comunes = [x for y in lista_paráms for x in y if False not in [x in z for z in lista_paráms]]
    lista_comunes = list(set(lista_comunes))  # Quitar valores duplicados

    return lista_comunes


def gen_matr_coefs(dic_parám, calibs, n_rep_parám):
    """
    Esta función genera una matríz de valores posibles para un coeficiente, dado los nombres de las calibraciones
      que queremos usar y el número de repeticiones que queremos.

    :param dic_parám: Un diccionario de un parámetro con todas sus calibraciones
    :param calibs: Cuales calibraciones hay que incluir

    :return:
    :rtype: np.ndarray

    """

    # Hacer una lista con únicamente las calibraciones que estén presentes y en la lista de calibraciones acceptables,
    # y en el diccionario del parámetro

    if calibs == 'todos':
        calibs_usables = [x for x in dic_parám]

    elif type(calibs) == list:
        calibs_usables = [x for x in dic_parám if x in calibs]

    else:
        raise ValueError

    # Si el perámetro no tiene calibraciones acceptables, usar el a priori no informativo como calibración
    if len(calibs_usables) == 0:
        calibs_usables = ['0']

        raise Warning('Un parámetro no tiene ninguna de las calibraciones especificadas. Voy a usar el a priori no '
                      'informativo.')

    # La lista para guardar las partes de las trazas de cada calibración que queremos incluir en la traza final
    lista_calibs = []

    n_calibs = len(calibs_usables)
    rep_per_calib = np.array([n_rep_parám // n_calibs] * n_calibs)

    resto = n_rep_parám % n_calibs
    rep_per_calib[:resto + 1] += 1

    for n_id, id_calib in enumerate(calibs_usables):

        traza = dic_parám[id_calib]

        if type(traza) is np.ndarray:
            if rep_per_calib[n_id] > len(dic_parám[id_calib]):

                warnings.warn('Número de replicaciones superior al tamaño de la traza de '
                              'parámetro disponible.')
                devolver = True
            else:
                devolver = False

            nuevos_vals = np.random.choice(traza, size=rep_per_calib[n_id], replace=devolver)

        elif type(traza) is str:
            dist_sp = Ds.texto_a_distscipy(traza)
            nuevos_vals = dist_sp.rvs(rep_per_calib[n_id])

        elif isinstance(traza, pymc.Stochastic):
            # Si es un variable de calibración activo, poner el variable sí mismo en la matriz

            nuevos_vals = traza

        else:
            raise ValueError

        lista_calibs.append(nuevos_vals)

    return np.concatenate(lista_calibs)


def gráfico(matr_predic, vector_obs, nombre, etiq_y='Población', etiq_x='Día', color=None, mostrar=True, archivo=''):
    """

    :param matr_predic:
    :type matr_predic: np.ndarray

    :param vector_obs:
    :param nombre:
    :param etiq_y:
    :param etiq_x:
    :param color:
    :param mostrar:
    :param archivo

    """

    assert len(vector_obs) == matr_predic.shape[2]

    if color is None:
        color = '#99CC00'

    if mostrar is False:
        if len(archivo) == 0:
            raise ValueError('Hay que especificar un archivo para guardar el gráfico de %s.' % nombre)

    prom_predic = matr_predic.mean(axis=(0,1))

    x = np.arange(len(vector_obs))

    dib.plot(x, prom_predic, lw=2, color=color)

    dib.plot(x, vector_obs, 'o', color=color)

    # Una matriz sin el incertidumbre estocástico
    matr_prom_estoc = matr_predic.mean(axis=0)

    # Ahora, el eje 0 es el eje de incertidumbre paramétrica
    máx_parám = matr_prom_estoc.max(axis=0)
    mín_parám = matr_prom_estoc.min(axis=0)

    dib.fill_between(x, máx_parám, mín_parám, facecolor=color, alpha=0.5)

    máx_total = matr_predic.max(axis=(0,1))
    mín_total = matr_predic.min(axis=(0,1))

    dib.fill_between(x, máx_total, mín_total, facecolor=color, alpha=0.3)

    dib.xlabel(etiq_x)
    dib.ylabel(etiq_y)
    dib.title(nombre)

    if mostrar is True:
        dib.show()
    else:
        if '.png' not in archivo:
            archivo = os.path.join(archivo, nombre + '.png')
        dib.savefig(archivo)
