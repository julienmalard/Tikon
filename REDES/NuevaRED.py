import io
import json
import math as mat
import numpy as np

import REDES.Ecuaciones as Ec
import INCERT.Distribuciones as Ds
from INCERT.NuevaCALIB import ModBayes
from REDES.ORGANISMO import Organismo


class Red(object):
    def __init__(símismo, fuente=None):

        símismo.receta = dict(Organismos={})  # La información necesaria para recrear la red

        símismo.fuente = fuente  # El archivo en que podemos guardar esta red
        símismo.organismos = {}  # Para los objetos de los organismos en la red
        símismo.etapas = []  # Una lista de las etapas de los organismos en la red

        # Diccionario que contendrá matrizes de los coeficientes de la red
        símismo.coefs_act = {}

        # Para guardar los tipos de ecuaciones de los organismos en la red
        símismo.ecs = {}

        # La matriz de datos de las simulaciones (incluso los datos de poblaciones)
        símismo.datos = {'Pobs': None, 'Transiciones': None, 'Depredación': np.array()}

        # Si se especificó un archivo, cargarlo.
        if fuente is not None:
            símismo.cargar(fuente)

        # Actualizar el organismo
        símismo.actualizar()

    def añadir_organismo(símismo, organismo):
        """

        :param organismo:
        :type organismo: Organismo or str
        """

        if isinstance(organismo, Organismo):  # 'organismo' es un objeto de tipo Organismo...

            # Añadir el organismo a la receta
            símismo.receta['Organismos'][organismo.nombre] = organismo.receta['config']

            # Poner el organismo en la lista activa
            símismo.organismos[organismo.nombre] = organismo

        elif isinstance(organismo, str):  #  ...o 'organismo' es una cadena de carácteres

            obj_org = Organismo(organismo)  # Crear el organismo correspondiente

            # Poner el organismo en la receta
            símismo.receta['Organismos'][organismo] = obj_org.receta['config']

            # Poner el organismo en la lista activa
            símismo.organismos[organismo] = obj_org

        # Actualizar la red
        símismo.actualizar()

    def quitar_organismo(símismo, organismo):
        """

        :param organismo:
        :type organismo: Organismo or str
        :return:
        """

        if isinstance(organismo, Organismo):  # 'organismo' es un objeto de tipo Organismo...
            símismo.receta['Organismos'].pop(organismo.nombre)  # Quitar su nombre a la receta
            símismo.organismos.pop(organismo.nombre)  # Poner el organismo en la lista activa


        elif isinstance(organismo, str):  #  ...o 'organismo' es una cadena de carácteres
            símismo.receta['Organismos'].pop(organismo)  # Poner el nombre en la receta
            símismo.organismos.pop(organismo)  # Crear el organismo correspondiente

        # Actualizar la red
        símismo.actualizar()

    def actualizar(símismo):
        """
        Actualiza la lista de etapas y las matrices de coeficientes de la red.

        :return: Nada
        """

        # Verificar que todos los organismos en la receta, y únicamente los organismos en la receta, estén en la
        # lista de organismos activos de la red.

        for nombre, config in símismo.receta['Organismos'].items():
            if nombre not in símismo.organismos:  # Si el organismo no existía...
                # Crear el organismo...
                símismo.organismos[nombre] = Organismo(nombre)

                # Y aplicar las configuraciones guardadas en la red
                símismo.organismos[nombre].receta['config'] = config

        for org in símismo.organismos:
            if org not in símismo.receta['Organismos']:
                símismo.organismos.pop(org)

        # Guardar las etapas de todos los organismos de la red y sus coeficientes en un orden reproducible

        símismo.etapas.clear()  # Borrar la lista de etapas existentes

        for organismo in [org for (nombre, org) in sorted(símismo.organismos.items())]:
            símismo.etapas += [etp for etp in sorted(organismo.receta.values())]

        # Guardar los tipos de ecuaciones activos de las etapas en un diccionario central
        for categ, dic_categ in Ec.ecuaciones:
            símismo.ecs[categ] = {}
            for subcateg in dic_categ:
                subcateg.ecs[categ][subcateg] = [etp['ecuaciones'][categ][subcateg] for etp in símismo.etapas]

    def llenar_coefs(símismo, n_etps, n_parc, n_rep_parám, n_rep_estoc, calibs):

        # Crear las matrices de coeficientes
        símismo.coefs_act = {}
        for categ, dic_categ in Ec.ecuaciones.items():
            símismo.coefs_act[categ] = {}

            for subcateg in dic_categ:
                lista_parám = símismo.coefs_act[categ][subcateg] = []

                for etp in símismo.etapas:
                    dic_parám = {}
                    opción = etp['ecuaciones'][categ][subcateg]['opción']

                    for parám in Ec.ecuaciones[categ][subcateg][opción]:

                        if parám['inter'] is None:

                            if calibs == 'Todo':
                                calibs_etp = list(etp['ecuaciones'][categ][subcateg]['paráms'][parám].keys())
                            else:
                                calibs_etp = calibs

                            n_calibs = len(calibs_etp)
                            rep_per_calib = np.array([n_rep_parám // n_calibs] * n_calibs)
                            resto = n_rep_parám % n_calibs
                            rep_per_calib[:resto+1] += 1

                            for n_id, id in enumerate(calibs_etp):

                                traza_parám = etp['ecuaciones'][categ][subcateg]['paráms'][parám][id]

                                if type(traza_parám) is np.ndarray:
                                    if rep_per_calib[n_id] > calibs_etp[id]:
                                        raise Warning('Número de replicaciones superior al tamaño de la traza de '
                                                      'parámetro disponible.')

                                    dic_parám[parám] = np.random.choice(calibs_etp[id], size=rep_per_calib[n_id])

                                elif type(traza_parám) is str:
                                    dist_sp = Ds.texto_a_distscipy(traza_parám)
                                    dic_parám[parám] = dist_sp.rvs(rep_per_calib[n_id])

                                else:
                                    raise TypeError


                        elif parám['inter'] == 'presa':
                            dic_parám[parám] = np.zeros(shape=(n_rep_parám, n_etps))

                        else:
                            raise ValueError

                    lista_parám += dic_parám


        # Crear las matrices para guardar resultados:
        símismo.datos['Pobs'] = np.empty(shape=(n_parc, n_rep_estoc, n_rep_parám, n_etps), dtype=int)

        símismo.datos['Depredación'] = np.zeros(shape=(n_parc, n_rep_estoc, n_rep_parám, n_etps, n_etps))

        símismo.datos['Transiciones'] = np.zeros(shape=(n_parc, n_rep_estoc, n_rep_parám, n_etps), dtype=np.int)


        símismo.listo = True



    def simular(símismo, paso=1, tiempo_final=120, rep_parám=100, rep_estoc=1, pobs_inic=None):

        # Determinar el número de parcelas y el número de especies
        n_parcelas = pobs_inic.shape[2]
        n_etps = len(símismo.etapas)


        if not símismo.listo:
            símismo.llenar_coefs(n_etps=n_etps, n_parc=n_parcelas, n_rep_parám=rep_parám, n_rep_estoc=rep_estoc)





        # Crear una matriz para guardar los resultados.
        # Eje 0 es el día de simulacion, eje 1 la especie y eje 2 las distintas parcelas
        símismo.pobs = np.empty(shape=(tiempo_final, n_etps, n_parcelas))

        # para hacer: inicializar las poblaciones a t=0
        for i in range(0, tiempo_final, paso):
            símismo.incrementar(paso, i+1)

    def incrementar(símismo, paso, i):
        pobs_ant = símismo.pobs[i-1]

        # Calcular la depredación, muerters, reproducción, y movimiento entre parcelas
        símismo.calc_depred(pobs=pobs_ant, paso=paso)
        símismo.calc_crec(pobs=pobs_ant, externo=climaYplantas, paso=paso)
        muerte = símismo.calc_muertes()
        trans = símismo.calc_trans()
        mov = símismo.calc_mov(pobs_ant, paso)

        # Actualizar la matriz de poblaciones según estos cambios
        símismo.pobs[i] = np.sum((símismo.pobs[i-1], depred, crec, mov), axis=0)

    def calc_depred(símismo, pobs, paso):
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
                  k = (b * P^2) / (P^2 + c)
                  m = (1/a - 1) * (b / P)


        :param pobs: matriz numpy de poblaciones actuales.
        :param paso:
        """

        # Calcular cuántas presas cada especie de depredador podría comerse

        # A este punto, depred representa la depredación potencial per cápita de depredador
        depred = símismo.datos['Depredación']
        tipos_ec = símismo.ecs['Depredación']['Ecuación']

        # La lista de los coeficientes de cada etapa para la depredación
        coefs = símismo.coefs_act['Depredación']['Ecuación']

        for n in range(len(símismo.etapas)):  # Para cada etapa...

            # Los coeficientes para esta etapa
            cf = coefs[n]
            # Los tipos de ecuaciones para esta etapa
            tipo_ec = tipos_ec[n]

            # Calcular la depredación según la ecuación de esta etapa.
            if tipo_ec is None:
                # Si no hay ecuación para la depredación del organismo (si ni tiene presas), seguir a la próxima etapa
                # de una vez.
                continue

            elif tipo_ec == 'Tipo I_Dependiente presa':
                # Depredación de respuesta funcional tipo I con dependencia en la población de la presa.
                depred_etp = pobs * cf['a']

            elif tipo_ec == 'Tipo II_Dependiente presa':
                # Depredación de respuesta funcional tipo II con dependencia en la población de la presa.
                depred_etp = pobs * cf['a'] / (pobs + cf['b'])

            elif tipo_ec == 'Tipo III_Dependiente presa':
                # Depredación de respuesta funcional tipo III con dependencia en la población de la presa.
                depred_etp = np.square(pobs) * cf['a'] / (np.square(pobs) + cf['b'])

            elif tipo_ec == 'Tipo I_Dependiente ratio':
                # Depredación de respuesta funcional tipo I con dependencia en el ratio de presa a depredador.
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa
                depred_etp = pobs / pob_etp * cf['a']

            elif tipo_ec == 'Tipo II_Dependiente ratio':
                # Depredación de respuesta funcional tipo II con dependencia en el ratio de presa a depredador.
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa
                depred_etp = pobs / pob_etp * cf['a'] / (pobs / pobs[n] + cf['b'])

            elif tipo_ec == 'Tipo III_Dependiente ratio':
                # Depredación de respuesta funcional tipo III con dependencia en el ratio de presa a depredador.
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa
                depred_etp = np.square(pobs / pob_etp) * cf['a'] / \
                            (np.square(pobs / pob_etp) + cf['b'])

            elif tipo_ec == 'Beddington-DeAngelis':
                # Depredación de respuesta funcional Beddington-DeAngelis. Incluye dependencia en el depredador.
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa
                depred_etp = pobs * cf['a'] / (1 + cf['b'] * pobs + cf['c'] * pob_etp)

            elif tipo_ec == 'Tipo I_Hassell-Varley':
                # Depredación de respuesta funcional Tipo I con dependencia Hassell-Varley.
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa
                depred_etp = pobs / pob_etp ** cf['m'] * cf['a']

            elif tipo_ec == 'Tipo II_Hassell-Varley':
                # Depredación de respuesta funcional Tipo II con dependencia Hassell-Varley.
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa
                depred_etp = pobs / pob_etp ** cf['m'] * cf['a'] / \
                            (pobs / pob_etp ** cf['m'] + cf['b'])

            elif tipo_ec == 'Tipo III_Hassell-Varley':
                # Depredación de respuesta funcional Tipo III con dependencia Hassell-Varley.
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa
                depred_etp = pobs / pob_etp ** cf['m'] * cf['a'] / \
                            (pobs / pob_etp ** cf['m'] + cf['b'])

            elif tipo_ec == 'Asíntota Doble':
                # Depredación de respuesta funcional de asíntota doble (ecuación Kovai).
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa

                k = (cf['b'] * pobs ** 2) / (pobs ** 2 + cf['c'])
                m = (1 / cf['a'] * - 1) * (cf['b'] / pobs)

                depred_etp = k / (1 + m * pob_etp)

            else:
                # Si el tipo de ecuación no estaba definida arriba, hay un error.
                raise ValueError

            depred[:, :, :, n, :] = depred_etp

        # Convertir depredación potencial por depredador a depredación potencial total (multiplicar por la población
        # de cada depredador). También multiplicamos por el paso de la simulación. 'depred' ahora esta en unidades
        # del número total de presas comidas por cada tipo de depredador por unidad de tiempo.
        depred *= pobs * paso


        # Abajo, vamos a ajustar por la presencia de varios depredadores

        # Primero, calculemos la fracción de la población de cada presa potencialmente consumida por cada depredador
        # (sin interferencia entre depredadores).
        frac_depred = np.divide(depred.swapaxes(4, 3), pobs)  # De pronto no sea necesario el '.swapaxes()'

        # Utilizar la ecuación de probabilidades conjuntas de estadísticas para calcular la fracción total de la
        # población de la presa que se comerá por los depredadores.
        frac_total_depred = np.add(1, -np.product(np.add(1, -frac_depred), axis=3))

        # La fracción total de cada presa potencialmente consumida por todos sus depredadores. Eso podría ser más que
        # 100% en el caso de depredadores múltiples.
        frac_depred_total_pot = np.sum(frac_depred, axis=3)

        # El factor de ajuste para que la suma de la depredación de cada depredador en la presa sume al total de
        # depredación ya calculado.
        ajuste = frac_total_depred / frac_depred_total_pot

        # AJustar la depredación por el factor de ajuste por interferencia entre depredadores
        depred *= ajuste

        # Redondear (para evitar de comer, por ejemplo, 2 * 10^-5 moscas)
        símismo.redondear(depred)

    def calc_crec(símismo, pobs, externo, paso):
        """
        Calcula las reproducciones y las transiciones de etapas de crecimiento

        :type externo: dict
        :param externo: diccionario de factores externos a la red (plantas, clima, etc.)

        :type paso: int


        :param pobs: matriz numpy de poblaciones actuales.
        :type pobs: np.ndarray

        :param paso:

        """


        crec = símismo.datos['Crecimiento']
        tipos_ec = símismo.ecs['Crecimiento']['Ecuación']
        modifs = símismo.ecs['Crecimiento']['Modif']

        coefs_mod = símismo.coefs_act['Creciiento']['Modif']
        coefs_ec = símismo.coefs_act['Crecimiento']['Ecuación']

        for n in range(len(símismo.etapas)):
            cf = coefs_mod[n]

            # Modificaciones ambientales a la taza de crecimiento intrínsica
            if modifs[n] is None:
                # Si no hay crecimiento para este insecto, seguir a la próxima etapa. Notar que si no quieres
                # modificación ambiental a r, pero sí quieres crecimiento, hay que escoger la modificación ambiental
                # 'Ninguna' y NO 'None'. Esto permetirá crear la variable 'r' que se necesitará después.
                continue

            elif modifs[n] == 'Ninguna':
                # Sin modificación a r.
                r = cf['r']

            elif modifs[n] == 'Log Normal Temperatura':
                # r responde a la temperatura con una ecuación log normal.
                r = cf['r']
                r *= mat.exp(-0.5*(mat.log(externo['temp_máx'] /cf['t']) / cf['p']) ** 2)

            else:
                raise ValueError

            # Calcular el crecimiento de la población

            pob_etp = pobs[:, :, :, n]  # La población de esta etapa
            cf = coefs_ec[n]

            if tipos_ec[n] == 'Exponencial':
                # Crecimiento exponencial

                crec_etp = pob_etp * (r * paso)

            elif tipos_ec[n] == 'Logístico':
                # Crecimiento logístico.

                crec_etp = pob_etp * (1 - pob_etp / cf['K'])  # Ecuación logística sencilla

            elif tipos_ec[n] == 'Logístico Presa':
                # Crecimiento logístico. 'K' es un parámetro repetido para cada presa de la etapa y indica
                # la contribución individual de cada presa a la capacidad de carga de esta etapa (el depredador).

                k = pobs * cf['K']  # Calcular la capacidad de carga
                crec_etp =  pob_etp * (1 - pob_etp / k)  # Ecuación logística sencilla

            else:
                raise ValueError

            crec[:, :, :, n] = crec_etp

        crec *= paso

        símismo.redondear(crec)

    def calc_muertes(símismo, pobs, externo, paso):

        """
        Esta función calcula las muertes de causas naturales de la etapa.

        :param externo:
        :param pobs:
        :param paso:
        """

        muertes = símismo.datos['Muertes']

        ec_edad = símismo.ecs['Muertes']['Edad']
        probs = símismo.ecs['Muertes']['Prob']

        coefs_ed = símismo.coefs_act['Muertes']['Edad']
        coefs_pr = símismo.coefs_act['Muertes']['Prob']

        for n, ec_ed in enumerate(ec_edad):

            # Si no hay cálculos de muertes para esta etapa, sigamos a la próxima etapa de una vez. Esto se detecta
            # por etapas que tienen 'None' como ecuación de probabilidad de muerte.

            if probs[n] is None:
                continue

            # Si hay que guardar cuenta de cohortes, hacerlo aquí
            cf = coefs_ed[n]
            if ec_ed is None:
                pass

            else:

                if ec_ed == 'Días':
                    edad_extra = 1
                elif ec_ed == 'Días Grados':
                    edad_extra = símismo.días_grados(externo['temp_máx'], externo['temp_mín'],
                                                     umbrales=(cf['mín'], cf['máx'])
                                                     )
                else:
                    raise ValueError
            np.ndarray
            # Y ya pasamos a calcular el número de individuos de esta etapa que se murieron en este paso de tiempo
            cf = coefs_pr[n]
            if probs[n] is None:
                pass

            elif probs[n] ==  'Constante':
                # Muertes en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
                # exponencial.

                muerte_etp = pobs * cf['q']

            elif probs[n]  == 'Log Normal Temperatura':
                # Muertes dependientes en la temperatura, calculadas con la ecuación mencionada en:
                #
                # Sunghoon Baek, Youngsoo Son, Yong-Lak Park. 2014. Temperature-dependent development and survival of
                #   Podisus maculiventris (Hemiptera: Pentatomidae): implications for mass rearing and biological
                #   control. Journal of Pest Science 87(2): 331-340.

                sobrevivencia = mat.exp(-0.5*(mat.log(externo['temp_máx']/cf['t']) / cf['p']) ** 2)
                muerte_etp = pobs * sobrevivencia

            elif probs[n] == 'Asimptótico Humedad':

                # M. P. Lepage, G. Bourgeois, J. Brodeur, G. Boivin. 2012. Effect of Soil Temperature and Moisture on
                #   Survival of Eggs and First-Instar Larvae of Delia radicum. Environmental Entomology 41(1): 159-165.

                sobrevivencia = max(0, 1-mat.exp(-cf['a'] * (externo['humedad'] - cf['b'])))
                muerte_etp[n] = pobs * sobrevivencia

            elif probs[n] == 'Sigmoidal Temperatura':

                sobrevivencia = 1/(1 + mat.exp((externo['temp_máx'] - cf['a']) / cf['b']))
                muerte_etp[n] = pobs * sobrevivencia

            else:
                # Aquí tenemos todas las probabilidades de muerte dependientes en distribuciones de cohortes:
                cohortes =
                edades =

                dic_cohorte = símismo.datos['Cohortes'][n]
                try:
                    muerte_etp[n] = símismo.eval_cohorte(pobs=cohortes, edades=edades, cambio=edad_extra,
                                                         tipo_dist=probs[n], paráms_dist=cf)
                except ValueError:
                    raise ValueError('Error en el tipo de distribución de probabilidad para muertes naturales.')

            muertes[:, :, :, n] = muerte_etp

        muertes *= paso
        símismo.redondear(muertes)


    def calc_trans(símismo, pobs_inic, paso):
        """
        Esta función calcula las transiciones de organismos de una etapa a otra. Esto puede incluir la reproducción.

        :param pobs_inic:
        :param paso:
        :return:
        """
        trans = np.zeros(shape=(pobs_inic[0], pobs_inic[1]))

        etapas = símismo.tipos_ecuaciones['Transiciones']['Etapas']
        tipo_edad = símismo.tipos_ecuaciones['Transiciones']['Ecuación']['Edad']
        tipo_prob = símismo.tipos_ecuaciones['Transiciones']['Ecuación']['Prob']

        for n, n_etp in enumerate(etapas):  # Para cada organismo...

            if tipo_edad == 'Briere Temperatura':
                # Mokhtar, Abrul Monim y Salem Saif al Nabhani. 2010. Temperature-dependent development of dubas bug, Ommatissus lybicus (Hemiptera: Tropiduchidae), an endemic
                #   pest of date palm, Phoenix dactylifera. Eur. J. Entomol. 107: 681–685

                edad += a * (temp_prom) * (temp_prom - t_dev_mín) * mat.sqrt(l_letal - temp_prom)


            'Logan Temperatura':

            # Modelling temperature-dependent development and survival of Otiorhynchus sulcatus (Coleoptera: Curculionidae)
            # Youngsoo Son andEdwin E. Lewis
            # Agricultural and Forest Entomology Volume 7, Issue 3, pages 201–209, August 2005

            edad += phi * (mat.exp(rho * temp_prom) - exp(rho * t_dev_mín - (t_letal - temp_prom)/delta))

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

    def poner_val(símismo, ):
        pass

    def calibrar(símismo):
        pass

    def añadir_exp(símismo, experimento):
        pass

    def validar(símismo, experimento):
        pass

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

    def cargar(símismo, fuente):
        """
        Esta función carga un documento de red ya guardado
        :param archivo:
        :return:
        """
        try:  # Intentar cargar el archivo (con formato UTF-8)
            with open(fuente, 'r', encoding='utf8') as d:
                nuevo_dic = json.load(d)

        except IOError as e:  # Si no funcionó, quejarse.
            raise IOError(e)

        else:  # Si se cargó el documento con éxito, usarlo
            pass
            # Copiar el documento a la receta de esta red
            # para hacer: llenar_dic(símismo.receta, nuevo_dic)

    # Funciones auxiliares
    @staticmethod
    def redondear(matriz):

        """
        Esta función redondea una matriz de manera estocástica, según el residuo. Por ejemplo, 8.5 se redondeará como
          8 50% del tiempo y como 9 50% del tiempo. 8.01 se redondaría como 8 99% del tiempo y como 9 sólo 1% del
          tiempo.
        :param matriz: La matriz a redondear
        :type matriz: np.ndarray

        """
        residuos = matriz - np.round(matriz, out=matriz)

        prob = np.random.rand(*matriz.shape)

        matriz += (prob > residuos) * 1

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


    @staticmethod
    def eval_cohorte(pobs, edades, cambio, tipo_dist, paráms_dist):
        """

        :param pobs: Una matriz multidimensional de la distribución de los cohortes de la etapa. Cada valor representa
          el número de individúos en una edad particular (determinada por el valor correspondiente en la matriz edades).
            Eje 0: Cohorte
            Eje 1: Parcela
            Eje 2: Repetición estocástica
            Eje 3: Repetición paramétrica
        :type pobs: np.ndarray

        :param edades: Una matriz multidimensional con las edades de cada cohorte de la etapa. Notar que la edad puede
          ser 'edad' en el sentido tradicional del término, tanto como la 'edad' del organismo medida por otro método
          (por ejemplo, exposición cumulativo a días grados).
          Los ejes son iguales que en 'pobs'.
        :type edades: np.ndarray

        :param cambio: Un número con el cambio a la edad de las poblaciones que hay que aplicar.
          Podría ser 1 día, o una cantidad de días grados.
          Ejes iguales a 'edades'.
        :type cambio: np.ndarray or float

        :param tipo_dist: El tipo de distribución usado para calcular probabilidades de transiciones.
        :type tipo_dist: str

        :param paráms_dist: Los parámetros de la distribución de probabilidad.
        :type paráms_dist: dict

        :return: El número total de individúos que transicionaron.
        :rtype: float
        """

        if tipo_dist == 'Normal':
            paráms = dict(loc=paráms_dist['mu'], scale=paráms_dist['sigma'])
        elif tipo_dist == 'Triang':
            paráms = dict(loc=paráms_dist['a'], scale=paráms_dist['b'], c=paráms_dist['c'])
        elif tipo_dist == 'Cauchy':
            paráms = dict(loc=paráms_dist['u'], scale=paráms_dist['f'])
        elif tipo_dist == 'Gamma':
            paráms = dict(loc=paráms_dist['u'], scale=paráms_dist['f'], a=paráms_dist['a'])
        elif tipo_dist == 'T':
            paráms = dict(loc=paráms_dist['mu'], scale=paráms_dist['sigma'], df=paráms_dist['k'])
        else:
            raise ValueError

        dist = Ds.dists['cont'][tipo_dist]['scipy'](**paráms)

        probs = (dist.cdf(edades + cambio) - dist.cdf(edades)) / (1 - dist.cdf(edades))
        n_cambian = np.random.binomial(pobs, probs)

        pobs -= n_cambian

        return np.sum(pobs, axis=0)
