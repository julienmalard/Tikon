import io
import json
import numpy as np

from REDES.ORGANISMO import Organismo, Etapa


class Red(object):
    def __init__(símismo, archivo = ''):
        símismo.receta = dict(Organismos=[])  # La información necesaria para recrear la red
        símismo.archivo = archivo  # El archivo en que podemos guardar esta red

        símismo.organismos = {}  # Contendrá los objetos de los organismos que existen en la red
        símismo.etapas = []  # Contendrá los objetos de las etapas de los organismos que existen en la red
        # Listas de los tipos de
        símismo.tipos_ecuaciones = {'Crecimiento': [], 'Depredación': [], 'Migración': []}
        # Diccionario que contendrá matrizes de los coeficientes de la red
        símismo.coefs = {'Crecimiento': {}, 'Depredación': {}, 'Migración': {}}
        símismo.pobs = None  # Contendrá la matriz de datos de poblaciones durante las simulaciones

        if archivo != '':  # Si se especificó un archivo, cargarlo
            símismo.cargar(archivo)

    def añadir_organismo(símismo, organismo):

        if isinstance(organismo, Organismo):  # Si le pasaste un objeto de organismo ya existente, usarlo
            símismo.receta['Organismos'].append(organismo.nombre)
            símismo.organismos[organismo.nombre] = organismo
        elif isinstance(organismo, str):  # Si en vez le pasaste el nombre de un organismo, intentar crearlo
            símismo.receta['Organismos'].append(organismo)
            símismo.organismos[organismo] = Organismo(organismo)

        símismo.actualizar()

    def quitar_organismo(símismo, organismo):
        símismo.receta['Organismos'].remove(organismo.nombre)
        símismo.organismos.pop(organismo.nombre)

        símismo.actualizar()

    def actualizar(símismo):
        """
        Actualiza la lista de etapas y las matrices de coeficientes de la red.
        :return: Nada
        """

        símismo.etapas.clear()  # Borrar la lista de etapas existentes

        # Guardar las etapas de todos los organismos de la red y sus coeficientes en un orden reproducible
        for organismo in [org for (nom, org) in sorted(símismo.organismos.items())]:
            símismo.etapas += organismo.etapas

        # Crear las listas de ecuaciones de cada organismo
        símismo.tipos_ecuaciones['Crecimiento'] = [etp.receta['Ecuaciones']['Crecimiento'] for etp in símismo.etapas]
        símismo.tipos_ecuaciones['Depredación'] = [etp.receta['Ecuaciones']['Depredación'] for etp in símismo.etapas]
        símismo.tipos_ecuaciones['Movimiento'] = [etp.receta['Ecuaciones']['Movimiento'] for etp in símismo.etapas]

        # Crear las matrices de coeficientes
        núm_etapas = len(símismo.etapas)
        símismo.coefs['Depredación'] = np.zeros(shape=(núm_etapas, núm_etapas))

    def simular(símismo, paso=1, tiempo_final=120, pobs_inic=None):

        # Determinar el número de parcelas y el número de especies
        n_parcelas = pobs_inic.shape[2]
        n_especies = len(símismo.etapas)

        # Crear una matriz para guardar los resultados.
        # Eje 0 es el día de simulacion, eje 1 la especie y eje 2 las distintas parcelas
        símismo.pobs = np.empty(shape=(tiempo_final, n_especies, n_parcelas))

        # para hacer: inicializar las poblaciones a t=0
        for i in range(0, tiempo_final, paso):
            símismo.incrementar(paso, i+1)

    def incrementar(símismo, paso, i):
        pobs_inic = símismo.pobs[i-1]

        # Calcular la depredación, muerters, reproducción, y movimiento entre parcelas
        reprod = símismo.calc_crec(pobs_inic, paso)
        depred = símismo.calc_depred(pobs_inic, paso)
        mov = símismo.calc_mov(pobs_inic, paso)

        # Actualizar la matriz de poblaciones según estos cambios
        símismo.pobs[i] = np.sum((símismo.pobs[i-1], depred, reprod, mov), axis=0)

    def calc_crec(símismo, pobs_act, paso):
        """
        Calcula las reproducciones y las transiciones de etapas de crecimiento
        :type paso: int
        :type pobs_act: np.ndarray
        :param pobs_act: matriz numpy de poblaciones actuales. Eje 0 = especie, eje 1 = parcela
        :param paso:
        :return: matriz numpy de reproducción (insectos/tiempo). Eje 0 = especie, eje 1 = parcela
        """
        reprod = np.empty(shape=pobs_act.shape)

        ecuaciones_reprod = símismo.tipos_ecuaciones['Reproducción']
        for n, etapa in enumerate(símismo.etapas):
            if ecuaciones_reprod[n] == 'exponencial':
                reprod[n] = pobs_act[n] * (r * paso)
            elif ecuaciones_reprod[n] == 'logístico':
                # coefs_k es una matriz del impacto de cada otro organismo en la capacidad de carga de
                # este organismo (n). Eje 0 = plano, eje 1 = especie
                coefs_k = símismo.coefs['CapacidadDeCarga'][n]
                k = pobs_act * coefs_k


                pass
            else:
                raise ValueError

        return reprod

    def calc_depred(símismo, pobs_inic, paso):
        """
        Calcula la depredación entre los varios organismos de la red. Aquí se implementan todas las ecuaciones
        de depredación posibles; el programa escoje la ecuación apropiada para cada depredador.
        El libro "A primer of Ecology" es una buena referencia a las ecuaciones incluidas aquí, tanto como
        Abrams PA, Ginzburg LR. 2000. The nature of predation: prey dependent, ratio dependent or neither?
            Trends Ecol Evol 15(8):337-341.

        Respuestas funcionales (y = consumo de presa por cápita de depredador, D = población del depredador,
        P = población de la presa; a, b y c son constantes):

            Tipo I:
                y = a*P
                Generalmente no recomendable. Incluido aquí por puro interés científico.

            Tipo II:
                y = a*P / (P + b)

            Tipo III:
                y = a*P^2 / (P^2 + b)

            Dependencia en la presa quiere decir que el modelo está dependiente de la población de la presa únicamente
            (como los ejemplos arriba). Ecuaciones dependientes en el ratio se calculan de manera similar, pero
            reemplazando P con (P/D) en las ecuaciones arriba.

            Beddington-DeAngelis:
                J.R. Beddington. Mutual interference between parasites and its effect on searching efficiency. J.
                    Anim. Ecol., 44 (1975), pp. 331–340
                D.L. DeAngelis, et al. A model for trophic interaction Ecology, 56 (1975), pp. 881–892

                y = a*P / (1 + b*P + c*D)

            Hassell-Varley:
                M.P. Hassell, G.C. Varley. New inductive population model for insect parasites and its bearing on
                    biological control. Nature, 223 (1969), pp. 1133–1136

                P en las respuestas funcionales arriba se reemplaza por P/(D^c)

            Asíntota doble:
                y = k / (1 + m * D), donde
                k = (b * P^2) / (P^2 + c), y
                m = (1/a - 1) * (b / P)


        :param pobs_inic: matriz numpy de poblaciones actuales. Eje 0 = especie, eje 1 = parcela
        :param paso:
        :return:
        """

        # Calcular cuántas presas cada especie de depredador podría comerse
        tipo_ec = símismo.tipos_ecuaciones['Depredación']
        for n, etapa in enumerate(símismo.etapas):  # Para cada depredador potencial...

            potenciales = np.zeros(shape=(pobs_inic[0], pobs_inic[0], pobs_inic[1]))
            if tipo_ec[n] is None:
                # Si no hay ecuación para la depredación del organismo (si ni tiene presas, por ejemplo), seguir
                # al próximo insecto de inmediato
                continue

            elif tipo_ec[n] == 'Tipo I_Dependiente presa':
                # Depredación de respuesta funcional tipo I con dependencia en la población de la presa.
                potenciales[n] = pobs_inic * a
                continue

            elif tipo_ec[n] == 'Tipo II_Dependiente presa':
                potenciales[n] = pobs_inic * a / (pobs_inic + b)
                continue

            elif tipo_ec[n] == 'Tipo III_Dependiente presa':
                potenciales[n] = np.square(pobs_inic) * a / (np.square(pobs_inic) + b)
                continue

            elif tipo_ec[n] == 'Tipo I_Dependiente ratio':
                potenciales[n] = pobs_inic / pobs_inic[n] * a
                continue

            elif tipo_ec[n] == 'Tipo II_Dependiente ratio':
                potenciales[n] = pobs_inic / pobs_inic[n] * a / (pobs_inic / pobs_inic[n] + b)
                continue

            elif tipo_ec[n] == 'Tipo III_Dependiente ratio':
                potenciales[n] = np.square(pobs_inic / pobs_inic[n]) * \
                              a / (np.square(pobs_inic / pobs_inic[n]) + b)
                continue

            elif tipo_ec[n] == 'Tipo III_Dependiente ratio':
                potenciales[n] = np.square(pobs_inic / pobs_inic[n]) * \
                              a / (np.square(pobs_inic / pobs_inic[n]) + b)
                continue

            elif tipo_ec[n] == 'Beddington-DeAngelis':
                potenciales[n] = pobs_inic * a / (1 + b * pobs_inic + c * pobs_inic[n])
                continue

            elif tipo_ec[n] == 'Tipo I_Hassell-Varley':
                potenciales[n] = pobs_inic / pobs_inic[n]^c * a
                continue

            elif tipo_ec[n] == 'Tipo II_Hassell-Varley':
                potenciales[n] = pobs_inic / pobs_inic[n]^c * a / (pobs_inic / pobs_inic[n]^c + b)
                continue

            elif tipo_ec[n] == 'Tipo III_Hassell-Varley':
                potenciales[n] = pobs_inic / pobs_inic[n]^c * a / (pobs_inic / pobs_inic[n]^c + b)
                continue

            elif tipo_ec[n] == 'Asíntota Doble':
                k = (b * pobs_inic^2) / (pobs_inic^2 + c)
                m = (1 / a * - 1) * (b / pobs_inic)

                potenciales[n] =  k / (1 + m * pobs_inic[n])
                continue

            else:
                raise ValueError


        # Calcular las presas disponibles por depredador

        #
        for etapa in símismo.etapas:
            if (ecuación de presa) is None:
                continue
            elif (ecuación de presa) == 'Tipo I_Dependiente presa':

                continue
            elif :

                continue
            else:
                raise ValueError

    def calc_muertes(símismo, pobs_inic, paso):
        pass

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
