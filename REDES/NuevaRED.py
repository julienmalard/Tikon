import io
import json
import math as mat
import numpy as np

from REDES.ORGANISMO import Organismo, Etapa


class Red(object):
    def __init__(símismo, archivo = ''):
        símismo.receta = dict(Organismos=[])  # La información necesaria para recrear la red
        símismo.archivo = archivo  # El archivo en que podemos guardar esta red

        símismo.organismos = {}  # Contendrá los objetos de los organismos que existen en la red
        símismo.etapas = []  # Contendrá los objetos de las etapas de los organismos que existen en la red
        # Listas de los tipos de ecuaciones
        símismo.tipos_ecuaciones = {'Crecimiento': {'Base': [], 'Modif': []},
                                    'Depredación': [],
                                    'Muertes': [],
                                    'Migración': []}
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
        tipos_ec = símismo.tipos_ecuaciones

        for tipo_cálc in símismo.etapas[0].receta['Ecuaciones']:
            etps = [(n, etp.receta['Ecuaciones'][tipo_cálc]) for n, etp in enumerate(símismo.etapas) if
                    etp.receta['Ecuaciones'][tipo_cálc] is not None]
            tipos_ec[tipo_cálc]['Etapas'] = [i[0] for i in etps]
            tipos_ec[tipo_cálc]['Ecuación'] = [i[1] for i in etps]


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

    def calc_crec(símismo, pobs_act, externo, paso):
        """
        Calcula las reproducciones y las transiciones de etapas de crecimiento
        :type externo: dict
        :param externo: diccionario de factores externos a la red (plantas, clima, etc.)
        :type paso: int
        :type pobs_act: np.ndarray
        :param pobs_act: matriz numpy de poblaciones actuales. Eje 0 = especie, eje 1 = parcela
        :param paso:
        :return: matriz numpy de reproducción (insectos/tiempo). Eje 0 = especie, eje 1 = parcela
        """

        crec = np.zeros(shape=pobs_act.shape)
        etapas = símismo.tipos_ecuaciones['Crecimiento']['Etapas']
        tipos_ec = símismo.tipos_ecuaciones['Crecimiento']['Ecuación']['Base']
        modif_ec = símismo.tipos_ecuaciones['Crecimiento']['Ecuación']['Modif']

        for n, n_etp in enumerate(etapas):

            cf = símismo.coefs_act[n_etp]

            r = cf['r']

            # Modificaciones ambientales a la taza de crecimiento intrínsica
            if modif_ec[n] is None:
                # Si no hay modificaciones ambientales, no hacer nada
                pass

            elif modif_ec[n] == 'Log Normal Temperatura':
                r *= mat.exp(-0.5*(mat.log(externo['temp_máx'] /cf['t']) / cf['p']) ** 2)

            else:
                raise ValueError

            # Calcular el crecimiento de la población
            if tipos_ec[n] == 'Exponencial':
                # Crecimiento exponencial

                crec[n] = pobs_act[n] * (r * paso)

            elif tipos_ec[n] == 'Logístico':
                # Crecimiento logístico

                # coefs_k es una matriz del impacto de cada otro organismo en la capacidad de carga de
                # este organismo (n). Eje 0 = vacío, eje 1 = especie
                coefs_k = cf['K'][n]
                k = pobs_act * coefs_k
                crec[n_etp] = pobs_act[n_etp] * (1 - pobs_act[n_etp] / k)

            else:
                raise ValueError

        return crec

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

                P en las respuestas funcionales arriba cambia a P/(D^m)

            Asíntota doble (Kovai):
                y = k / (1 + m * D), donde
                k = (b * P^2) / (P^2 + c), y
                m = (1/a - 1) * (b / P)


        :param pobs_inic: matriz numpy de poblaciones actuales. Eje 0 = especie, eje 1 = parcela
        :param paso:
        :return: depred, una martiz numpy
        """

        # Calcular cuántas presas cada especie de depredador podría comerse

        depred_potencial = np.zeros(shape=(pobs_inic[0], pobs_inic[0], pobs_inic[1]))
        tipos_ec = símismo.tipos_ecuaciones['Depredación']['Ecuación']
        etapas = símismo.tipos_ecuaciones['Depredación']['Etapas']


        for n, n_etp in etapas:  # Para cada depredador...
            cf = símismo.coefs_act[n_etp]

            if tipos_ec[n] is None:
                # Si no hay ecuación para la depredación del organismo (si ni tiene presas, por ejemplo), seguir
                # al próximo insecto de inmediato
                continue

            elif tipos_ec[n] == 'Tipo I_Dependiente presa':
                # Depredación de respuesta funcional tipo I con dependencia en la población de la presa.
                depred_potencial[n_etp] = pobs_inic * cf['a']
                continue

            elif tipos_ec[n] == 'Tipo II_Dependiente presa':
                # Depredación de respuesta funcional tipo II con dependencia en la población de la presa.
                depred_potencial[n_etp] = pobs_inic * cf['a'] / (pobs_inic + cf['b'])
                continue

            elif tipos_ec[n] == 'Tipo III_Dependiente presa':
                # Depredación de respuesta funcional tipo III con dependencia en la población de la presa.
                depred_potencial[n_etp] = np.square(pobs_inic) * cf['a'] / (np.square(pobs_inic) + cf['b'])
                continue

            elif tipos_ec[n] == 'Tipo I_Dependiente ratio':
                # Depredación de respuesta funcional tipo I con dependencia en el ratio de presa a depredador.
                depred_potencial[n_etp] = pobs_inic / pobs_inic[n] * cf['a']
                continue

            elif tipos_ec[n] == 'Tipo II_Dependiente ratio':
                # Depredación de respuesta funcional tipo II con dependencia en el ratio de presa a depredador.
                depred_potencial[n_etp] = pobs_inic / pobs_inic[n] * cf['a'] / (pobs_inic / pobs_inic[n] + cf['b'])
                continue

            elif tipos_ec[n] == 'Tipo III_Dependiente ratio':
                # Depredación de respuesta funcional tipo III con dependencia en el ratio de presa a depredador.
                depred_potencial[n_etp] = np.square(pobs_inic / pobs_inic[n]) * cf['a'] / \
                                          (np.square(pobs_inic / pobs_inic[n]) + cf['b'])
                continue

            elif tipos_ec[n] == 'Beddington-DeAngelis':
                # Depredación de respuesta funcional Beddington-DeAngelis. Incluye dependencia en el depredador.
                depred_potencial[n_etp] = pobs_inic * cf['a'] / (1 + cf['b'] * pobs_inic + cf['c'] * pobs_inic[n])
                continue

            elif tipos_ec[n] == 'Tipo I_Hassell-Varley':
                # Depredación de respuesta funcional Tipo I con dependencia Hassell-Varley.
                depred_potencial[n_etp] = pobs_inic / pobs_inic[n] ** cf['m'] * cf['a']
                continue

            elif tipos_ec[n] == 'Tipo II_Hassell-Varley':
                # Depredación de respuesta funcional Tipo II con dependencia Hassell-Varley.
                depred_potencial[n_etp] = pobs_inic / pobs_inic[n]**cf['m'] * cf['a'] / \
                                      (pobs_inic / pobs_inic[n]**cf['m'] + cf['b'])
                continue

            elif tipos_ec[n] == 'Tipo III_Hassell-Varley':
                # Depredación de respuesta funcional Tipo III con dependencia Hassell-Varley.
                depred_potencial[n_etp] = pobs_inic / pobs_inic[n]**cf['m'] * cf['a'] / \
                                      (pobs_inic / pobs_inic[n]**cf['m'] + cf['b'])
                continue

            elif tipos_ec[n] == 'Asíntota Doble':
                # Depredación de respuesta funcional de asíntota doble (ecuación Kovai).
                k = (cf['b'] * pobs_inic**2) / (pobs_inic**2 + cf['c'])
                m = (1 / cf['a'] * - 1) * (cf['b'] / pobs_inic)

                depred_potencial[n_etp] = k / (1 + m * pobs_inic[n])
                continue

            else:
                # Si el tipo de ecuación no estaba definida arriba, hay un error.
                raise ValueError

        # Convertir depredación por depredador a depredación total (multiplicar por la población de cada depredador)
        depred_potencial *= pobs_inic

        # Ajustar por la presencia de varios depredadores
        depred_total = np.sum(depred_potencial, axis=0)
        poblaciones_totales = np.sum(pobs_inic, axis=0)

        factor_ajuste = depred_total / poblaciones_totales
        depred = depred_potencial * factor_ajuste

        # Redondear (para evitar de comer, por ejemplo, 2 * 10^-5 moscas)
        depred = símismo.redondear(depred)

        return depred

    def calc_muertes(símismo, pobs_inic, paso):

        muertes = np.zeros(shape=(pobs_inic[0], pobs_inic[1]))
        depred_potencial = np.zeros(shape=(pobs_inic[0], pobs_inic[0], pobs_inic[1]))
        tipos_ec = símismo.tipos_ecuaciones['Muertes']['Ecuación']
        etapas = símismo.tipos_ecuaciones['Muertes']['Etapas']

        for n, n_etp in enumerate(etapas):
            if tipos_ec[n] == 'Proporcional':
                # Muertes en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
                # exponencial.

                muertes[n] = pobs_inic * q
                continue

            elif tipos_ec[n] == 'Log Normal Temperatura':
                # Muertes dependientes en la temperatura, calculadas con la ecuación mencionada en:
                #
                # Sunghoon Baek, Youngsoo Son, Yong-Lak Park. 2014. Temperature-dependent development and survival of
                #   Podisus maculiventris (Hemiptera: Pentatomidae): implications for mass rearing and biological
                #   control. Journal of Pest Science 87(2): 331-340.

                sobrevivencia = mat.exp(-0.5*(mat.log(temp_máx/t) / p) ** 2)
                muertes[n] = pobs_inic * sobrevivencia
                continue

            else:
                raise ValueError

    def calc_trans(símismo, pobs_inic, paso):
        trans = np.zeros(shape=(pobs_inic[0], pobs_inic[1]))

        etapas = símismo.tipos_ecuaciones['Transiciones']['Etapas']
        tipo_edad = símismo.tipos_ecuaciones['Transiciones']['Ecuación']['Edad']
        tipo_prob = símismo.tipos_ecuaciones['Transiciones']['Ecuación']['Prob']

        for n, n_etp in enumerate(etapas):  # Para cada organismo...
            if tipo_ec[n] == 'Constante':
                # Transiciones en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
                # exponencial.

                trans[n] = pobs_inic * q
                continue

            elif tipo_ec[n] == 'Normal':
                #
                dist_pob[n] =


                trans[n] = pobs_inic * q
                continue

            elif tipo_ec[n] == 'Linear':
                raise NotImplementedError

            else:
                raise ValueError

        return trans

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

    # Funciones auxiliares
    @staticmethod
    def redondear(matriz):
        redondeado = np.round(matriz)
        residuos = matriz - redondeado

        prob = np.random.rand(*matriz.shape)

        redondeado += (prob > residuos) * 1

        return redondeado

    @staticmethod
    def días_grados(mín, máx, umbrales, método='Triangular', corte='Horizontal'):
        """
        Esta función calcula los días grados basados en vectores de temperaturas mínimas y máximas diarias.
        Información sobre los métodos utilizados aquí se puede encontrar en:
        http://www.ipm.ucdavis.edu/WEATHER/ddconcepts.html

        :type mín: float
        :param mín:
        :type máx: float
        :param máx:
        :type umbrales: tuple
        :param umbrales:
        :param método:
        :param corte:
        :return: número de días grados (número entero)
        """

        if método == 'Triangular':
            # Método triangular único
            sup_arriba = max(12 * (máx - umbrales[1])**2 / (máx - mín), 0) / 24
            sup_centro = max(12 * (umbrales[1] - umbrales[0])**2 / (umbrales[1] - mín), 0) / 24
            sup_lados = max(24 * (máx - umbrales[1]) * (umbrales[1 - umbrales[0]]) / (máx - mín), 0) / 24

        elif método == 'Sinusoidal':
            # Método sinusoidal único
            # NOTA: Probablemente lleno de bogues
            amp = (máx - mín) / 2
            prom = (máx + mín) / 2
            if umbrales[1] >= máx:
                intersect_máx = 0
                sup_arriba = 0
            else:
                intersect_máx = 24 * mat.acos((umbrales[1] - prom) / amp)
                sup_arriba = 2 * (intersect_máx * (prom - máx) + 2*mat.pi/24 * mat.sin(2*mat.pi/24 * intersect_máx))

            if umbrales[0] <= mín:
                intersect_mín = intersect_máx
            else:
                intersect_mín = 24 * mat.acos((umbrales[0] - prom) / amp)

            sup_centro = 2 * intersect_máx * (máx - mín)
            sup_lados = 2 * (2*mat.pi/24 * mat.sin(2*mat.pi/24 * intersect_mín) -
                             2*mat.pi/24 * mat.sin(2*mat.pi/24 * intersect_máx) +
                             (intersect_mín - intersect_máx) * (umbrales[0] - prom)
                             )

        else:
            raise ValueError

        if corte == 'Horizontal':
            días_grados = sup_centro + sup_lados
        elif corte == 'Intermediario':
            días_grados = sup_centro + sup_lados - sup_arriba
        elif corte == 'Vertical':
            días_grados = sup_lados
        elif corte == 'Ninguno':
            días_grados = sup_lados + sup_centro + sup_arriba
        else:
            raise ValueError

        return días_grados
