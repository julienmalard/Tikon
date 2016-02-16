import io
import json
import numpy as np


class Red(object):
    def __init__(símismo, archivo = ''):
        símismo.receta = dict(Organismos={})  # La información necesaria para recrear la red
        símismo.archivo = archivo  # El archivo en que podemos guardar esta red
        símismo.pobs = None  # Contendrá la matriz de datos de poblaciones durante las simulaciones

        if archivo != '':  # Si se especificó un archivo, cargarlo
            símismo.cargar(archivo)

    def añadir_insecto(símismo):
        pass

    def quitar_insecto(símiso):
        pass

    def simular(símismo, paso, tiempo_final):
        n_parcelas =
        n_especies =
        # Crear una matriz para guardar los resultados.
        # Eje 0 es el día de simulacion, eje 1 la especie y eje 2 las distintas parcelas
        símismo.pobs = np.empty(shape=(tiempo_final, n_especies, n_parcelas))
        for i in range(0, tiempo_final, paso):
            símismo.incrementar(inic, paso, i+1)

    def incrementar(símismo, inic, paso, i):
        # Calcular la depredación, muerters, reproducción, y movimiento entre parcelas
        depred = símismo.calc_depred(inic, paso)
        muertes = símismo.calc_muertes(inic, paso)
        reprod = símismo.calc_repr(inic, paso)
        mov = símismo.calc_mov(inic, paso)

        # Actualizar la matriz de poblaciones según estos cambios
        símismo.pobs[i] = np.sum((símismo.pobs[i-1], depred, muertes, reprod, mov), axis=0)

    def calc_depred(símismo, inic, paso):
        pass

    def calc_muertes(símismo, inic, paso):
        pass

    def calc_repr(símismo, inic, paso):
        """
        Calcula las reproducciones y las transiciones de etapas de crecimiento
        :type paso: int
        :type inic: np.ndarray
        :param inic:
        :param paso:
        :return: matriz numpy de reproducción (insectos/tiempo). Eje 0 = especie, eje 1 = parcela
        """
        reprod = np.empty(shape=inic.shape)

        dic = símismo.receta['Organismos']
        for n, etapa in enumerate(sorted(dic.items())):
            if dic[etapa][''] == 'exponencial':
                reprod[n] = inic[n] * (r * paso)
            elif dic[etapa][''] == 'logístico':
                pass
            else:
                raise ValueError

        return reprod


    def calc_mov(símismo, inic, paso):
        """
        Calcula la imigración i emigración de organismos entre parcelas
        :type inic: np.narray
        :param inic:
        :type paso: int
        :param paso:
        :return:
        """



    def guardar(símismo, archivo=''):
        """
        Esta función guardar la red para uso futuro
        :param archivo:
        :return:
        """

        # Si no se especificó archivo...
        if archivo == '':
            if símismo.archivo != '':
                archivo = símismo.archivo  # utilizar el archivo existente
            else:
                # Si no hay archivo existente, tenemos un problema.
                raise FileNotFoundError('Hay que especificar un archivo para guardar la red.')

        # Guardar el documento de manera que preserve carácteres no latinos (UTF-8)
        with io.open(archivo, 'w', encoding='utf8') as d:
            json.dump(símismo.receta, d, ensure_ascii=False, sort_keys=True, indent=2)

    def cargar(símismo, archivo):
        """
        Esta función carga un documento de red ya guardado
        :param archivo:
        :return:
        """

        try:  # Intentar cargar el archivo
            with open(archivo, 'r', encoding='utf8') as d:
                símismo.receta = json.load(d)
            símismo.archivo = archivo  # Guardar la ubicación del archivo activo de la red

        except IOError as e:
            raise IOError(e)
