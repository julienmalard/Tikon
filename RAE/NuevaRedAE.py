import math as mat
import numpy as np

import MATEMÁTICAS.Distribuciones as Ds
import MATEMÁTICAS.Ecuaciones as Ec
from MATEMÁTICAS.NuevoIncert import numerizar, gen_vector_coefs
from NuevoCoso import Simulable, valid_vals_inic
from RAE.ORGANISMO import Organismo


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
        :param nombre: El nombre de la red.
        :type nombre: str

        :param organismos: Una lista de objetos o nombres de organismos para añadir a la red, o una instancia única
          de un tal objeto o nombre.
        :type organismos: list

        :param fuente: De dónde cargar la red, si estamos cargando una red ya definida.
        :type fuente: str
        """

        super().__init__(nombre=nombre, fuente=fuente)

        # La información necesaria para recrear la red
        símismo.receta['estr'] = dict(Organismos={})

        # Unas referencias internas para facilitar el manejo de la red.
        símismo.organismos = {}  # Para guardar una referencia a los objetos de los organismos en la red
        símismo.etapas = []  # Una lista de las recetas (y más) de las etapas de los organismos en la red
        símismo.núms_etapas = {}

        # Diccionario que contendrá matrices de los coeficientes de la red
        símismo.coefs_act = {}

        # Para guardar los tipos de ecuaciones de los organismos en la red
        símismo.ecs = dict([(cat, dict([(sub_cat, [])
                                        for sub_cat in Ec.ecs_orgs[cat].keys()]))
                            for cat in Ec.ecs_orgs.keys()
                            ]
                           )

        # La matriz de datos de las simulaciones (incluso los datos de poblaciones)
        símismo.predics = {'Pobs': np.array([]),
                           'Depredación': np.array([]),
                           'Crecimiento:': np.array([]),
                           'Reproducción': np.array([]),
                           'Muertes': np.array([]),
                           'Transiciones': np.array([]),
                           'Movimiento': np.array([])
                           }

        # Un diccionario para guardar información específica a cada experimento asociado para poder procesar
        # las predicciones de la red en función a cada experimento.
        símismo.formatos_exps = {'etps_interés': {}, 'combin_etps': {}, 'días_interés': {}, 'nombres_cols': {}}

        # Si ya se especificaron organismos en la inicialización, añadirlos a la red.
        if type(organismos) is not list:
            organismos = [organismos]

        if organismos is not None:
            for org in organismos:
                símismo.añadir_org(org)

        # Actualizar el organismo
        símismo.actualizar()

    def añadir_org(símismo, organismo):
        """
        Esta función añade un organismo a la red.

        :param organismo: El organismo que hay que añadir a la red
        :type organismo: Organismo | str
        """

        # Sacar el nombre del organismo, tanto como el objeto correspondiente.
        if isinstance(organismo, Organismo):
            # Si 'organismo' es un objeto de tipo Organismo, guardar su nombre y el objeto sí mismo
            nombre = organismo.nombre
            obj_org = organismo

        elif isinstance(organismo, str):
            # Pero si 'organismo' es una cadena de carácteres, crear el objeto correspondiente y guardar su nombre
            obj_org = Organismo(organismo)  # Crear el organismo correspondiente
            nombre = organismo

        else:
            # Si organismo es ni objeto de Organismo ni el nombre de uno, hay un error.
            raise TypeError('"organismo" debe ser de tipo Organismo o de texto.')

        # Añadir el organismo a la receta
        dic_org = símismo.receta['estr']['Organismos'][nombre] = {}
        dic_org['config'] = organismo.config
        dic_org['fuente'] = organismo.fuente

        # Poner el organismo en la lista activa
        símismo.organismos[nombre] = obj_org

        # Guardar el Organismo en la lista de objetos de la red.
        símismo.objetos.append(obj_org)

        # Actualizar la red
        símismo.actualizar()

    def quitar_org(símismo, organismo):
        """
        Esta función quita un organismo de la Red.

        :param organismo: El organismo para quitar
        :type organismo: Organismo or str
        """

        if isinstance(organismo, Organismo):
            # Si 'organismo' es un objeto de tipo Organismo...
            obj_org = organismo
            nombre = organismo.nombre

        elif isinstance(organismo, str):
            # Si 'organismo' es una cadena de carácteres
            nombre = organismo

            try:
                obj_org = símismo.organismos[organismo]
            except KeyError:
                raise KeyError('El organismo especificado no existía en esta red.')

        else:
            # Si "organismo" no es de tipo Organismo o texto, hay un error.
            raise TypeError

        # Quitar el Organismo de la Red, pero con cuidado con los errores
        try:
            símismo.receta['estr']['Organismos'].pop(nombre)  # Quitar el nombre de la receta
            símismo.organismos.pop(nombre)  # Quitar el organismo del diccionario de organismos

        except KeyError:
            # Si Organismo no existía en la Red, no se puede quitar.
            raise KeyError('El organismo especificado no existía en esta red.')

        # Quitar Organismo de la lista de objetos de la red.
        símismo.objetos.remove(obj_org)

        # Actualizar la red
        símismo.actualizar()

    def actualizar(símismo):
        """
        Actualiza la lista de etapas y las matrices de coeficientes de la red y sus objetos.

        """

        # Verificar que todos los organismos en la receta, y únicamente los organismos en la receta, estén en la
        # lista de organismos activos de la red.
        for nombre, dic_org in símismo.receta['estr']['Organismos'].items():

            # Si el organismo en la receta de la Red no existía en el diccionario de organismos activos...
            if nombre not in símismo.organismos:

                # ...crear el organismo
                símismo.organismos[nombre] = Organismo(nombre)

                # ...y aplicar las configuraciones guardadas en la red
                símismo.organismos[nombre].config = dic_org['config']

        for org in símismo.organismos:
            if org not in símismo.receta['estr']['Organismos']:
                # Si un organismo activo en la Red no existe en la receta de la Red...

                # ...quitar el organismo del diccionario de organismos activos
                símismo.organismos.pop(org)

        # Guardar las etapas de todos los organismos de la red y sus coeficientes en un orden reproducible
        símismo.etapas.clear()  # Borrar la lista de etapas existentes

        n = 0
        for nombre_org, org in sorted(símismo.organismos.items()):
            símismo.núms_etapas[nombre_org] = {}
            for etp in org.etapas:
                # Para cada etapa de cada organismo...

                # Una referencia al nombre de la etapa
                nombre_etp = etp['nombre']
                # Crear un diccionario con la información de la etapa
                dic_etp = dict(org=nombre_org,
                               nombre=nombre_etp,
                               dic=etp,
                               conf=org.config[nombre_etp],
                               coefs=org.receta['coefs'][nombre_etp])

                # Y guardar este diccionario en la Red
                símismo.etapas.append(dic_etp)

                # Y guardamos una referencia al número de la etapa
                símismo.núms_etapas[nombre_org][nombre_etp] = n

                n += 1

        # Crear el diccionario de los tipos de las ecuaciones activas para cada etapa.
        símismo.ecs.clear()  # Borrar todo en el diccionario existente para evitar posibilidades de cosas raras

        for categ in Ec.ecs_orgs:
            # Para cada tipo de ecuación posible...

            # Crear la llave correspondiente en el diccionario de tipos de ecuaciones de la red.
            símismo.ecs[categ] = {}

            # Para cada subcategoría de ecuación posible...
            for sub_categ in Ec.ecs_orgs[categ]:

                # Crear una lista de tamaño igual al número de etapas en la red
                símismo.ecs[categ][sub_categ] = []

                # Para cada etapa de esta red...
                for d_etp in símismo.etapas:
                    # Leer el tipo de ecuación activo para esta simulación
                    try:
                        tipo_ec = d_etp['dic']['ecs'][categ][sub_categ]
                    except KeyError:
                        raise KeyError

                    # Guardar el tipo de ecuación en su lugar en símismo.ecs
                    símismo.ecs[categ][sub_categ].append(tipo_ec)

        # Para hacer: incluir posibilidades de cohortes
        símismo.ecs['Cohortes'] = []

        # La red ya está lista para simular
        símismo.listo = True

    def dibujar(símismo, mostrar=True, archivo=''):
        pass

    def _calc_depred(símismo, pobs, paso):
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
        :type pobs: np.ndarray

        :param paso: El paso de tiempo de la simulación.
        :type paso: int

        """

        # Calcular cuántas presas cada especie de depredador podría comerse

        # A este punto, depred representa la depredación potencial per cápita de depredador
        depred = símismo.predics['Depredación']
        tipos_ec = símismo.ecs['Depredación']['Ecuación']

        # La lista de los coeficientes de cada etapa para la depredación
        coefs = numerizar(símismo.coefs_act['Depredación']['Ecuación'])

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

            elif tipo_ec == 'Kovai':
                # Depredación de respuesta funcional de asíntota doble (ecuación Kovai).
                pob_etp = pobs[:, :, :, n]  # La población de esta etapa
                k = np.divide(np.multiply(cf['b'],
                                          np.square(pobs)),
                              np.add(np.square(pobs),
                                     cf['c'])
                              )
                m = (1 / cf['a'] - 1) * np.divide(cf['b'], pobs)

                depred_etp = k / (1 + m * pob_etp)

                # Ajusta para presas múltiples

            else:
                # Si el tipo de ecuación no estaba definida arriba, hay un error.
                raise ValueError('Tipo de ecuación "%s" no reconodico para cálculos de depradación.' % tipo_ec)

            print('depred 1', depred_etp)
            input()
            depred[:, :, :, n, :] = depred_etp

        # Convertir depredación potencial por depredador a depredación potencial total (multiplicar por la población
        # de cada depredador). También multiplicamos por el paso de la simulación. 'depred' ahora esta en unidades
        # del número total de presas comidas por cada tipo de depredador por unidad de tiempo.
        np.multiply(depred, pobs*paso, out=depred)

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

        # Si la etapa usa cohortes para cualquier otro cálculo, actualizar los cohortes ahora.
        for n in símismo.ecs['Cohortes']:
            símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n], depred_por_presa[..., n])

        # Actualizar la matriz de poblaciones
        pobs = np.nansum(pobs, -depred_por_presa)

    def _calc_crec(símismo, pobs, extrn, paso):
        """
        Calcula las reproducciones y las transiciones de etapas de crecimiento

        :param pobs: Matriz numpy de poblaciones actuales. Eje 0 =
        :type pobs: np.ndarray

        :param extrn: Diccionario de factores externos a la red (plantas, clima, etc.)
        :type extrn: dict

        :param paso: El paso para la simulación.
        :type paso: int

        """

        crec = símismo.predics['Crecimiento']
        tipos_ec = símismo.ecs['Crecimiento']['Ecuación']
        modifs = símismo.ecs['Crecimiento']['Modif']

        coefs_ec = numerizar(símismo.coefs_act['Crecimiento']['Ecuación'])
        coefs_mod = numerizar(símismo.coefs_act['Crecimiento']['Modif'])

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

                k = np.sum(np.multiply(pobs, cf['K']))  # Calcular la capacidad de carga
                crec_etp = pob_etp * (1 - pob_etp / k)  # Ecuación logística sencilla

            else:
                raise ValueError

            crec[:, :, :, n] = crec_etp

        crec *= paso

        símismo.redondear(crec)

        # Si la etapa usa cohortes para cualquier otro cálculo, acutlizar los cohortes ahora.
        for n in símismo.ecs['Cohortes']:
            símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n], crec[..., n])

        # Actualizar la matriz de poblaciones
        pobs += crec

    def _calc_reprod(símismo, pobs, extrn, paso):
        reprod = NotImplemented

        # Actualizar la matriz de predicciones
        pobs += reprod

    def _calc_muertes(símismo, pobs, extrn, paso):

        """
        Esta función calcula las muertes de causas ambientales de la etapa.

        :param extrn: Un diccionario con las condiciones exógenas a la red
        :type extrn: dict

        :param pobs: La matriz de poblaciones actuales de la red. Ejes tal como indicado arriba.
        :type pobs: np.ndarray

        :param paso: El paso para la simulación.
        :type paso: int

        """

        muertes = símismo.predics['Muertes']

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

                sobrevivencia = 1 / (1 + mat.exp((extrn['temp_máx'] - cf['a']) / cf['b']))
                muerte_etp[n] = pobs * sobrevivencia

            else:
                raise ValueError

            muertes[:, :, :, n] = muerte_etp

        muertes *= paso
        símismo.redondear(muertes)

        # Si la etapa usa cohortes para cualquier otro cálculo, acutlizar los cohortes ahora.
        for n in símismo.ecs['Cohortes']:
            símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n], muertes[..., n])

        # Actualizar la matriz de predicciones
        pobs -= muertes

    def _calc_trans(símismo, pobs, extrn, paso):
        """
        Esta función calcula las transiciones de organismos de una etapa a otra. Esto puede incluir muerte por
          viejez.

        :param pobs:
        :type pobs: np.ndarray

        :param extrn:
        :type extrn: dict

        :param paso:
        :type paso: int

        """

        trans = símismo.predics['Transiciones']

        ec_edad = símismo.ecs['Transiciones']['Edad']
        probs = símismo.ecs['Transiciones']['Prob']

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
                             mat.pow(cf['t_letal'] - extrn['temp_prom'], 1 / cf['m'])

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

                cohortes = símismo.predics['Cohortes'][n]['Pobs']
                edades = símismo.predics['Cohortes'][n]['Edades']['Transiciones']

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

        pobs += trans

    def _calc_mov(símismo, pobs, paso, extrn):
        """
        Calcula la imigración i emigración de organismos entre parcelas

        :param pobs:
        :type pobs: np.narray

        :param paso:
        :type paso: int

        :param extrn:
        :type extrn: dict

        """

        mov = símismo.predics['Movimiento']

        tipos_ec = símismo.ecs['Movimiento']

        coefs = símismo.coefs_act['Movimiento']

        for ec in tipos_ec:
            mobil = NotImplemented
            modif_peso = NotImplemented
            área = NotImplemented
            peso = área * modif_peso

            mov = NotImplemented

        # Si la etapa usa cohortes para cualquier otro cálculo, acutlizar los cohortes ahora.
        for n in símismo.ecs['Cohortes']:
            símismo.añadir_a_cohorte(símismo.ecs['Cohortes'][n], mov[..., n])

        # Actualizar la matriz de predicciones
        pobs += mov

    def _limpiar_cohortes(símismo):
        for n, etp in enumerate(símismo.ecs['Cohortes']):
            vacíos = (etp['Pobs'] == 0)
            for ed in etp['Edades'].values():
                ed[vacíos] = np.nan

    def _poner_val(símismo, ):
        pass

    def _incrementar(símismo, paso, i, mov=False, extrn=None):

        # Empezar con las poblaciones del paso anterior
        print(símismo.predics)
        input()
        pobs = símismo.predics['Pobs'][..., i - 1].copy()

        # Calcular la depredación, crecimiento, reproducción, muertes, transiciones, y movimiento entre parcelas
        print(1, pobs)
        # Una especie que mata a otra.
        símismo._calc_depred(pobs=pobs, paso=paso)
        print('depred', símismo.predics['Depredación'])
        print(2, pobs)
        quit()
        # Una población que crece (misma etapa)
        símismo._calc_crec(pobs=pobs, extrn=extrn, paso=paso)
        print(3, pobs)

        # Una etapa que crear más individuos de otra etapa
        # para hacer: símismo._calc_reprod(pobs=pobs, extrn=extrn, paso=paso)

        # Muertes por el ambiente
        símismo._calc_muertes(pobs=pobs, extrn=extrn, paso=paso)
        print(4, pobs)

        # Una etapa que cambia a otra, o que se muere por su edad.
        símismo._calc_trans(pobs=pobs, extrn=extrn, paso=paso)
        print(5, pobs)

        if mov:
            # Movimientos de organismos de una parcela a otra.
            símismo._calc_mov(pobs=pobs, extrn=extrn, paso=paso)

        # Añadir las predicciones de poblaciones para el paso de tiempo i en la matriz de predicciones.
        print('i', i)
        símismo.predics['Pobs'][..., i] = pobs

        # Limpiar los cohortes de los organismos de la Red.
        símismo._limpiar_cohortes()

    def _procesar_validación(símismo, vector_obs, vector_preds):
        pass

    def _sacar_líms_coefs_interno(símismo):
        """
        No hay nada nada que hacer, visto que una red no tiene coeficientes propios.
        """

        return []

    def _sacar_coefs_interno(símismo):
        """
        No hay nada nada que hacer, visto que una red no tiene coeficientes propios.
        """

        return []

    def _acción_añadir_exp(símismo, experimento, corresp):
        """
        Ver la documentación de Simulable.

        :type experimento: Experimento
        :type corresp: dict

        """

        # Verificar que los nombres de organismos y etapas estén correctos
        for org, d_org in corresp.items():
            if org not in símismo.receta['estr']['Organismos']:
                raise ValueError('El organismo "%s" no existe en la red.' % org)

            for etp, d_etp in d_org.items():
                if etp not in símismo.núms_etapas[org]:
                    raise ValueError('Organismo "%s" no tiene etapa "%s".' % (org, etp))

        # El nombre del experimento
        nombre = experimento.nombre

        # Crear las llaves para este experimento en el diccionario de formatos de la red.
        for ll in símismo.formatos_exps:
            símismo.formatos_exps[ll][nombre] = []

        # Los días de observaciones
        símismo.formatos_exps['días_interés'][nombre] = experimento.datos['Organismos']['tiempo']

        # Para simplificar el código
        lista_nombres_cols = símismo.formatos_exps['nombres_cols'][nombre]

        # Para guardar las etapas que corresponden a la misma columna en la base de datos, si aplica.
        lista_comunes = [[]] * len(símismo.etapas)

        # Para cada organismo en el diccionario de correspondencias
        for org, d_org in corresp.items():

            # Para cada etapa del organismo en el diccionario de correspondencias
            for etp, d_etp in d_org.items():

                # Si hay más que una columna de la base de datos
                lista_cols = corresp[org][etp]

                # Asegurar el formato correcto
                if type(lista_cols) is not list:
                    lista_cols = [lista_cols]

                # Si hay más que una columna de la base de datos correspondiendo a la etapa, sumarlos
                if len(lista_cols) > 1:
                    # El nombre de la nueva columna sumada
                    nombre_col = '&'.join(str(x) for x in sorted(lista_cols))

                    # Hacer la suma
                    suma = np.sum([experimento.datos['Organismos']['obs'][x] for x in lista_cols], axis=0)

                    # Guardar la nueva columna en el Experimento
                    experimento.datos['Organismos']['obs'][nombre_col] = suma

                else:
                    # Si solo hay una columna para la etapa, utilizar esta.
                    nombre_col = lista_cols[0]

                # Guardar el número de la etapa en la Red
                núm_etp = símismo.núms_etapas[org][etp]

                lista_comunes[núm_etp].append(núm_etp)

                # Si la columna ya no se utilizó para otra etapa...
                if len(lista_comunes[núm_etp]) == 1:
                    símismo.formatos_exps['etps_interés'][nombre].append(núm_etp)
                    lista_nombres_cols.append(nombre_col)

        símismo.formatos_exps['combin_etps'][nombre] = [(n, x) for n, x in enumerate(lista_comunes) if len(x) > 1]

    def _procesar_predics_calib(símismo):

        vector_predics = np.array([])

        for nombre, predic in sorted(símismo.predics_exps.items()):

            etps_interés = símismo.formatos_exps['etps_interés'][nombre]

            # {exp: [(1, [3,4]), etc...], ...}
            combin_etps = símismo.formatos_exps['combin_etps'][nombre]

            días_interés = símismo.formatos_exps['días_interés'][nombre]
            print(combin_etps)  # para hacer: quitar duplicaciones recíprocas
            for i in combin_etps:
                predic['Pobs'][..., i[0], :] += np.sum(predic['Pobs'][..., i[1], :], axis=3)

            vector_predics = np.concatenate((vector_predics,
                                             predic['Pobs'][..., etps_interés, días_interés].flatten()))

        return vector_predics

    def _prep_args_simul_exps(símismo, exper, n_rep_estoc, n_rep_paráms):
        """
        Ver la documentación de Coso.

        :type exper: list
        :type n_rep_estoc: int
        :type n_rep_paráms: int
        :rtype: dict

        """

        dic_args = dict(datos_inic={},
                        n_pasos={},
                        extrn={})

        # El número de etapas se toma de la Red sí misma
        n_etapas = len(símismo.etapas)

        # Para cada experimento...
        for exp in exper:
            # Sacamos el objeto correspondiente al experimento
            obj_exp = símismo.exps[exp]

            # Calculamos el número de parcelas en el experimento
            n_parc = valid_vals_inic(obj_exp.datos['Organismos']['obs'])

            # El número de pasos necesarios es la última observación en la base de datos de organismos.
            n_pasos = int(obj_exp.datos['Organismos']['tiempo'][-1] + 1)

            # Generamos el diccionario (vacío) de datos iniciales
            datos_inic = símismo.gen_dic_matr_predic(n_parc=n_parc, n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_paráms,
                                                     n_etps=n_etapas, n_pasos=n_pasos)

            # Llenamos la poblaciones iniciales
            for i, n_etp in enumerate(símismo.formatos_exps['etps_interés'][exp]):

                # La matriz de datos iniciales para una etapa. Eje 0 = parcela, eje 1 = tiempo. Quitamos eje 1.
                # noinspection PyTypeChecker
                nombre_col = símismo.formatos_exps['nombres_cols'][exp][i]
                matr_obs_inic = obj_exp.datos['Organismos']['obs'][nombre_col][:, 0]

                # Llenamos eje 0 (parcela), eje 1 y 2 (repeticiones estocásticas y paramétricas) de la etapa
                # en cuestión a tiempo 0.
                datos_inic['Pobs'][..., n_etp, 0] = matr_obs_inic[:, np.newaxis, np.newaxis]

            # Y, por fin, guardamos este diccionario bajo la llave "datos_inic" del diccionario.
            dic_args['datos_inic'][exp] = datos_inic

            # También guardamos el número de pasos y diccionarios de ingresos externos.
            dic_args['n_pasos'][exp] = n_pasos
            dic_args['extrn'][exp] = None  # Para hacer para implementar clima, apliaciones y cultivos

        return dic_args

    def _llenar_coefs(símismo, n_rep_parám, calibs, comunes):
        """
        Ver la documentación de Coso.

        :type n_rep_parám: int
        :type calibs: list | str
        :type comunes: bool

        """

        # El número de etapas en la Red
        n_etapas = len(símismo.etapas)

        # Asegurar que calibs es una lista
        if type(calibs) is str:
            calibs = [calibs]

        # Vaciar los coeficientes existentes.
        símismo.coefs_act.clear()

        # Para cada categoría de ecuación posible...
        for categ, dic_categ in Ec.ecs_orgs.items():

            # Crear una llave correspondiente en coefs_act
            símismo.coefs_act[categ] = {}

            # Para cada subcategoría de ecuación...
            for subcateg in dic_categ:

                # Crear una lista en coefs_act para guardar los diccionarios de los parámetros de cada etapa
                coefs_act = símismo.coefs_act[categ][subcateg] = [{}] * n_etapas

                # La lista de los tipos de ecuaciones para esta subcategoría para todas las etapas
                lista_tipos_ecs = símismo.ecs[categ][subcateg]

                # Para cada etapa en la lista de diccionarios de parámetros de interés de las etapas...
                for n_etp, tipo_ec in enumerate(lista_tipos_ecs):

                    # Para cada parámetro en el diccionario de las ecuaciones de esta etapa en uso actual
                    # (Ignoramos los parámetros para ecuaciones que no se usarán en esta simulación)...
                    for parám, d_parám in Ec.ecs_orgs[categ][subcateg][tipo_ec].items():

                        # El diccionario del parámetro
                        d_parám_etp = símismo.etapas[n_etp]['coefs'][categ][subcateg][tipo_ec][parám]

                        # Si no hay interacciones entre este parámetro y otras etapas...
                        if d_parám['inter'] is None:
                            # Generar la matríz de valores para este parámetro de una vez

                            coefs_act[n_etp][parám] = gen_vector_coefs(dic_parám=d_parám_etp, calibs=calibs,
                                                                       n_rep_parám=n_rep_parám,
                                                                       comunes=comunes)

                        # Si, al contrario, hay interacciones (aquí con las presas de la etapa)...
                        elif d_parám['inter'] == 'presa':
                            # Generar una matriz para guardar los valores de parámetros. Eje 0 = repetición paramétrica,
                            # eje 1 = presa.
                            matr = coefs_act[n_etp][parám] = np.zeros(shape=(n_rep_parám, len(símismo.etapas)),
                                                                      dtype=object)

                            # Para cada presa del organismo...
                            for org_prs, l_etps_prs in símismo.etapas[n_etp]['conf']['presa'].items():

                                for etp_prs in l_etps_prs:

                                    n_etp_prs = símismo.núms_etapas[org_prs][etp_prs]

                                    matr[:, n_etp_prs] = gen_vector_coefs(dic_parám=d_parám_etp[org_prs][etp_prs],
                                                                          calibs=calibs,
                                                                          n_rep_parám=n_rep_parám,
                                                                          comunes=comunes)

                        else:

                            # Al momento, solamente es posible tener interacciones con las presas de la etapa. Si
                            # un día alguien quiere incluir más tipos de interacciones (como, por ejemplo,
                            # interacciones entre competidores), se tendrían que añadir aquí.
                            raise ValueError('Interacción "%s" no reconocida.' % d_parám['inter'])

    def _prep_predics(símismo, n_pasos, n_rep_parám, n_rep_estoc, n_parcelas):
        """
        Ver la documentación de Coso para una explicación.

        :type n_pasos: int
        :type n_rep_parám: int
        :type n_rep_estoc: int
        :type n_parcelas: int

        """

        n_etapas = len(símismo.etapas)

        símismo.predics['Pobs'] = np.zeros(shape=(n_parcelas, n_rep_estoc, n_rep_parám, n_etapas, n_pasos),
                                           dtype=int)
        símismo.predics['Depredación'] = np.zeros(shape=(n_parcelas, n_rep_estoc, n_rep_parám, n_etapas, n_etapas),
                                                  dtype=int)

        # Crear las matrices para guardar resultados:
        for categ in símismo.predics:
            if categ not in ['Pobs', 'Depradación']:
                símismo.predics[categ] = np.zeros(shape=(n_parcelas, n_rep_estoc, n_rep_parám, n_etapas),
                                                  dtype=int)

    def _prep_obs_exper(símismo, exper):
        """
        Ver la documentación de Simulable.

        :type exper: list
        :rtype: np.ndarray

        """

        lista_obs = []

        # Para cada experimento, en orden...
        for exp in sorted(exper):

            # Para cada observación de organismos de este experimento para cual tenemos datos, en orden...
            for nombre_col in símismo.formatos_exps['nombres_cols'][exp]:

                # Sacar los datos del Experimento
                datos_etp = símismo.exps[exp].datos['Organismos']['obs'][nombre_col]

                # Guardar los datos aplastados en una única dimensión de matriz numpy (esto combina las dimensiones
                # de parcela (eje 0) y de tiempo (eje 1).
                lista_obs.append(datos_etp.flatten())

        return np.concatenate(lista_obs)

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
        print('matriz', matriz)
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

    @staticmethod
    def gen_dic_matr_predic(n_parc, n_rep_estoc, n_rep_parám, n_etps, n_pasos):
        """
        Esta función genera un diccionario con matrices del tamaño apropiado para guardar las predicciones del modelo.
          Por usar una función auxiliar, se facilita la generación de matrices para simulaciones de muchos experimentos.

        :param n_parc: El número de parcelas
        :type n_parc: int

        :param n_rep_estoc: El número de repeticiones estocásticas
        :type n_rep_estoc: int

        :param n_rep_parám: El número de repeticiones paramétricas
        :type n_rep_parám: int

        :param n_etps: El número de etapas de organismos en la Red.
        :type n_etps: int

        :param n_pasos: El número de pasos para la simulación
        :type n_pasos: int

        :return: Un diccionario del formato de símismo.predics según las especificaciones en los argumentos de la
          función.
        :rtype: dict

        """

        # El tamaño estándar para una matriz de resultados (algunos resultados tienen unas dimensiones adicionales).
        tamaño_normal = (n_parc, n_rep_estoc, n_rep_parám, n_etps)

        # El diccionario en formato símismo.predics
        dic = {'Pobs': np.zeros(shape=(*tamaño_normal, n_pasos)),
               'Depredación': np.zeros(shape=(*tamaño_normal, n_etps)),
               'Crecimiento': np.zeros(shape=tamaño_normal),
               'Reproducción': np.zeros(shape=tamaño_normal),
               'Muertes': np.zeros(shape=tamaño_normal),
               'Transiciones': np.zeros(shape=tamaño_normal),
               'Movimiento': np.zeros(shape=tamaño_normal)
               }

        return dic
