import os
import io
import warnings
import copy as copiar
import json
from datetime import datetime as ft
import matplotlib.pyplot as dib
import numpy as np
import pymc

from INCERT.NuevaCALIB import ModBayes
from INCERT.DATOS import Experimento
from INCERT import Distribuciones as Ds


class Coso(object):
    """
    Un "coso", por falta de mejor palabra, se refiere a todo, TODO en el programa
    Tikon que representa un aspecto físico del ambiente y que tiene datos. Incluye
    paisajes, parcelas, variedades de cultivos, suelos, insectos, etc. Todos tienen la misma
    lógica para leer y escribir sus datos en carpetas externas, tanto como para la
    su calibración.
    """

    # La extensión para guardar recetas de este tipo de objeto
    ext = NotImplemented

    def __init__(símismo, nombre, fuente=None):
        """
        Creamos un Coso con un numbre y, posiblemente, una fuente de cual cargarlo.

        :param nombre: El nombre del Coso
        :type nombre: str

        :param fuente: El archivo de cual cargar el Coso
        :type fuente: str
        """

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
        Esta función guarda el Coso para uso futuro.

        :param archivo: Donde hay que guardar el Coso
        :type archivo: str
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

        :param fuente: Dónde se ubica el archivo.
        :type fuente: str

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
            # Copiar el documento a la receta de este Coso
            símismo.receta.clear()
            llenar_dic(símismo.receta, nuevo_dic)

            # Convertir listas a matrices numpy en las ecuaciones (coeficientes)
            dic_lista_a_np(símismo.receta['coefs'])


class Simulable(Coso):
    """
    Una subclase de Coso para objetos que se pueden simular y calibrar. (Por ejemplo, una Red AgroEcológica o una
      Parcela, pero NO un Insecto.
    """

    def __init__(símismo, nombre, fuente=None):
        """
        Un simulable se inicia como Coso.

        :param nombre: El nombre del simulable
        :type nombre: str

        :param fuente: Un archivo de cual cargar el Simulable
        :type fuente: str
        """

        # Primero, llamamos la función de inicio de la clase pariente 'Coso'
        super().__init__(nombre=nombre, fuente=fuente)

        # Añadir Calibraciones a la receta del Simulable. Este únicamente guarda la información sobre cada calibración.
        #   (Los resultados de las calibraciones se guardan en "coefs".
        if 'Calibraciones' not in símismo.receta:
            símismo.receta['Calibraciones'] = {'0': 'A prioris no informativos generados automáticamente por TIKON.'}

        # Para guardar los objetos relacionados con este Simulable. Sirve para encontrar todos los objetos que hay que
        #  mirar para una simulación o calibración.
        símismo.objetos = []

        # Indica si el Simulable está listo para una simulación.
        símismo.listo = False

        # Contendrá el objeto de modelo Bayesiano para la calibración
        símismo.ModBayes = None

        # Experimentos asociados
        símismo.exps = {}

        # Predicciones del modelo correspondiendo a los Experimentos asociados (para calibración y validación)
        símismo.predics_exps = {}

        # Predicciones de datos (para simulaciones normales)
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
        """
        Esta función corre una simulación del Simulable.

        :param vals_inic: Los valores iniciales para la simulación.
        :type vals_inic: dict

        :param paso: El paso de tiempo para la simulación
        :type paso: int

        :param tiempo_final: El tiempo final para la simulación.
        :type tiempo_final: int

        :param rep_parám: El número de repeticiones paramétricas para incluir en la simulación.
        :type rep_parám: int

        :param rep_estoc: El número de repeticiones estocásticas para incluir en la simulación
        :type rep_estoc: int

        :param extrn: Un diccionario externo de valores para usar en la simulación, si necesario. (Por ejemplo,
          aplicaciones de pesticidas para la simulación de una Red.)
        :type extrn: dict

        :param calibs: El nombre de la calibración que utilizar, o una lista de calibraciones para utilizar.
        :type calibs: list | str
        """

        # Actualizar el objeto, si necesario. Si ya se ha actualizado el objeto una vez, no se actualizará
        # automáticamente aquí (y no tendrá en cuenta cambios al objeto desde la última calibración).
        if not símismo.listo:
            símismo.actualizar()

        # Unos números útiles
        n_parcelas = valid_vals_inic(vals_inic)
        n_pasos = tiempo_final // paso

        # Preparar la lista de parámetros de interés
        lista_paráms, _  = símismo.gen_lista_coefs_interés_todo()
        calibs = filtrar_calibs(calibs=calibs, lista_paráms=lista_paráms)

        # Llenar las matrices internas de coeficientes
        símismo.llenar_coefs(n_rep_parám=rep_parám, calibs=calibs)

        # Preparar las matrices internas para guardar las predicciones
        símismo.prep_predics(n_pasos=n_pasos, rep_parám=rep_parám, rep_estoc=rep_estoc, n_parcelas=n_parcelas)

        # Simular el modelo
        símismo.calc_simul(paso=paso, n_pasos=n_pasos, extrn=extrn)

    def llenar_coefs(símismo, n_rep_parám, calibs):
        """
        Transforma los diccionarios de coeficientes a matrices internas (para aumentar la rapidez de la simulación).
          Las matrices internas, por supuesto, dependerán del tipo de Simulable en cuestión. No obstante, todas
          tienen la forma siguiente: eje 0 = parcela, eje 1 = repetición estocástica, eje 2 = repetición paramétrica,
          eje 3+ : dimensiones opcionales.

        :param n_rep_parám: El número de repeticiones paramétricas que incluir.
        :type n_rep_parám: int

        :param calibs: Una lista de los nombres de las calibraciones, o el nomre de una calibración, que hay que
          incluir.
        :type calibs: list | str

        """

        raise NotImplementedError

    def prep_predics(símismo, n_pasos, rep_parám, rep_estoc, n_parcelas):
        """
        Esta función prepara el diccionario de predicciones para guardar los resultados de una simulación.
          Se tiene que implementar para cada tipo de Simulable. Modifica símismo.predics, así que no devuelve
          ningún valor.

        :param n_pasos: El número de pasos de la simulación que vamos a hacer.
        :type n_pasos: int

        :param rep_parám: El número de repeticiones paramétricas.
        :type rep_parám: int

        :param rep_estoc: El número de repeticiones estocásticas.
        :type rep_estoc: int

        :param n_parcelas: El número de parcelas en la simulación.
        :type n_parcelas: int

        """

        raise NotImplementedError

    def calc_simul(símismo, paso, n_pasos, extrn=None):
        """
        Esta función aumenta el modelo para cada paso en la simulación. Se usa en simulaciones normales, tanto como en
          simulaciones de experimentos.

        :param paso: El paso para la simulación
        :type paso: int

        :param n_pasos: El número de pasos en la simulación.
        :type n_pasos: int

        :param extrn: Un diccionario externo, si necesario, con información para la simulación.
        :type extrn: dict

        """

        # Para cada paso de tiempo, incrementar el modelo
        for i in range(0, n_pasos):
            símismo.incrementar(paso, i=i + 1, extrn=extrn)

    def incrementar(símismo, paso, i, extrn):
        """
        Esta función incrementa el modelo por un paso. Se tiene que implementar en cada subclase de Simulable.
        
        :param paso: El paso con cual incrementar el modelo
        :type paso: int

        :param i: El número de este incremento en la simulación
        :type i: int

        :param extrn: Un diccionario de valores externos al modelo, si necesario
        :type extrn: dict

        """

        # Dejamos la implementación del incremento del modelo a las subclases individuales.
        raise NotImplementedError

    def calibrar(símismo, nombre=None, aprioris=None, exper=None, paso=1,
                 n_iter=10000, quema=100, extraer=10):
        """
        Esta función calibra un Simulable. Para calibrar un modelo, hay algunas cosas que hacer:
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

        :param nombre: El nombre de la calibración.
        :type nombre: str

        :param aprioris: Las calibraciones anteriores que hay que utilizar para los a prioris.
        :type aprioris: int | str | list | None

        :param exper: Los experimentos vinculados al objeto a usar para la calibración. exper=None lleva al uso de
          todos los experimentos disponibles.
        :type exper: list | str | Experimento | None

        :param paso: El paso para la calibración
        :type paso: int

        :param n_iter: El número de iteraciones para la calibración.
        :type n_iter: int

        :param quema: El número de iteraciones iniciales que hay que botar. (Para evitar el efecto de condiciones
          iniciales en la calibración).
        :type quema: int

        :param extraer: Cada cuantas iteraciones guardar (para limitar el efecto de autocorrelación entre iteraciones).
          extraer = 1 lleva al uso de todas las iteraciones.
        :type extraer: int

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

        # 2. Creamos la lista de parámetros que hay que calibrar
        lista_paráms, lista_líms = símismo.gen_lista_coefs_interés_todo()

        # 3. Filtrar coeficientes por calib
        lista_aprioris = filtrar_calibs(calibs=aprioris, lista_paráms=lista_paráms)

        # 4. Preparar el diccionario de argumentos para la función "simul_calib", según los experimentos escogidos
        # para la calibración.

        exper = símismo.prep_lista_exper(exper=exper)

        dic_argums = símismo.prep_args_simul_exps(exper=exper, n_rep_paráms=1, n_rep_estoc=1)
        dic_argums[paso] = paso  # Guardar el paso en el diccionario también

        # 5. Generar el vector numpy de observaciones para los experimentos
        obs = símismo.prep_obs_exper(exper=exper)

        # 6. Creamos el modelo ModBayes de calibración, lo cual genera variables PyMC
        símismo.ModBayes = ModBayes(función=símismo.simul_exps,
                                    dic_argums=dic_argums,
                                    obs=obs,
                                    lista_paráms=lista_paráms,
                                    lista_apriori=lista_aprioris,
                                    lista_líms=lista_líms,
                                    id_calib=nombre
                                    )

        # 7. Llenamos las matrices de coeficientes con los variables PyMC recién creados
        símismo.llenar_coefs(n_rep_parám=1, calibs=nombre)

        # 8. Calibrar el modelo, llamando las ecuaciones bayesianas a través del objeto ModBayes
        símismo.ModBayes.calib(rep=n_iter, quema=quema, extraer=extraer)

    def validar(símismo, exper, calibs=None, paso=1, n_rep_parám=100, n_rep_estoc=100, dibujar=True):
        """
        Esta función valida el modelo con datos de observaciones de experimentos.

        :param exper: Los experimentos vinculados al objeto a usar para la calibración. exper=None lleva al uso de
          todos los experimentos disponibles.
        :type exper: list | str | Experimento | None

        :param calibs: Las calibraciones que hay que usar para la validación.
        :type calibs: list | str | None

        :param paso: El paso para la validación
        :type paso: int

        :param n_rep_parám: El número de repeticiones de parámetros.
        :type n_rep_parám: int

        :param n_rep_estoc: El número de repeticiones estocásticas.
        :type n_rep_estoc: int

        :param dibujar: Si hay que generar gráficos de los resultados.
        :type dibujar: bool

        :return: Un diccionario con los resultados de la validación.
        :rtype: dict
        """

        # Encontrar los parámetros de interés
        lista_paráms = símismo.gen_lista_coefs_interés_todo()[0]

        # Si no se especificaron calibraciones para validar, tomamos la calibración activa, si hay, y en el caso
        # contrario tomamos el conjunto de todas las calibraciones anteriores.
        if calibs is None:
            if símismo.ModBayes is None:
                calibs = 'Todos'
            else:
                calibs = símismo.ModBayes.id

        lista_calibs = filtrar_calibs(calibs=calibs, lista_paráms=lista_paráms)

        # Llenar coeficientes
        símismo.llenar_coefs(n_rep_parám=n_rep_parám, calibs=lista_calibs)

        exper = símismo.prep_lista_exper(exper=exper)

        # Generar el vector numpy de observaciones para los experimentos
        obs = símismo.prep_obs_exper(exper=exper)

        # Simular los experimentos
        dic_argums = símismo.prep_args_simul_exps(exper=exper, n_rep_estoc=n_rep_estoc, n_rep_paráms=n_rep_parám)
        preds = símismo.simul_exps(**dic_argums, paso=paso)

        # Si hay que dibujar, dibujar
        if dibujar:
            símismo.dibujar()

        # Procesar los datos de la validación
        return símismo.procesar_validación(vector_obs=obs, vector_preds=preds)

    def gen_lista_coefs_interés_todo(símismo):

        """
        Esta función devuelve una lista de todos los coeficientes de un Simulable y de sus objetos de manera
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
        Prepara un vector numpy de las obsevaciones de los experimentos.

        :param exper: Una lista de los nombres de los experimentos que vamos a incluir para esta calibración.
        :type exper: list

        :return: Un vector, en orden reproducible, de las observaciones de los experimentos.
        :rtype: np.ndarray
        """

        raise NotImplementedError

    def prep_args_simul_exps(símismo, exper, n_rep_paráms, n_rep_estoc):
        """
        Prepara un diccionaro de los argumentos para simul_exps. El diccionario debe de tener la forma elaborada
          abajo. Se implementa para cada subclase de Simulable.

        :param exper: Una lista de los nombres de los experimentos para incluir
        :type exper: list

        :param n_rep_paráms: El número de repeticiones paramétricas para las simulaciones.
        :type n_rep_paráms: int

        :param n_rep_estoc: El número de repeticiones estocásticas para las simulaciones.
        :type n_rep_estoc: int

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

    def simul_exps(símismo, datos_inic, paso, n_pasos, extrn):
        """
        Esta es la función que se calibrará cuando se calibra o valida el modelo. Devuelve las predicciones del modelo
          correspondiendo a los valores observados, y eso en el mismo orden.
        Todos los argumentos de esta función, a parte "paso," son diccionarios con el nombre de los experimentos para
          simular como llaves.

        :param datos_inic: Un diccionario de los datos iniciales para la simulación de cada experimento.
        :type datos_inic: dict

        :param paso: El paso para la simulación
        :type paso: int

        :param n_pasos: Un diccionario con el número de pasos para cada simulación
        :type n_pasos: dict

        :param extrn: Un diccionario de valores externas a pasar a la simulación, si aplica.
        :type extrn: dict

        :return: Matriz unidimensional Numpy de las predicciones del modelo correspondiendo a los valores observados.
        :rtype: np.ndarray

        """

        # Hacer una copia de los datos iniciales (así que, en la calibración del modelo, una iteración no borará los
        # datos iniciales para las próximas).
        símismo.predics_exps = copiar.deepcopy(datos_inic)

        # Para cada experimento...
        for exp in datos_inic:
            # Apuntar el diccionario de predicciones del Simulable al diccionario apropiado en símismo.predics_exps.
            símismo.predics = símismo.predics_exps[exp]

            # Simular el modelo
            símismo.calc_simul(paso=paso, n_pasos=n_pasos[exp], extrn=extrn[exp])

        # Convertir los diccionarios de predicciones en un vector numpy.
        vector_predics = símismo.procesar_predics_calib()

        # Devolver el vector de predicciones.
        return vector_predics

    def procesar_predics_calib(símismo):
        """
        Procesa las predicciones de simulación de experimentos (predics_exps) del modelo y genera una matriz numpy
          unidimensional de las predicciones. Se debe implementar para cada subclase de Simulable.

        :return: Un vector numpy de las predicciones del modelo.
        :rtype: np.ndarray
        """

        raise NotImplementedError

    def avanzar_calib(símismo, rep=10000, quema=100, extraer=10):
        """
        Añade a una calibración ya empezada.

        :param rep: El número de iteraciones extras.
        :type rep: int

        :param quema: El número de iteraciones iniciales que hay que botar.
        :type quema: int

        :param extraer: Cada cuántas iteraciones guardar.
        :type extraer: int

        """

        # Si ya no existe un modelo de calibración, no podemos avanzarla.
        if símismo.ModBayes is None:
            raise TypeError('Hay que iniciar una calibración antes de avanzarla.')

        # Avanzar la calibración.
        símismo.ModBayes.calib(rep=rep, quema=quema, extraer=extraer)

    def guardar_calib(símismo, descrip, utilizador, contacto):
        """
        Esta función guarda una calibración existente para uso futuro.

        :param descrip: La descripción de la calibración (para referencia futura).
        :type descrip: str

        :param utilizador: El nombre del utilizador que hizo la calibración.
        :type utilizador: str

        :param contacto: El contacto del utilizador
        :type contacto: str

        """

        # Si no hay modelo, no hay nada para guardar.
        if símismo.ModBayes is None:
            raise ValueError('No hay calibraciones para guardar')

        # La fecha y hora a la cual se guardó
        ahora = ft.now().strftime('%Y-%m-%d %H:%M:%S')

        # El nombre de identificación de la calibración.
        nb = símismo.ModBayes.id

        # Guardar la descripción de esta calibración en el diccionario del objeto
        símismo.receta['Calibraciones'][nb] = dict(Descripción=descrip,
                                                   Fecha=ahora,
                                                   Utilizador=utilizador,
                                                   Contacto=contacto,
                                                   Config=símismo.receta['estr'].deepcopy())

        # Guardar los resultados de la calibración
        símismo.ModBayes.guardar()

        # Borrar el objeto de modelo, ya que no se necesita
        símismo.ModBayes = None

    def añadir_exp(símismo, experimentos):
        """
        Esta función añade un experimento al Simulable.

        :param experimentos: El experimento (o lista de experimentos) para añadir
        :type experimentos: list

        """

        if type(experimentos) is not list:
            experimentos = [experimentos]

        for exp in experimentos:
            símismo.exps[exp.nombre] = exp

    def procesar_validación(símismo, vector_obs, vector_preds):
        """
        Esta función procesa los resultados de la validación del modelo. Se tiene que implementar para cada subclase
          de Simulable.

        :param vector_obs: El vector de observaciones.
        :type vector_obs: np.ndarray

        :param vector_preds: El vector de predicciones.
        :type vector_preds: np.ndarray

        :return: Un diccionario del análisis de la validación.
        :rtype: dict
        """

        raise NotImplementedError

    def prep_lista_exper(símismo, exper):
        """
        Esta lista prepara la lista de nombres de los experimentos para validación o calibración.

        :param exper: Los experimentos a usar.
        :type exper: list | str | Experimento | None

        :return: Una lista de los nombres de los experimentos.
        :rtype: list
        """

        # Si "experimentos" no se especificó, usar todos los experimentos vinculados con el Simulable
        if exper is None:
            exper = list(símismo.exps)

        # Si exper no era una lista, hacer una.
        if not type(exper) is list:
            exper = [exper]

        # Para cada elemento de exper, poner únicamente el nombre.
        for n, exp in enumerate(exper):
            if type(exp) is Experimento:
                exper[n] = exp.nombre

        # Devolver exper
        return exper

    def dibujar(símismo, mostrar=True, archivo=''):
        """
        Una función para generar gráficos de los resultados del objeto.
        """

        raise NotImplementedError


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


def dic_lista_a_np(d):
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
            dic_lista_a_np(v)  # Llamar esta función de nuevo
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
            prep_json(v)  # ...llamar esta función de nuevo con el nuevo diccionario

        elif type(v) is np.ndarray:  # Si el itema era una matriz numpy...
            d[ll] = v.tolist()  # ...convertir la matriz al formato de lista.

        elif isinstance(v, pymc.Stochastic):  # Si el itema es un variable de PyMC...
            d.pop(ll)  # ... borrarlo


def valid_vals_inic(d, n=None):
    """

    :param d:
    :type d: dict
    :param n:
    :type n:
    :return:
    :rtype:
    """

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


def filtrar_calibs(calibs, lista_paráms):
    if type(calibs) is int:
        calibs = [str(calibs)]
    elif type(calibs) is str:
        calibs = [calibs]
        # para hacer

    lista_aprioris =

    return lista_aprioris


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


def gráfico(matr_predic, vector_obs, nombre, etiq_y=None, etiq_x='Día', color=None, mostrar=True, archivo=''):
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

    if etiq_y is None:
        etiq_y = nombre

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
