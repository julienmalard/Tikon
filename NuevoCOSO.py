import os
import io
import json

from INCERT.NuevaCALIB import Experimento, ModBayes
import numpy as np


class Coso(object):

    # La extensión para guardar recetas de este tipo de objeto
    ext = NotImplemented

    def __init__(símismo, nombre, fuente=None):

        # En 'coefs', ponemos todos los coeficientes del modelo (se pueden organizar en diccionarios). En 'estr',
        # pondremos la información estructural del modelo.

        símismo.receta = dict(coefs={},
                              estr={}
                              )

        # Dónde vamos a guardar este objeto
        símismo.fuente = fuente
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
        np_a_lista(símismo.receta['Coefs'])  # Convertir matrices a formato de lista

        with io.open(archivo, 'w', encoding='utf8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)  # Guardar todo

    def cargar(símismo, fuente):
        """
        Esta función carga un archivo de receta para crear el Coso. NO usar esta función directamente; se debe
          llamar únicamente por la función __init__(). Si quieres cargar un objeto existente de otra fuente,
          crear un nuevo objeto con la nueva fuente.

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
            llenar_dic(símismo.receta, nuevo_dic)

            # Convertir listas a matrices numpy en las ecuaciones (coeficientes)
            lista_a_np(símismo.receta['Coefs'])


class Simulable(Coso):
    """
    Una subclase de Coso para objetos que se pueden simular y calibrar. (Por ejemplo, una Red AgroEcológica, pero NO
      un Insecto.
    """

    def __init__(símismo, nombre, fuente=None):

        # Primero, llamamos la función de inicio de la clase pariente 'Coso'
        super().__init__(nombre=nombre, fuente=fuente)

        # Una indicación de que el objeto Simulable no está listo todavía para su simulación
        símismo.listo = False

        símismo.modelo = None

        símismo.observ = {}

    def actualizar(símismo):
        raise NotImplementedError

    def simular(símismo, tiempo_final, paso, extrn):

        # Si necesario, actualizar el objeto
        if not símismo.listo:
            símismo.actualizar()

        # Para cada paso de tiempo, incrementar el modelo
        for i in range(0, tiempo_final // paso):
            símismo.incrementar(paso, i=i + 1, extrn=extrn)

    def incrementar(símismo, paso, i, extrn=None):
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

    def simul_calib(símismo):
        raise NotImplementedError

    def calibrar(símismo):

        # símismo.modelo = ModBayes(función=símismo.simul_calib, obs=, dic_parám=, lista_apriori=, dic_líms=)
        pass

    def añadir_exp(símismo, experimento, corresp, categ):

        """

        :param experimento:
        :type experimento: Experimento

        :param corresp:
        :type corresp: dict

        """
        dic_datos = símismo.observ[experimento.nombre] = corresp.copy()

        llenar_obs(d=dic_datos, exp=experimento, categ=categ)

    def validar(símismo, experimento):
        pass


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
    Esta función llena un diccionario con los valores de otro diccionario. Es util para situaciones dónde hay que
      asegurarse de que el formato de un diccionario que estamos cargando esté correcto.

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
    Esta función toma las matrices numpy contenidas en un diccionario de estructura arbitraria y las convierte
      en listas numéricas. Cambia el diccionario in situ, así que no devuelve ningún valor.
      Una nota importante: esta función puede tomar diccionarios de estructura arbitraria, pero no convertirá
      exitosamente diccionarios que contienen listas que a su turno contienen otras listas para convertir a matrices
      numpy. No hay problema con listas compuestas representando matrices multidimensionales.

    :param d: El diccionario a convertir
    :type d: dict

    """

    for ll, v in d.items():  # Para cada itema (llave, valor) del diccionario
        if type(v) is dict:  # Si el itema era otro diccionario...
            np_a_lista(v)  # Llamar esta función de nuevo
        elif type(v) is list:  # Si el itema era una lista...
            try:
                d[ll] = np.array(v, dtype=float)  # Ver si se puede convertir a una matriz numpy
            except ValueError:
                pass  # Si no funcionó, pasar al siguiente


def np_a_lista(d):
    """
    Esta función toma las listas numéricas contenidas en un diccionario de estructura arbitraria y las convierte
      en matrices de numpy. Cambia el diccionario in situ, así que no devuelve ningún valor.
      Una nota importante: esta función puede tomar diccionarios de estructura arbitraria, pero no convertirá
      exitosamente diccionarios que contienen listas.

    :param d: El diccionario para convertir
    :type d: dict

    """

    for ll, v in d.items():  # Para cada itema (llave, valor) del diccionario
        if type(v) is dict:  # Si el itema era otro diccionario...
            lista_a_np(v)  # Llamar esta función de nuevo con el nuevo diccionario
        elif type(v) is np.ndarray:  # Si el itema era una matriz numpy...
            d[ll] = v.tolist()  # Convertir la matriz al formato de lista.
