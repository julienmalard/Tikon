import math as mat
import numpy as np

from NuevoCOSO import Simulable, filtrar_comunes, gen_matr_coefs
from RAE.ORGANISMO import Organismo
import RAE.NuevoINSECTO
import RAE.ENFERMEDADES

import RAE.Ecuaciones as Ec
import INCERT.Distribuciones as Ds


class Red(Simulable):
    """
    Una Red representa una red agroecológica. Trae varios Organismos juntos para interactuar. Aquí se implementan
      los cálculos de todas las ecuaciones controlando las dinámicas de poblaciones de los organismos, tanto como las
      interacciones entre ellos. Una red tiene la propiedad interesante de poder tomar datos iniciales para varias
      parcelas al mismo tiempo y de simular las dinámicas de cada parcela simultáneamente por el uso de matrices.
      Esto permite el empleo de un único objeto de red para modelizar las dinámicas de poblaciones en una cantidad
      ilimitada de parcelas al mismo tiempo. Esto también facilita mucho el cálculo del movimiento de organismos entre
      varias parcelas.
    """

    # La extensión para guardar documentos de recetas de redes agroecológicas.
    ext = '.red'

    def __init__(símismo, nombre, organismos=None, fuente=None):

        """
        :param nombre:
        :param organismos:
        :param fuente:
        """
        super().__init__(nombre=nombre, fuente=fuente)

        # La información necesaria para recrear la red
        símismo.receta['estr'] = dict(Organismos={})

        símismo.organismos = {}  # Para guardar una referencia a los objetos de los organismos en la red
        símismo.etapas = {}  # Un diccionario de las recetas (y más) de las etapas de los organismos en la red

        # Diccionario que contendrá matrices de los coeficientes de la red
        símismo.coefs_act = {}

        # Para guardar los tipos de ecuaciones de los organismos en la red
        símismo.ecs = {'Depredación': {},
                       'Crecimiento': {},
                       'Transiciones': {},
                       'Movimiento': {},
                       'Cohortes': {},
                       'Orden': [],
                       }

        # La matriz de datos de las simulaciones (incluso los datos de poblaciones)
        símismo.datos = {'Pobs': np.array([]),
                         'Depredación': np.array([]),
                         'Crecimiento:': np.array([]),
                         'Transiciones': np.array([]),
                         'Movimiento': np.array([])
                         }

        # Si ya se especificaron organismos en la inicialización, añadirlos a la red.
        if organismos is not None:
            for org in organismos:
                símismo.añadir_org(org)

        # Actualizar el organismo
        símismo.actualizar()

    def añadir_org(símismo, organismo):
        """

        :param organismo:
        :type organismo: Organismo or str
        """

        if isinstance(organismo, Organismo):  # 'organismo' es un objeto de tipo Organismo...

            # Añadir el organismo a la receta
            símismo.receta['estr']['Organismos'][organismo.nombre] = organismo.receta['config']

            # Poner el organismo en la lista activa
            símismo.organismos[organismo.nombre] = organismo

        elif isinstance(organismo, str):  # ...o 'organismo' es una cadena de carácteres

            obj_org = Organismo(organismo)  # Crear el organismo correspondiente

            # Poner el organismo en la receta
            símismo.receta['Organismos'][organismo] = obj_org.receta['config']

            # Poner el organismo en la lista activa
            símismo.organismos[organismo] = obj_org

        # Actualizar la red
        símismo.actualizar()

    def quitar_org(símismo, organismo):
        """

        :param organismo:
        :type organismo: Organismo or str
        :return:
        """

        if isinstance(organismo, Organismo):  # 'organismo' es un objeto de tipo Organismo...
            símismo.receta['Organismos'].pop(organismo.nombre)  # Quitar su nombre a la receta
            símismo.organismos.pop(organismo.nombre)  # Quitar el organismo de los organismos activos

        elif isinstance(organismo, str):  # ...o 'organismo' es una cadena de carácteres
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

        for nombre, config in símismo.receta['estr']['Organismos'].items():
            if nombre not in símismo.organismos:  # Si el organismo no existía...
                # Crear el organismo...
                símismo.organismos[nombre] = Organismo(nombre)

                # Y aplicar las configuraciones guardadas en la red
                símismo.organismos[nombre].receta['config'] = config

        for org in símismo.organismos:
            if org not in símismo.receta['estr']['Organismos']:
                símismo.organismos.pop(org)

        # Guardar las etapas de todos los organismos de la red y sus coeficientes en un orden reproducible

        símismo.etapas.clear()  # Borrar la lista de etapas existentes

        símismo.lista_etps = [] # para hacer

        # Crear una lista con únicamente las listas de calibraciones para cada parámetro. Será útil para las funciones
        # de simulación, calibración y validación más adelante.
        símismo.lista_calibs_paráms_interés = []
        for d_etp in símismo.lista_etps:
            for categ in d_etp['estr']['ecs'].values():
                for sub_categ in categ.values():
                    for parám in sub_categ.values():
                        if type(list(parám.values())[0]) is np.ndarray:
                            símismo.lista_calibs_paráms_interés.append(list(parám))
                        else:
                            for inter in parám.values():
                                símismo.lista_calibs_paráms_interés.append(list(inter))



        """
        for organismo in [org for (nombre, org) in sorted(símismo.organismos.items())]:

            símismo.etapas += [dict(etp[1] for etp in sorted(organismo.receta.items()))]

        # Guardar los tipos de ecuaciones activos de las etapas en un diccionario central
        for categ, dic_categ in Ec.ecuaciones:
            símismo.ecs[categ] = {}
            for subcateg in dic_categ:
                subcateg.ecs[categ][subcateg] = [etp['ecuaciones'][categ][subcateg] for etp in símismo.etapas]

        # Crear una lista con el número de la etapa en el mismo organismo que sigue cada etapa.
        lista = símismo.ecs['Orden'] = np.arange(len(símismo.etapas))
        n = 0
        for org in [org for (nombre, org) in sorted(símismo.organismos.items())]:
            pos_etps = [etp['posición'] for (nombre, etp) in sorted(org.receta['etapas'].items())]

            for i, j in enumerate(pos_etps):
                try:
                    lista[i] += pos_etps.index(j+1) - j
                except IndexError:
                    lista[n + len(pos_etps) - 1] = -1  # Para la última etapa, ponemos -1

            n += len(pos_etps)
        """

        # Crear el diccionario de tipos de ecuaciones actuales

        símismo.ecs.clear()  # Borrar todo en el diccionario existente para evitar posibilidades de cosas raras

        for categ in Ec.ecuaciones:  # Para cada tipo de ecuación posible...

            # Crear la llave correspondiente en el diccionario de tipos de ecuaciones de la red.
            símismo.ecs[categ] = {}

            # Para cada subcategoría de ecuación posible...
            for sub_categ in Ec.ecuaciones[categ]:

                # Crear una lista de tamaño igual al número de etapas en la red
                símismo.ecs[categ][sub_categ] = [None] * len(símismo.etapas)

                # Para cada etapa de esta red...
                for d_etp in símismo.etapas.values():

                    # Leer el tipo de ecuación activo para esta simulación
                    tipo_ec = d_etp['estr']['ecs'][categ][sub_categ]

                    # El número de la etapa en las matrices de esta red.
                    n_etp = d_etp['núm']

                    # Guardar el tipo de ecuación en su lugar en símismo.ecs
                    símismo.ecs[categ][sub_categ][n_etp] = tipo_ec


        símismo.lista_dic_paráms_interés = [] # para hacer

        # La red ya está lista para simular
        símismo.listo = True

    def llenar_coefs(símismo, n_etps, n_parc, n_rep_parám, n_rep_estoc, calibs):

        # Preparar la lista de calibraciones para utilizar:

        if type(calibs) is list:
            pass
        elif calibs == 'Todos':
            pass
        elif calibs == 'Comunes':
            calibs = filtrar_comunes(símismo.lista_calibs_paráms_interés)
        elif calibs == 'Correspondientes':
            corr = [x for x in calibs if x in símismo.receta['Calibraciones']]
            calibs = corr
        elif type(calibs) is str:
            calibs == [calibs]

        # Crear las matrices de coeficientes
        símismo.coefs_act = {}

        # Para cada categoría de ecuación posible...
        for categ, dic_categ in Ec.ecuaciones.items():
            símismo.coefs_act[categ] = {}  # Crear una llave correspondiente en coefs_act

            # Para cada subcategoría de ecuación posible...
            for subcateg in dic_categ:
                # Crear una lista en coefs_act para guardar los diccionarios de los parámetros de cada etapa
                coefs_act = símismo.coefs_act[categ][subcateg] = []

                # Para cada etapa en la lista de diccionarios de parámetros de interés...
                for n_etp, dic_coefs_etp in enumerate(símismo.lista_etps):

                    # Añadir el diccionario de parámetros para esta etapa en la lista
                    coefs_act[n_etp] = {}

                    # Para cada parámetro en el diccionario de las ecuaciones de esta etapa en uso actual
                    # (Ignoramos los parámetros para ecuaciones que no se usarán en esta simulación)...
                    for parám, d_parám in dic_coefs_etp[categ][subcateg]:

                        # Si no hay interacciones entre este parámetro y otras etapas...
                        if d_parám['inter'] is None:
                            # Generar la matríz de valores para este parámetro de una vez
                            coefs_act[n_etp][parám] = gen_matr_coefs(dic_parám=d_parám, calibs=calibs,
                                                                     n_rep_parám=n_rep_parám)

                        # Si, al contrario, hay interacciones (aquí con las presas de la etapa)...
                        elif d_parám['inter'] == 'presa':

                            matr = coefs_act[n_etp][parám] = np.empty(shape=(len(símismo.etapas), n_rep_parám),
                                                                             dtype=float)
                            matr.fill(np.nan)

                            for org_prs, l_etps_prs in símismo.lista_etps[n_etp]['config']['presas'].items():
                                for etp_prs in l_etps_prs:
                                    n_etp_prs = símismo.etapas[org_prs][etp_prs]['núm']
                                    matr[n_etp_prs] = gen_matr_coefs(dic_parám=d_parám,
                                                                     calibs=calibs,
                                                                     n_rep_parám=n_rep_parám)

                        # Al momento, solamente es posible tener interacciones con las presas de la etapa. Si
                        # un día alguien quiere incluir más tipos de interacciones (como, por ejemplo, interacciones
                        # entre competidores), se tendrían que añadir aquí.
                        else:
                            raise ValueError

    def prep_predics(símismo):
        # Crear las matrices para guardar resultados:
        símismo.datos['Pobs'] = np.empty(shape=(n_parc, n_rep_estoc, n_rep_parám, n_etps), dtype=int)

        símismo.datos['Depredación'] = np.zeros(shape=(n_parc, n_rep_estoc, n_rep_parám, n_etps, n_etps),
                                                dtype=int)

        for categ in símismo.datos:
            if categ not in ['Pobs', 'Depredación']:
                símismo.datos[categ] = np.zeros(shape=(n_parc, n_rep_estoc, n_rep_parám, n_etps), dtype=np.int)



    def prep_predics(símismo, n_pasos, rep_parám, rep_estoc, n_parcelas, calibs):

        n_etapas = len(símismo.etapas)

        for dato in símismo.datos:
            if dato == 'Pobs':
                símismo.datos[dato] = np.zeros(shape=(n_parcelas, rep_estoc, rep_parám, n_etapas, n_pasos),
                                               dtype=int)
            else:
                símismo.datos[dato] = np.zeros(shape=(n_parcelas, rep_estoc, rep_parám, n_etapas),
                                               dtype=int)

    def añadir_exp(símismo, experimento, corresp, categ='Organismos'):
        super().añadir_exp(experimento=experimento, corresp=corresp, categ=categ)

    def incrementar(símismo, paso, i, mov=False, extrn=None):

        pobs = símismo.datos['P'][i-1]

        # Calcular la depredación, muertes, reproducción, y movimiento entre parcelas
        depred = símismo.calc_depred(pobs=pobs, paso=paso)
        pobs -= depred

        crec = símismo.calc_crec(pobs=pobs, extrn=extrn, paso=paso)
        pobs += crec

        reprod = NotImplemented

        muertes = símismo.calc_muertes(pobs=símismo.datos['Pobs'][..., i], extrn=extrn, paso=paso)
        pobs -= muertes

        trans = símismo.calc_trans(pobs=símismo.datos['Pobs'][..., i], extrn=extrn, paso=paso)
        pobs += trans

        if mov:
            mov = símismo.calc_mov(pobs=símismo.datos['Pobs'][..., i], extrn=extrn, paso=paso)
            pobs += mov

        símismo.datos['Pobs'][..., i] = pobs

        símismo.limpiar_cohortes()

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
                depred_etp = np.square(pobs / pob_etp) * cf['a'] / (np.square(pobs / pob_etp) + cf['b'])

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
                depred_etp = pobs / pob_etp ** cf['m'] * cf['a'] / (pobs / pob_etp ** cf['m'] + cf['b'])

            elif tipo_ec == 'Tipo III_Hassell-Varley':
                # Depredación de respuesta funcional Tipo III con dependencia Hassell-Varley.
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa
                depred_etp = pobs / pob_etp ** cf['m'] * cf['a'] / (pobs / pob_etp ** cf['m'] + cf['b'])

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

        # Depredación únicamente por presa (todos los depredadores juntos)
        depred_por_presa = np.sum(depred, axis=3)

        # Si la etapa usa cohortes para cualquier otro cálculo, acutlizar los cohortes ahora.
        for n in símismo.ecs['Cohortes']:
            símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n], depred_por_presa[..., n])

        # Actualizar la matriz de poblaciones
        return depred_por_presa

    def calc_crec(símismo, pobs, extrn, paso):
        """
        Calcula las reproducciones y las transiciones de etapas de crecimiento

        :type extrn: dict
        :param extrn: diccionario de factores externos a la red (plantas, clima, etc.)

        :type paso: int


        :param pobs: matriz numpy de poblaciones actuales.
        :type pobs: np.ndarray

        :param paso:

        """

        crec = símismo.datos['Crecimiento']
        tipos_ec = símismo.ecs['Crecimiento']['Ecuación']
        modifs = símismo.ecs['Crecimiento']['Modif']

        coefs_ec = símismo.coefs_act['Crecimiento']['Ecuación']
        coefs_mod = símismo.coefs_act['Creciiento']['Modif']

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
                r *= mat.exp(-0.5 * (mat.log(extrn['temp_máx'] / cf['t']) / cf['p']) ** 2)

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
                crec_etp = pob_etp * (1 - pob_etp / k)  # Ecuación logística sencilla

            else:
                raise ValueError

            crec[:, :, :, n] = crec_etp

        crec *= paso

        símismo.redondear(crec)

        # Si la etapa usa cohortes para cualquier otro cálculo, acutlizar los cohortes ahora.
        for n in símismo.ecs['Cohortes']:
            símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n], crec[..., n])

        return crec

    def calc_reprod(símismo, pobs, extrn, paso):
        pass

    def calc_muertes(símismo, pobs, extrn, paso):

        """
        Esta función calcula las muertes de causas ambientales de la etapa.
        
        :param extrn: Un diccionario con las condiciones exógenas a la red
        :type extrn: dict

        :param pobs: La matriz de poblaciones actuales de la red. Ejes tal como indicado arriba.
        :type pobs: np.ndarray

        :param paso: El paso para la simulación.
        :type paso: int

        """

        muertes = símismo.datos['Muertes']

        tipos_ec = símismo.ecs['Muertes']['Ecuación']

        coefs = símismo.coefs_act['Muertes']['Ecuación']

        for n, ec in enumerate(tipos_ec):

            cf = coefs[n]

            if ec is None:
                continue

            elif ec == 'Constante':
                # Muertes en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
                # exponencial.

                muerte_etp = pobs * cf['q']

            elif ec == 'Log Normal Temperatura':
                # Muertes dependientes en la temperatura, calculadas con la ecuación mencionada en:
                #
                # Sunghoon Baek, Youngsoo Son, Yong-Lak Park. 2014. Temperature-dependent development and survival of
                #   Podisus maculiventris (Hemiptera: Pentatomidae): implications for mass rearing and biological
                #   control. Journal of Pest Science 87(2): 331-340.

                sobrevivencia = mat.exp(-0.5 * (mat.log(extrn['temp_máx'] / cf['t']) / cf['p']) ** 2)
                muerte_etp = pobs * sobrevivencia

            elif ec == 'Asimptótico Humedad':

                # M. P. Lepage, G. Bourgeois, J. Brodeur, G. Boivin. 2012. Effect of Soil Temperature and Moisture on
                #   Survival of Eggs and First-Instar Larvae of Delia radicum. Environmental Entomology 41(1): 159-165.

                sobrevivencia = max(0, 1 - mat.exp(-cf['a'] * (extrn['humedad'] - cf['b'])))
                muerte_etp[n] = pobs * sobrevivencia

            elif ec == 'Sigmoidal Temperatura':

                sobrevivencia = 1/(1 + mat.exp((extrn['temp_máx'] - cf['a']) / cf['b']))
                muerte_etp[n] = pobs * sobrevivencia

            else:
                raise ValueError

            muertes[:, :, :, n] = muerte_etp

        muertes *= paso
        símismo.redondear(muertes)

        # Si la etapa usa cohortes para cualquier otro cálculo, acutlizar los cohortes ahora.
        for n in símismo.ecs['Cohortes']:
            símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n], muertes[..., n])

        return muertes

    def calc_trans(símismo, pobs, extrn, paso):
        """
        Esta función calcula las transiciones de organismos de una etapa a otra. Esto puede incluir muerte por
          viejez.
        
        :param pobs:

        :param extrn:
        :type extrn: dict

        :param paso:


        """

        trans = símismo.datos['Transiciones']

        ec_edad = símismo.ecs['Transiciones']['Edad']
        probs = símismo.ecs['Muertes']['Prob']

        coefs_ed = símismo.coefs_act['Transiciones']['Edad']
        coefs_pr = símismo.coefs_act['Transiciones']['Prob']

        for n, ec_ed in enumerate(ec_edad):

            # Si no hay cálculos de transiciones para esta etapa, sigamos a la próxima etapa de una vez. Esto se
            # detecta por etapas que tienen 'None' como ecuación de probabilidad de transición.

            if probs[n] is None:
                continue

            # Si hay que guardar cuenta de cohortes, hacerlo aquí
            cf = coefs_ed[n]

            if ec_ed is None:
                edad_extra = None

            elif ec_ed == 'Días':
                # Edad calculada en días.

                edad_extra = paso

            elif ec_ed == 'Días Grados':
                # Edad calculada por días grados.

                edad_extra = símismo.días_grados(extrn['temp_máx'], extrn['temp_mín'],
                                                 umbrales=(cf['mín'], cf['máx'])
                                                 )

            elif ec_ed == 'Brière Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura Briere. En esta ecuación,
                # tal como en las otras con taza de desarrollo, quitamos el parámetro típicamente multiplicado por
                # toda la ecuación, porque eso duplicaría el propósito del parámetro de ubicación de las distribuciones
                # de probabilidad empleadas después.
                #
                # Mokhtar, Abrul Monim y Salem Saif al Nabhani. 2010. Temperature-dependent development of dubas bug,
                #   Ommatissus lybicus (Hemiptera: Tropiduchidae), an endemic pest of date palm, Phoenix dactylifera.
                #   Eur. J. Entomol. 107: 681–685
                edad_extra = extrn['temp_prom'] * (extrn['temp_prom'] - cf['t_dev_mín']) * \
                             mat.sqrt(cf['t_letal'] - extrn['temp_prom'])

            elif ec_ed == 'Brière No Linear Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura no linear de Briere.
                #
                # Youngsoo Son et al. 2012. Estimation of developmental parameters for adult emergence of Gonatocerus
                #   morgani, a novel egg parasitoid of the glassy-winged sharpshooter, and development of a degree-day
                #   model. Biological Control 60(3): 233-260.

                edad_extra = extrn['temp_prom'] * (extrn['temp_prom'] - cf['t_dev_mín']) * \
                             mat.pow(cf['t_letal'] - extrn['temp_prom'], 1/cf['m'])

            elif ec_ed == 'Logan Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura Logan:
                #
                # Youngsoo Son y Lewis, Edwin E. 2005. Modelling temperature-dependent development and survival of
                #   Otiorhynchus sulcatus (Coleoptera: Curculionidae). Agricultural and Forest Entomology 7(3): 201–209.

                edad_extra = mat.exp(cf['rho'] * extrn['temp_prom']) - \
                             mat.exp(cf['rho'] * cf['t_letal'] - (cf['t_letal'] - extrn['temp_prom']) / cf['delta'])

            else:
                raise ValueError

            # Y ya pasamos a calcular el número de individuos de esta etapa que se transicionan en este paso de tiempo
            cf = coefs_pr[n]
            if probs[n] == 'Constante':
                # Muertes en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
                # exponencial.

                # Tomamos el paso en cuenta según las regals de probabilidad:
                #   p(x sucede n veces) = (1 - (1- p(x))^n)

                trans_etp = pobs * (1 - (1 - cf['q']) ** paso)

                # Si la etapa usa cohortes para cualquier otro cálculo (transiciones a parte), acutlizar los
                # cohortes ahora.
                if n in símismo.ecs['Cohortes']:
                    símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n], trans_etp)

            else:
                # Aquí tenemos todas las probabilidades de muerte dependientes en distribuciones de cohortes:

                edad_extra *= paso

                cohortes = símismo.datos['Cohortes'][n]['Pobs']
                edades = símismo.datos['Cohortes'][n]['Edades']['Transiciones']

                if edad_extra is None:
                    raise ValueError('Se debe usar una ecuación de edad para poder usar distribuciones de cohortes'
                                     'en el cálculo de transiciones de inviduos.')

                try:
                    trans_etp = símismo.trans_cohorte(pobs=cohortes, edades=edades, cambio=edad_extra,
                                                      tipo_dist=probs[n], paráms_dist=cf)
                except ValueError:
                    raise ValueError('Error en el tipo de distribución de probabilidad para muertes naturales.')

            n_recip = símismo.ecs['Orden'][n]

            # Quitar el número de indivuduos que transicionaron desde una etapa
            trans[..., n] -= trans_etp

            # Si no eran adultos muríendose por viejez, añadirlos a la próxima etapa
            if n_recip >= 0:
                if n_recip in símismo.ecs['Cohortes']:
                    # Si la próxima fase también tiene cohortes, añadirlo aquí
                    símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n_recip], trans_etp)

                # Y guardar estos datos en la matriz general de transiciones.
                trans[..., n_recip] += trans_etp

        símismo.redondear(trans)

        return trans

    def calc_mov(símismo, pobs, paso, extrn):
        """
        Calcula la imigración i emigración de organismos entre parcelas

        :type pobs: np.narray
        :param pobs:
        :type paso: int
        :param paso:
        :param extrn:

        :return:
        """
        mov = símismo.datos['Movimiento']

        tipos_ec = símismo.ecs['Movimiento']

        coefs = símismo.coefs_act['Movimiento']

        for ec in tipos_ec:
            pass

        # Si la etapa usa cohortes para cualquier otro cálculo, acutlizar los cohortes ahora.
        for n in símismo.ecs['Cohortes']:
            símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n], mov[..., n])

        return mov

    def limpiar_cohortes(símismo):
        for n, etp in enumerate(símismo.datos['Cohortes']):
            vacíos = (etp['Pobs'] == 0)
            for ed in etp['Edades'].values():
                ed[vacíos] = np.nan

    def prep_obs_exper(símismo, exper):


        dic_líms = {}
        dic_parám = {}

        for org, d_org in símismo.etapas.items():
            dic_líms[org] = {}
            dic_parám[org] = {}

            for etp, d_etp in org.items():
                dic_líms[org][etp] = {}
                dic_parám[org][etp] = {}

                dic_ecs = d_etp['estr']['ecs']

                for categ, d_categ in dic_ecs.items():
                    dic_parám[org][etp][categ] = {}
                    dic_líms[org][etp][categ] = {}

                    for subcateg in d_categ:
                        dic_parám[org][etp][categ][subcateg] =
                        dic_líms[org][etp][categ][subcateg] =



        for categ, d_categ in etp['estr']['ecs'].items():
                dic_líms[categ] = {}
                for

        dic_parám =
        dic_líms = Ec.ecuaciones

        obs =


        return obs, dic_parám, dic_líms

    def simul_exps(símismo, paso=1, extrn=None):

        egresos = np.array()

        i_obs = np.array(())
        list_obs = np.array(())

        for exp, d_exp in símismo.observ.items():
            for org, d_org in d_exp[''].items():
                for etp, datos in d_org.items():
                    pass

            # para hacer: inicializar las poblaciones a t=0

            # Para cada paso de tiempo, incrementar el modelo
            tiempo_final = max(i_obs)

            for org, d_org in d_exp.items():
                for etp_datos in d_org.items():
                    pass
            i = None
            símismo.incrementar(paso, i=i + 1, extrn=extrn)

        return egresos


    def poner_val(símismo, ):
        pass

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
    def trans_cohorte(pobs, edades, cambio, tipo_dist, paráms_dist):
        """

        :param pobs: Una matriz multidimensional de la distribución de los cohortes de la etapa. Cada valor representa
          el número de individuos en una edad particular (determinada por el valor correspondiente en la matriz edades).
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

        :return: El número total de individuos que transicionaron.
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

    @staticmethod
    def añadir_a_cohorte(dic_cohorte, nuevos):

        try:
            primer_vacío = np.where(dic_cohorte['Pobs'] == 0)[0][0]
        except IndexError:
            primer_vacío = dic_cohorte['Pobs'].size()
            np.append(dic_cohorte['Pobs'], np.zeros_like(dic_cohorte['Pobs']), axis=0)

            for ed in dic_cohorte['Edades'].values():
                np.append(ed, np.zeros_like(ed), axis=0)

        dic_cohorte['Pobs'][primer_vacío] = nuevos

        for ed in dic_cohorte['Edades'].values():
            ed[primer_vacío] = 0

    @staticmethod
    def quitar_de_cohorte(dic_cohorte, muertes):

        pobs = dic_cohorte['Pobs']

        while sum(muertes):
            p = muertes / pobs.sum(axis=0)
            quitar_por_cohorte = np.floor(p * pobs)

            pobs -= quitar_por_cohorte

            muertes -= np.sum(quitar_por_cohorte, axis=0)


def encontrar_subclase_org(ext):

    def sacar_subclases(cls):
        return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                       for g in sacar_subclases(s)]

    for sub in sacar_subclases(Organismo):
        if sub.ext == ext:
            return sub

    raise ValueError

