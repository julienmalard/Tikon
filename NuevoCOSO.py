import os
import io
import warnings
import json
from datetime import datetime as ft
import matplotlib.pyplot as dib
import numpy as np
import pymc

from INCERT.NuevaCALIB import ModBayes
from INCERT.DATOS import Experimento
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

        # Para guardar los objetos relacionados con este Simulable
        símismo.objetos = []

        símismo.listo = False

        # Contendrá el objeto de modelo Bayesiano para la calibración
        símismo.modelo = None

        # El nombre de la calibración
        símismo.id_calib = None

        # Experimentos asociados
        símismo.exps = {}

        # Predicciones del modelo correspondiendo a los Experimentos asociados
        símismo.predics_exps = {}

        # Datos observados
        símismo.observ = {}

        # Predicciones de datos
        símismo.predics = {}

    def actualizar(símismo):
        """
        Esta función actualiza las matrices internas del Simulable para prepararlo para una simulación.
          Se aplica individualmente en todas las subclases de Simulable, que también deben llamar esta función al
          final para poner símismo.listo = True.

        """

        símismo.listo = True

    def simular(símismo, vals_inic, paso=1, tiempo_final=120, rep_parám=100, rep_estoc=1, extrn=None,
                calibs='Todos'):

        # Actualizar el objeto, si necesario. Si ya se ha actualizado el objeto una vez, no se actualizará
        # automáticamente aquí (y no tendrá en cuenta cambios al objeto desde la última calibración).
        if not símismo.listo:
            símismo.actualizar()

        # Unos números útiles
        n_parcelas = valid_vals_inic(vals_inic)
        n_pasos = tiempo_final // paso

        # Llenar las matrices internas de coeficientes
        símismo.llenar_coefs(n_rep_parám=rep_parám, calibs=calibs)

        # Preparar las matrices internas para guardar las predicciones
        símismo.prep_predics(n_pasos=n_pasos, rep_parám=rep_parám, rep_estoc=rep_estoc, n_parcelas=n_parcelas,
                             calibs=calibs)

        # Simular el modelo
        símismo.calc_simul(paso=paso, n_pasos=n_pasos, extrn=extrn)

    def llenar_coefs(símismo, n_rep_parám, calibs):
        """
        Transforma los diccionarios de coeficientes a matrices internas (para aumentar la rapidez de la simulación).
          Las matrices internas, por supuesto, dependerán del tipo de Simulable en cuestión. No obstante, todas
          tienen la forma siguiente: eje 0 = parcela, eje 1 = repetición estocástica, eje 2 = repetición paramétrica,
          eje 3+ : dimensiones opcionales.

        :param n_rep_parám:
        :param calibs:

        """

        raise NotImplementedError

    def prep_predics(símismo, n_pasos, rep_parám, rep_estoc, n_parcelas, calibs):
        """
        Esta funcion prepara las

        """
        raise NotImplementedError

    def calc_simul(símismo, paso, n_pasos, extrn=None):

        # Para cada paso de tiempo, incrementar el modelo
        for i in range(0, n_pasos):
            símismo.incrementar(paso, i=i + 1, extrn=extrn)

    def incrementar(símismo, paso, i, extrn):
        """
        Esta función incrementa el modelo por un paso.
        
        :param paso: El paso con cual incrementar el modelo
        :type paso: int

        :param i: El número de este incremento en la simulación
        :type i: int

        :param extrn: Un diccionario de valores externos al modelo, si necesario
        :type extrn: dict

        """

        # Dejamos la implementación del incremento del modelo a las subclases individuales.
        raise NotImplementedError

    def calibrar(símismo, nombre=None, aprioris=None, exper=None, descrip='', paso=1,
                 rep=10000, quema=100, extraer=10):
        """
        Para calibrar un modelo, hay algunas cosas que hacer:
          1. Estar seguro de el el nombre de la calibración sea válido
          2. Preparar listas de parámetros a calibrar, tanto como de sus límites matemáticas (para estar seguro de no
             calibrar un parámetro afuera de sus límites teoréticas).
          3. Generar la lista de nombres de calibraciones anteriores para emplear como distribuciones a prioris
             en la calibración de cada parámetro.
          4. Preparar los argumentos para la calibración, dado los experimentos vinculados.
          5. Generar un vector unidimensional, en orden reproducible, de las observaciones de los experimentos (para
             comparar más rápido después con las predicciones del modelo).
          6. Crear el modelo (ModBayes) para la calibración
          7. Por fin, calibrar el modelo.

        :param aprioris:
        :type aprioris: int | str | list | None

        :param exper: Los experimentos vinculados al objeto a usar para la calibración. exper=None lleva al uso de
          todos los experimentos disponibles.
        :type exper: list | Experimento

        """

        # 1. Primero, validamos el nombre y, si necesario, lo creamos.
        # Si se especificó un nombre para la calibración, asegurarse de que no existe en la lista de calibraciones
        # existentes
        if nombre is not None and nombre in símismo.receta['Calibraciones']:
            raise ValueError('Nombre de calibración ya existe en el objeto. Escoger otro nombre y volver a intentar.')

        # Si no se especificó nombre para la calibración, generar un número de identificación aleatorio.
        if nombre is None:
            nombre = int(np.random.uniform() * 1e10)

            # Evitar el caso muy improbable de que el código aleatorio ya existe
            while nombre in símismo.receta['Calibraciones']:
                nombre = int(np.random.uniform() * 1e10)

        símismo.id_calib = nombre  # Guardar el nombre para uso futuro (en particular, si guardamos la calibración).

        # 2. Creamos la lista de parámetros que hay que calibrar
        lista_params, lista_líms = símismo.gen_lista_coefs_interés_todo()

        # 3. Filtrar coeficientes por calib
        if type(aprioris) is int:
            aprioris = [str(aprioris)]
        elif type(aprioris) is str:
            aprioris = [aprioris]
        lista_aprioris = []  # para hacer

        # 4. Preparar el diccionario de argumentos para la función "simul_calib", según los experimentos escogidos
        # para la calibración.

        if exper is None:
            # Si "exper" no se especificó, usar todos los experimentos vinculados con el Simulable
            exper = list(símismo.exps)

        if type(exper) is not list:
            # Si exper no era una lista, hacer una.
            exper = [exper]

        for n, exp in enumerate(exper):
            if type(exp) is Experimento:
                exper[n] = exp.nombre

        dic_argums = símismo.prep_args_calib(exper=exper)
        dic_argums[paso] = paso  # Guardar el paso en el diccionario también

        # 5. Generar el vector numpy de observaciones para los experimentos
        obs = símismo.prep_obs_exper(exper=exper)

        # 6. Creamos el modelo ModBayes de calibración, lo cual genera variables PyMC
        símismo.modelo = ModBayes(función=símismo.simul_calib,
                                  dic_argums=dic_argums,
                                  obs=obs,
                                  lista_paráms=lista_params,
                                  lista_apriori=lista_aprioris,
                                  lista_líms=lista_líms,
                                  id_calib=nombre)

        # 7. Llenamos las matrices de coeficientes con los variables PyMC recién creados
        símismo.llenar_coefs(n_rep_parám=1, calibs=nombre)

        # 8. Calibrar el modelo, llamando las ecuaciones bayesianas a través del objeto ModBayes
        símismo.modelo.calib(rep=rep, quema=quema, extraer=extraer)

    def gen_lista_coefs_interés_todo(símismo):

        """
        Esta función devuelve una lista de todos los coeficientes de un Simulable y de todos sus objetos de manera
          recursiva, tanto como una lista, en el mismo orden, de los límites de dichos coeficientes.

        :return: Un tuple conteniendo una lista de todos los coeficientes de interés para la calibración y una lista
          de sus límites.
        :rtype: (list, list)

        """

        def sacar_coefs_recursivo(objeto):
            """
            La implementación recursiva de la función.

            :param objeto: El objeto Simulable a cual hay que sacar los coeficientes.
            :type objeto: Simulable

            :return: Un tuple, como descrito en la documentación de la función arriba.
            :rtype: (list, list)
            """

            # Inicializar las listas de coeficientes y de límites con los coeficientes y límites del objeto actual.
            lista_coefs = objeto.sacar_coefs_interno()
            lista_líms = objeto.sacar_líms_coefs_interno()

            # Ahora, hacer lo mismo para cada objeto contenido en este objeto.
            for obj in objeto.objetos:
                resultado = sacar_coefs_recursivo(obj)
                lista_coefs += resultado[0]
                lista_líms += resultado[1]

            # Devolver la lista de coeficientes y la lista de límites
            return lista_coefs, lista_líms

        # Implementar la función recursiva arriba
        return sacar_coefs_recursivo(símismo)

    def sacar_coefs_interno(símismo):
        """
        Esta función genera una lista de los coeficientes propios al objeto de interés para la calibración actual.
          Se debe implementar para cada Coso (objeto) que tiene coeficientes.

        :return: Una lista de diccionarios de coeficientes, con el formato siguiente:
           [ {calib1: distribución o [lista de valores],
              calib2: ibid,
              ...},
              {coeficiente 2...},
              ...
           ]
        :rtype: list

        """

        raise NotImplementedError

    def sacar_líms_coefs_interno(símismo):
        """
        Esta función genera una lista de las límites de los coeficientes propios al objeto de interés para la
          calibración actual. Se debe implementar para cada Coso (objeto) que tiene coeficientes.

        :return: Un tuple, conteniendo:
          1. Una lista de diccionarios de coeficientes, con el formato siguiente:
           [ {calib1: distribución o [lista de valores],
              calib2: ibid,
              ...},
              {coeficiente 2...},
              ...
           ]

           2. Una lista de los límites de los coeficientes, en el mismo orden que (1.)
        :rtype: (list, list)

        """

        raise NotImplementedError

    def prep_obs_exper(símismo, exper):
        """
        Prepara

        :param exper: Una lista de los nombres de los experimentos que vamos a incluir para esta calibración.
        :type exper: list

        :return:
        :rtype: np.ndarray
        """

        raise NotImplementedError

    def prep_args_calib(símismo, exper):
        """

        :param exper: Una lista de los nombres de los experimentos para incluir
        :type exper: list

        :return: Un diccionario del formato siguiente:
           {
            datos_inic: {},
            n_pasos: {},
            extrn: {}
            )
          Donde cada elemento del diccionario es un diccionario con los nombres de los experimentos como llaves.
        :rtype: dict

        """

        raise NotImplementedError

    def simul_calib(símismo, datos_inic, paso, n_pasos, extrn):

        """
        Esta es la función que se calibrará cuando se calibra el modelo. Debe devolver las predicciones del modelo
          correspondiendo a los valores observados, y eso en el mismo orden.

        :param datos_inic:
        :type datos_inic: dict

        ...

        :return: Matriz unidimensional Numpy de las predicciones del modelo correspondiendo a los valores observados.
        :rtype: np.ndarray

        """

        símismo.predics_exps = datos_inic.deepcopy()

        for exp in datos_inic:
            símismo.predics = símismo.predics_exps[exp]
            símismo.calc_simul(paso=paso, n_pasos=n_pasos[exp], extrn=extrn[exp])

        lista_predics = símismo.procesar_predics_calib()

        return lista_predics

    def procesar_predics_calib(símismo):
        """
        Procesa las predicciones del modelo y genera una matriz numpy unidimensional de las predicciones.
        :return:
        :rtype: np.ndarray
        """

        raise NotImplementedError

    def avanzar_calib(símismo, rep=10000, quema=100, extraer=10):

        if símismo.modelo is None:
            raise ValueError

        símismo.modelo.calib(rep=rep, quema=quema, extraer=extraer)


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

        # Llenar coeficientes


        # inic_datos

        for exp in experimentos:
            símismo.predics =
            símismo.calc_simul(paso=paso, n_pasos=, extrn=)


        # Procesar datos validación


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
            símismo.simul_experimento(exper=,
                                      paso=paso, tiempo_final=tiempo_final,
                                      rep_parám=rep_parám, rep_estoc=rep_estoc,
                                      extrn=extrn, mov=mov,
                                      calibs=calibs
                                      )
            vals_inic =
            tiempo_final =
            extrn =
            mov =

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
