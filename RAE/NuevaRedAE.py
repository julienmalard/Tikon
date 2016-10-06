import math as mat
import os
from warnings import warn as avisar
import numpy as np

import Matemáticas.Distribuciones as Ds
import Matemáticas.Ecuaciones as Ec
import RAE.Planta as Plt
from Matemáticas.NuevoIncert import numerizar, validar, gen_vector_coefs, gráfico
from Matemáticas.Experimentos import Experimento
from NuevoCoso import Simulable
from RAE.Organismo import Organismo


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

    def __init__(símismo, nombre, organismos=None, proyecto=None, fuente=None):

        """
        :param nombre: El nombre de la red.
        :type nombre: str

        :param organismos: Una lista de objetos o nombres de organismos para añadir a la red, o una instancia única
          de un tal objeto o nombre.
        :type organismos: list

        :param fuente: De dónde cargar la Red, si estamos cargando una Red ya definida.
        :type fuente: str
        """

        super().__init__(nombre=nombre, proyecto=proyecto, fuente=fuente)

        # La información necesaria para recrear la Red
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

        # Para guardar el orden relativo de transiciones y de reproducciones entre etapas
        símismo.orden = {}

        # Para guardar etapas que siempre se deben combinar antes de reportar resultados (por ejemplo, etapas fantasmas)
        símismo.fantasmas = {}

        # La matriz de datos de las simulaciones (incluso los datos de poblaciones)
        símismo.predics = {'Pobs': np.array([]),
                           'Depredación': np.array([]),
                           'Crecimiento:': np.array([]),
                           'Reproducción': np.array([]),
                           'Muertes': np.array([]),
                           'Transiciones': np.array([]),
                           'Movimiento': np.array([]),
                           'Cohortes': {}
                           }

        # Un diccionario para guardar información específica a cada experimento asociado para poder procesar
        # las predicciones de la red en función a cada experimento.
        símismo.info_exps = {'etps_interés': {}, 'combin_etps': {}, 'nombres_cols': {},
                             'ubic_obs': {}, 'parcelas': {}}

        # Para guardar una conexión con los organismos de plantas en la red
        símismo.plantas = {'dic': {}, 'n_etp': {}}

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
        Actualiza la lista de etapas y las matrices de coeficientes de la red y de sus objetos.

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
        símismo.plantas['dic'].clear()  # Borrar los diccionarios para plantas
        símismo.plantas['n_etp'].clear()

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

                # Para la gestión de cultivos/plantas
                if isinstance(org, Plt.Planta):
                    símismo.plantas['dic'][
                        n] = org.densidad  # arreglar: ¿agrega el número para todas etapas de la planta?
                    símismo.plantas['n_etp'][n] = nombre_etp

                n += 1

        # Crear etapas fantasmas para huéspedes infectados
        n_etps_reg = len(símismo.etapas)  # El número de etapas regulares (no fantasmas)

        for etp in símismo.etapas:
            # Para cada etapa de la Red...

            # El diccionario de huéspedes de la etapa
            dic_hués = etp['config']['huésped']

            if len(dic_hués):
                # Si esta etapa tiene huéspedes

                # El objeto del organismo al cual esta etapa pertenece
                obj_org_inf = símismo.organismos[etp['org']]

                # Para cada organismo que infecta esta etapa
                for org_hués, d_org_hués in dic_hués.items():

                    # Una referencia al objeto del organismo hospedero
                    obj_org_hués = símismo.organismos[org_hués]

                    # El índice de la primera y la última etapa del huésped que pueden tener la infección
                    n_prim = min([símismo.núms_etapas[org_hués][x] for x in d_org_hués['entra']])
                    n_sale = símismo.núms_etapas[org_hués][d_org_hués['sale']]

                    # Una lista con todas las etapas del huésped que pueden tener la infección.
                    l_etps_hués = [x for x in símismo.organismos[org_hués].etapas[n_prim: n_sale + 1]]

                    # La segunda etapa existentes del organismo que infecta (los individuos infectados terminarán por
                    # transicionar a la esta etapa).
                    nombre_etp_recip = obj_org_inf.etapas[1]
                    n_recip = símismo.núms_etapas[org_hués][nombre_etp_recip]  # Su posición absoluta en la Red

                    # Crear las etapas fantasmas para las etapas infectadas del huésped
                    for n_etp_hués, etp_hués in enumerate(l_etps_hués):

                        # El índice de la etapa fantasma
                        n_etp_fant = len(símismo.etapas) - 1

                        # Crear un diccionario para la etapa fantasma. Queremos la misma estructura de diccionario que
                        # la etapa original del huésped; tiene que ser un diccionario distinto pero con referencias
                        # a los mismos objetos de matrices o variables PyMC (para coefs).
                        dic = copiar_dic_refs(obj_org_hués.receta['estr']['etapas'][etp_hués])
                        dic['nombre'] = '%s infectando a %s_%s' % (etp['org'], org_hués, etp_hués)
                        dic['pos'] = 0  # No hay posición relativa para etapas fantasmas

                        if n_etp_hués <= len(l_etps_hués):
                            n_trans = n_etp_fant + 1
                        else:
                            n_trans = n_recip

                        dic['trans'] = n_trans

                        # La configuración de la etapa fantasma es la misma que la de su etapa pariente
                        conf = obj_org_hués.config[etp_hués]

                        # Copiamos el diccionario de coeficientes, pero con referencias a los objetos de distrubuciones
                        # (Comparten los mismos variables).

                        coefs = copiar_dic_refs(obj_org_hués.receta['coefs'][etp_hués])

                        dic_etp = dict(org=etp['org'],
                                       nombre=dic['nombre'],
                                       dic=dic,
                                       conf=conf,
                                       coefs=coefs)

                        símismo.etapas.append(dic_etp)

                        símismo.fantasmas[n_etp_hués].append(n_etp_fant)

        # Crear el diccionario de los tipos de las ecuaciones activas para cada etapa.
        símismo.ecs.clear()  # Borrar todo en el diccionario existente para evitar posibilidades de cosas raras

        for categ in Ec.ecs_orgs:
            # Para cada tipo de ecuación posible...

            # Crear la llave correspondiente en el diccionario de tipos de ecuaciones de la red.
            símismo.ecs[categ] = {}

            # Para cada subcategoría de ecuación posible...
            for sub_categ in Ec.ecs_orgs[categ]:

                # Crear una lista
                símismo.ecs[categ][sub_categ] = []

                # Para cada etapa de esta red...
                for d_etp in símismo.etapas:
                    # Leer el tipo de ecuación activo para esta simulación
                    tipo_ec = d_etp['dic']['ecs'][categ][sub_categ]

                    # Guardar el tipo de ecuación en su lugar en símismo.ecs
                    símismo.ecs[categ][sub_categ].append(tipo_ec)

        # Guardar el orden de transiciones y de reproducciones
        símismo.orden['trans'] = np.empty(len(símismo.etapas))
        símismo.orden['repr'] = np.empty(len(símismo.etapas))

        for nombre_org, org in símismo.núms_etapas.items():
            # Para cada organismo...

            # Encontrar el índice de la primera etapa del organismo
            n_etp_mín = min(org.values())

            for etp, n_etp in org:
                # Para cada etapa del organismo...

                # Buscar el diccionario de la etapa
                d_etp = símismo.etapas[n_etp]['dic']

                # Ajustar el número de la etapas a la cual esta etapa transiciona o se reproduce
                símismo.orden['trans'][n_etp] = d_etp['trans'] + n_etp_mín
                símismo.orden['repr'][n_etp] = d_etp['repr'] + n_etp_mín

        # Guardar el orden de transiciones y de reproducciones para etapas fantasmas
        for n_etp in range(n_etps_reg, len(símismo.etapas)):
            símismo.orden['trans'][n_etp] = símismo.etapas[n_etp]['dic']['trans']
            símismo.orden['repr'][n_etp] = símismo.etapas[n_etp]['dic']['repr']

        # Para hacer: usar las ecuaciones de transiciones de agentes infectuosos.

        # La red ya está lista para simular
        símismo.listo = True

    def dibujar(símismo, mostrar=True, archivo='', exper=None):
        """
        Ver la documentación de Simulable.

        :type mostrar: bool
        :type archivo: str
        :type exper: list

        """

        # El diccionario de información a poner en el título del gráfico
        dic_título = {'exp': None, 'prc': None, 'org': None, 'etp': None}

        # Si no se especificó experimento, tomar todos los experimentos de la validación o calibración la más recién.
        if exper is None:
            exper = list(símismo.predics_exps.keys())

        # Asegurar el formato correcto para 'exper'.
        if type(exper) is str:
            exper = [exper]

        # Para cada experimento...
        for exp in exper:
            dic_título['exp'] = exp

            dic_preds_obs = símismo._sacar_vecs_preds_obs(exp=exp)

            # Para cada organismo en la red...
            for org, d_org in dic_preds_obs.items():
                dic_título['org'] = org

                # Para cada etapa de este organismo...
                for etp, n_etp in d_org.items():
                    dic_título['etp'] = etp

                    # El vector de observaciones y la matriz de predicciones.
                    matr_predic = dic_preds_obs[org][etp]['preds']  # Eje 0: parcela, 1: rep estoc, 2: rep parám, 3: día
                    vector_obs = dic_preds_obs[org][etp]['obs']  # Eje 0: parcela, eje 2: día

                    # Para cada parcela en las predicciones...
                    for n_p in range(matr_predic.shape[0]):

                        # Las matrices de predicciones y observaciones de poblaciones, con una única parcela
                        matr_predic_prc = matr_predic[n_p, :, :]
                        if vector_obs is None:
                            vector_obs_prc = None
                        else:
                            vector_obs_prc = vector_obs[n_p, :]

                        # El archivo para guardar la imagen
                        archivo_img = os.path.join(archivo, '{exp}_{prc}_{org}_{etp}'.format(**dic_título))

                        # Generar el titulo del gráfico. Incluir el nombre de la parcela, si necesario:
                        if len(símismo.info_exps['parcelas'][exp]) > 1:
                            dic_título['prc'] = símismo.info_exps['parcelas'][exp][n_p]
                            título = '{exp}, Parcela {prc}: {org}, etapa {etp}'.format(**dic_título)
                        else:
                            título = '{exp}: {org}, etapa {etp}'.format(**dic_título)

                            # Generar el gráfico
                        gráfico(matr_predic=matr_predic_prc, vector_obs=vector_obs_prc,
                                título=título,
                                etiq_y='Población', mostrar=mostrar, archivo=archivo_img)

    def _calc_depred(símismo, pobs, extrn, paso):
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

                Usamos una forma matemáticamente equivalente a la en el artículo, y que facilita el establecimiento de
                  distribuciones a prioris para los parámetros:
                y = a*P / (b + P + c*D)

            Hassell-Varley:
                M.P. Hassell, G.C. Varley. New inductive population model for insect parasites and its bearing on
                    biological control. Nature, 223 (1969), pp. 1133–1136

                P en las respuestas funcionales arriba cambia a P/(D^m)

            Kovai (Asíntota doble):
                y = (a * P/D) / (P/D + c) * (P^2 / (P^2 +b), simplificado a
                  y = a * P^3 / (P^3 + D*c*(b + P^2) + b*P).
                Con la suposición que c = a / 2, tenemos entonces
                  y = P^3 / ( (P^3 + b*P)/a + D/2*(b + P^2) ).

        :param pobs: matriz numpy de poblaciones actuales.
        :type pobs: np.ndarray
        
        :param extrn: Un diccionario con datos externos
        :type extrn: dict

        :param paso: El paso de tiempo de la simulación.
        :type paso: int

        """

        # Calcular cuántas presas cada especie de depredador podría comerse

        # A este punto, depred representa la depredación potencial per cápita de depredador
        depred = símismo.predics['Depredación']
        tipos_ec = símismo.ecs['Depredación']['Ecuación']

        # La lista de los coeficientes de cada etapa para la depredación
        coefs = numerizar(símismo.coefs_act['Depredación']['Ecuación'])

        # Densidades de poblaciones
        dens = np.divide(pobs, extrn['superficies'].reshape(pobs.shape[0], 1, 1, 1))

        for n in range(len(símismo.etapas)):  # Para cada etapa...

            # Los coeficientes para esta etapa
            cf = coefs[n]
            # Los tipos de ecuaciones para esta etapa
            tipo_ec = tipos_ec[n]

            # Una referencia a la parte de la matriz que representa la depredación por esta etapa
            depred_etp = depred[:, :, :, n, :]

            # Calcular la depredación según la ecuación de esta etapa.
            if tipo_ec == 'Nada':
                # Si no hay ecuación para la depredación del organismo (si ni tiene presas), seguir a la próxima etapa
                # de una vez.
                continue

            elif tipo_ec == 'Tipo I_Dependiente presa':
                # Depredación de respuesta funcional tipo I con dependencia en la población de la presa.
                np.multiply(pobs, cf['a'], out=depred_etp)

            elif tipo_ec == 'Tipo II_Dependiente presa':
                # Depredación de respuesta funcional tipo II con dependencia en la población de la presa.
                np.multiply(dens, cf['a'] / (dens + cf['b']), out=depred_etp)

            elif tipo_ec == 'Tipo III_Dependiente presa':
                # Depredación de respuesta funcional tipo III con dependencia en la población de la presa.
                np.multiply(np.square(dens), cf['a'] / (np.square(dens) + cf['b']), out=depred_etp)

            elif tipo_ec == 'Tipo I_Dependiente ratio':
                # Depredación de respuesta funcional tipo I con dependencia en el ratio de presa a depredador.
                dens_depred = dens[:, :, :, n]  # La población de esta etapa
                np.multiply(dens / dens_depred, cf['a'], out=depred_etp)

            elif tipo_ec == 'Tipo II_Dependiente ratio':
                # Depredación de respuesta funcional tipo II con dependencia en el ratio de presa a depredador.
                dens_depred = dens[:, :, :, n]  # La población de esta etapa
                np.multiply(dens / dens_depred, cf['a'] / (dens / dens[n] + cf['b']), out=depred_etp)

            elif tipo_ec == 'Tipo III_Dependiente ratio':
                # Depredación de respuesta funcional tipo III con dependencia en el ratio de presa a depredador.
                dens_depred = dens[:, :, :, n]  # La población de esta etapa
                np.multiply(np.square(dens / dens_depred), cf['a'] / (np.square(dens / dens_depred) + cf['b']),
                            out=depred_etp)

            elif tipo_ec == 'Beddington-DeAngelis':
                # Depredación de respuesta funcional Beddington-DeAngelis. Incluye dependencia en el depredador.
                dens_depred = dens[:, :, :, n]  # La población de esta etapa
                np.multiply(dens, cf['a'] / (cf['b'] + dens + cf['c'] * dens_depred), out=depred_etp)

            elif tipo_ec == 'Tipo I_Hassell-Varley':
                # Depredación de respuesta funcional Tipo I con dependencia Hassell-Varley.
                dens_depred = dens[:, :, :, n]  # La población de esta etapa
                np.multiply(dens / dens_depred ** cf['m'], cf['a'], out=depred_etp)

            elif tipo_ec == 'Tipo II_Hassell-Varley':
                # Depredación de respuesta funcional Tipo II con dependencia Hassell-Varley.
                dens_depred = dens[:, :, :, n]  # La población de esta etapa
                np.multiply(dens / dens_depred ** cf['m'], cf['a'] / (dens / dens_depred ** cf['m'] + cf['b']),
                            out=depred_etp)

            elif tipo_ec == 'Tipo III_Hassell-Varley':
                # Depredación de respuesta funcional Tipo III con dependencia Hassell-Varley.
                dens_depred = dens[:, :, :, n]  # La población de esta etapa
                np.multiply(dens / dens_depred ** cf['m'], cf['a'] / (dens / dens_depred ** cf['m'] + cf['b']),
                            out=depred_etp)

            elif tipo_ec == 'Kovai':
                # Depredación de respuesta funcional de asíntota doble (ecuación Kovai).
                dens_depred = dens[:, :, :, n]  # La población de esta etapa (depredador)

                np.divide(np.power(dens, 3),
                          np.add(np.divide(np.add(np.power(dens, 3),
                                                  np.multiply(dens, cf['b'])
                                                  ),
                                           cf['a']),
                                 np.multiply(np.add(np.square(dens), cf['b']),
                                             np.divide(dens_depred, 2)[..., np.newaxis]
                                             )
                                 ),
                          out=depred_etp)

                # Ajustar por la presencia de múltiples presas
                símismo.probs_conj(depred_etp, cf['a'], eje=3)

            else:
                # Si el tipo de ecuación no estaba definida arriba, hay un error.
                raise ValueError('Tipo de ecuación "%s" no reconodico para cálculos de depradación.' % tipo_ec)

        # Reemplazar valores NaN con 0.
        depred[np.isnan(depred)] = 0

        # Convertir depredación potencial por depredador a depredación potencial total (multiplicar por la población
        # de cada depredador). También multiplicamos por el paso de la simulación. 'depred' ahora está en unidades
        # del número total de presas comidas por cada tipo de depredador por unidad de tiempo.
        np.multiply(depred, np.multiply(pobs, paso)[..., np.newaxis], out=depred)

        # Ajustar por la presencia de varios depredadores
        símismo.probs_conj(depred, máx=pobs[..., np.newaxis], eje=3)

        depred[np.isnan(depred)] = 0

        # Redondear (para evitar de comer, por ejemplo, 2 * 10^-5 moscas)
        redondear(depred)

        # Depredación únicamente por presa (todos los depredadores juntos)
        depred_por_presa = np.sum(depred, axis=3)

        # Si la etapa usa cohortes para cualquier otro cálculo, actualizar los cohortes ahora.
        for n, coh in símismo.predics['Cohortes'].items():

            if n in símismo.fantasmas:
                # Si la etapa tiene etapas fantasmas, hacer las transiciones apropiadas a cada etapa fantasma
                for n_fant in símismo.fantasmas[n]:
                    recip = símismo.predics['Cohortes'][n_fant]
                    nombre_org_depr = símismo.etapas[n_fant]['org']
                    nombre_etp_depr = símismo.organismos[nombre_org_depr].etapas[-1]['nombre']
                    n_depr = símismo.núms_etapas[nombre_org_depr, nombre_etp_depr]
                    quitar_de_cohorte(coh, depred[..., n, n_depr], recip=recip)
            else:
                quitar_de_cohorte(coh, depred_por_presa[..., n])

        # Actualizar la matriz de poblaciones
        np.add(pobs, -depred_por_presa, out=pobs)

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
            crec_etp = crec[:, :, :, n]  # Vinculo con la parte de la matriz "crec" de esta etapa.

            # Modificaciones ambientales a la taza de crecimiento intrínsica
            if modifs[n] == 'Nada':
                # Si no hay crecimiento para este insecto, no hacer nada. Notar que si no quieres
                # modificación ambiental a r, pero sí quieres crecimiento, hay que escoger la modificación ambiental
                # 'Ninguna' y NO 'None'. Esto permetirá crear la variable 'r' que se necesitará después.
                pass

            elif modifs[n] == 'Ninguna':
                # Sin modificación a r.
                r = np.multiply(cf['r'], paso)

            elif modifs[n] == 'Log Normal Temperatura':
                # r responde a la temperatura con una ecuación log normal.
                r = cf['r'] * paso
                r *= mat.exp(-0.5 * (mat.log(extrn['temp_máx'] / cf['t']) / cf['p']) ** 2)

            else:
                raise ValueError

            # Calcular el crecimiento de la población

            pob_etp = pobs[:, :, :, n]  # La población de esta etapa
            cf = coefs_ec[n]

            if tipos_ec[n] == 'Exponencial':
                # Crecimiento exponencial

                np.multiply(pob_etp, r, out=crec_etp)

            elif tipos_ec[n] == 'Logístico':
                # Crecimiento logístico.

                np.multiply(r, pob_etp * (1 - pob_etp / cf['K']), out=crec_etp)  # Ecuación logística sencilla

            elif tipos_ec[n] == 'Logístico Presa':
                # Crecimiento logístico. 'K' es un parámetro repetido para cada presa de la etapa y indica
                # la contribución individual de cada presa a la capacidad de carga de esta etapa (el depredador).

                k = np.nansum(np.multiply(pobs, cf['K']))  # Calcular la capacidad de carga
                np.multiply(r, pob_etp * (1 - pob_etp / k), out=crec_etp)  # Ecuación logística sencilla

                # Evitar péridadas de poblaciones superiores a la población.
                np.maximum(crec_etp, -pob_etp, out=crec_etp)

            elif tipos_ec[n] == 'Depredación':
                # Crecimiento proporcional a la cantidad de presas que se consumió el depredador.
                # para hacer: implementar
                raise NotImplementedError

            elif tipos_ec[n] == 'Externo Cultivo':
                # Esta ecuación guarda la población del organismo a un nivel constante, no importe qué esté pasando
                # en el resto de la red. Puede ser util para representar plantas donde los herbívoros están bien
                # abajo de sus capacidades de carga.
                nueva_pob = símismo.plantas['dic'][n][símismo.plantas['n_etp'][n]]
                np.subtract(nueva_pob, pob_etp, out=crec_etp)

            else:
                raise ValueError('Ecuación de crecimiento "%s" no reconocida.' % tipos_ec[n])

        crec[np.isnan(crec)] = 0

        redondear(crec)

        # Actualizar la matriz de poblaciones
        np.add(pobs, crec, out=pobs)

    def _calc_reprod(símismo, pobs, extrn, paso):
        """

        :param pobs:
        :type pobs: np.ndarray
        :param extrn:
        :type extrn:
        :param paso:
        :type paso:
        :return:
        :rtype:
        """

        # Simplificamos el código un poco.
        reprs = símismo.predics['Reproducción']

        ec_edad = símismo.ecs['Reproducción']['Edad']
        probs = símismo.ecs['Reproducción']['Prob']

        coefs_ed = símismo.coefs_act['Reproducción']['Edad']
        coefs_pr = símismo.coefs_act['Reproducción']['Prob']

        for n, ec_ed in enumerate(ec_edad):

            # Si no hay cálculos de reproducción para esta etapa, sigamos a la próxima etapa de una vez. Esto se
            # detecta por etapas que tienen 'Nada' como ecuación de densidad (probabilidad) de reproducción.
            if probs[n] == 'Nada':
                continue

            # Una referencia a la parte apriopiada de la matriz de reproducciones
            n_recip = símismo.orden['trans'][n]
            repr_etp_recip = reprs[..., n_recip]

            # Si hay que guardar cuenta de cohortes, hacerlo aquí
            cf_ed = coefs_ed[n]

            if ec_ed == 'Nada':
                edad_extra = None

            elif ec_ed == 'Días':
                # Edad calculada en días.
                edad_extra = paso

            elif ec_ed == 'Días Grados':
                # Edad calculada por días grados.
                edad_extra = días_grados(extrn['temp_máx'], extrn['temp_mín'],
                                         umbrales=(cf_ed['mín'], cf_ed['máx'])
                                         ) * paso

            elif ec_ed == 'Brière Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura Briere. En esta ecuación,
                # tal como en las otras con taza de desarrollo, quitamos el parámetro típicamente multiplicado por
                # toda la ecuación, porque eso duplicaría el propósito del parámetro de ubicación de las distribuciones
                # de probabilidad empleadas después.
                #
                # Mokhtar, Abrul Monim y Salem Saif al Nabhani. 2010. Temperature-dependent development of dubas bug,
                #   Ommatissus lybicus (Hemiptera: Tropiduchidae), an endemic pest of date palm, Phoenix dactylifera.
                #   Eur. J. Entomol. 107: 681–685
                edad_extra = extrn['temp_prom'] * (extrn['temp_prom'] - cf_ed['t_dev_mín']) * \
                             mat.sqrt(cf_ed['t_letal'] - extrn['temp_prom'])

            elif ec_ed == 'Brière No Linear Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura no linear de Briere.
                #
                # Youngsoo Son et al. 2012. Estimation of developmental parameters for adult emergence of Gonatocerus
                #   morgani, a novel egg parasitoid of the glassy-winged sharpshooter, and development of a degree-day
                #   model. Biological Control 60(3): 233-260.

                edad_extra = extrn['temp_prom'] * (extrn['temp_prom'] - cf_ed['t_dev_mín']) * \
                             mat.pow(cf_ed['t_letal'] - extrn['temp_prom'], 1 / cf_ed['m'])

            elif ec_ed == 'Logan Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura Logan:
                #
                # Youngsoo Son y Lewis, Edwin E. 2005. Modelling temperature-dependent development and survival of
                #   Otiorhynchus sulcatus (Coleoptera: Curculionidae). Agricultural and Forest Entomology 7(3): 201–209.

                edad_extra = mat.exp(cf_ed['rho'] * extrn['temp_prom']) - \
                             mat.exp(cf_ed['rho'] * cf_ed['t_letal'] - (cf_ed['t_letal'] -
                                                                        extrn['temp_prom'])
                                     / cf_ed['delta'])

            else:
                raise ValueError('No reconozco el tipo de ecuación %s para la edad de transiciones.' % ec_ed)

            # Y ya pasamos a calcular el número de individuos de esta etapa que se reproducen en este paso de tiempo
            cf = coefs_pr[n]
            if probs[n] == 'Constante':
                # Reproducciones en proporción al tamaño de la población.

                # Tomamos el paso en cuenta según las regals de probabilidad:
                #   p(x sucede n veces) = (1 - (1- p(x))^n)

                np.multiply(cf['n'] * pobs, (1 - (1 - cf['q']) ** paso), out=repr_etp_recip)

            elif probs[n] == 'Depredación':
                # Reproducciones en función de la depredación (útil para avispas esfécidas)
                depred = símismo.predics['Depredación'][..., n, :]

                np.sum(np.multiply(cf['n'], depred), axis=-1, out=repr_etp_recip)

            else:
                # Aquí tenemos todas las probabilidades de reproducción dependientes en distribuciones de cohortes:
                edad_extra *= paso

                cohortes = símismo.predics['Cohortes'][n_recip]['Pobs']
                edades = símismo.predics['Cohortes'][n_recip]['Edades']['repr']

                if edad_extra is None:
                    raise ValueError('Se debe usar una ecuación de edad para poder usar distribuciones de cohortes'
                                     'en el cálculo de reproducciones.')

                try:
                    np.multiply(cf['n'], trans_cohorte(pobs=cohortes, edades=edades, cambio=edad_extra,
                                                       tipo_dist=probs[n], paráms_dist=cf, quitar=False),
                                out=repr_etp_recip)

                except ValueError:
                    raise ValueError('Error en el tipo de distribución de probabilidad para reproducciones.')

        # Redondear las reproducciones calculadas
        redondear(reprs)

        # Si la fase que recibe las reproducciones también tiene cohortes, actualizarlos aquí
        for n_recip, coh in símismo.predics['Cohortes'].items():
            añadir_a_cohorte(coh, reprs[..., n_recip])

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

        # Simplificamos el código un poco.

        muertes = símismo.predics['Muertes']
        tipos_ec = símismo.ecs['Muertes']['Ecuación']
        coefs = símismo.coefs_act['Muertes']['Ecuación']

        for n, ec in enumerate(tipos_ec):

            cf = coefs[n]
            muerte_etp = muertes[:, :, :, n]

            if ec == 'Nada':
                continue

            elif ec == 'Constante':
                # Muertes en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
                # exponencial.

                np.multiply(pobs, cf['q'], out=muerte_etp)

            elif ec == 'Log Normal Temperatura':
                # Muertes dependientes en la temperatura, calculadas con la ecuación mencionada en:
                #
                # Sunghoon Baek, Youngsoo Son, Yong-Lak Park. 2014. Temperature-dependent development and survival of
                #   Podisus maculiventris (Hemiptera: Pentatomidae): implications for mass rearing and biological
                #   control. Journal of Pest Science 87(2): 331-340.

                sobrevivencia = mat.exp(-0.5 * (mat.log(extrn['temp_máx'] / cf['t']) / cf['p']) ** 2)
                np.multiply(pobs, (1 - sobrevivencia), out=muerte_etp)

            elif ec == 'Asimptótico Humedad':

                # M. P. Lepage, G. Bourgeois, J. Brodeur, G. Boivin. 2012. Effect of Soil Temperature and Moisture on
                #   Survival of Eggs and First-Instar Larvae of Delia radicum. Environmental Entomology 41(1): 159-165.

                sobrevivencia = max(0, 1 - mat.exp(-cf['a'] * (extrn['humedad'] - cf['b'])))
                np.multiply(pobs, (1 - sobrevivencia), out=muerte_etp)

            elif ec == 'Sigmoidal Temperatura':

                sobrevivencia = 1 / (1 + mat.exp((extrn['temp_máx'] - cf['a']) / cf['b']))
                np.multiply(pobs, (1 - sobrevivencia), out=muerte_etp)

            else:
                raise ValueError

        np.multiply(muertes, paso, out=muertes)
        redondear(muertes)

        # Si la etapa usa cohortes para cualquier otro cálculo, actualizar los cohortes ahora.
        for n in símismo.predics['Cohortes']:
            quitar_de_cohorte(símismo.predics['Cohortes'][n], muertes[..., n])

        # Actualizar la matriz de predicciones
        np.subtract(pobs, muertes, out=pobs)

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

        # Simplificamos el código un poco.
        trans = símismo.predics['Transiciones']

        ec_edad = símismo.ecs['Transiciones']['Edad']
        probs = símismo.ecs['Transiciones']['Prob']

        coefs_ed = símismo.coefs_act['Transiciones']['Edad']
        coefs_pr = símismo.coefs_act['Transiciones']['Prob']

        cohortes = símismo.predics['Cohortes']['trans']

        for n, ec_ed in enumerate(ec_edad):

            # Si no hay cálculos de transiciones para esta etapa, sigamos a la próxima etapa de una vez. Esto se
            # detecta por etapas que tienen 'Nada' como ecuación de probabilidad de transición.
            if probs[n] == 'Nada':
                continue

            # Una referencia a la parte apriopiada de la matriz de transiciones
            trans_etp = trans[..., n]

            # Si hay que guardar cuenta de cohortes, hacerlo aquí
            cf_ed = coefs_ed[n]

            if ec_ed == 'Nada':
                edad_extra = None

            elif ec_ed == 'Días':
                # Edad calculada en días.
                edad_extra = paso

            elif ec_ed == 'Días Grados':
                # Edad calculada por días grados.
                edad_extra = días_grados(extrn['temp_máx'], extrn['temp_mín'],
                                         umbrales=(cf_ed['mín'], cf_ed['máx'])
                                         ) * paso

            elif ec_ed == 'Brière Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura Briere. En esta ecuación,
                # tal como en las otras con taza de desarrollo, quitamos el parámetro típicamente multiplicado por
                # toda la ecuación, porque eso duplicaría el propósito del parámetro de ubicación de las distribuciones
                # de probabilidad empleadas después.
                #
                # Mokhtar, Abrul Monim y Salem Saif al Nabhani. 2010. Temperature-dependent development of dubas bug,
                #   Ommatissus lybicus (Hemiptera: Tropiduchidae), an endemic pest of date palm, Phoenix dactylifera.
                #   Eur. J. Entomol. 107: 681–685
                edad_extra = extrn['temp_prom'] * (extrn['temp_prom'] - cf_ed['t_dev_mín']) * \
                             mat.sqrt(cf_ed['t_letal'] - extrn['temp_prom'])

            elif ec_ed == 'Brière No Linear Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura no linear de Briere.
                #
                # Youngsoo Son et al. 2012. Estimation of developmental parameters for adult emergence of Gonatocerus
                #   morgani, a novel egg parasitoid of the glassy-winged sharpshooter, and development of a degree-day
                #   model. Biological Control 60(3): 233-260.

                edad_extra = extrn['temp_prom'] * (extrn['temp_prom'] - cf_ed['t_dev_mín']) * \
                             mat.pow(cf_ed['t_letal'] - extrn['temp_prom'], 1 / cf_ed['m'])

            elif ec_ed == 'Logan Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura Logan:
                #
                # Youngsoo Son y Lewis, Edwin E. 2005. Modelling temperature-dependent development and survival of
                #   Otiorhynchus sulcatus (Coleoptera: Curculionidae). Agricultural and Forest Entomology 7(3): 201–209.

                edad_extra = mat.exp(cf_ed['rho'] * extrn['temp_prom']) - \
                             mat.exp(cf_ed['rho'] * cf_ed['t_letal'] - (cf_ed['t_letal'] -
                                                                        extrn['temp_prom'])
                                     / cf_ed['delta'])

            else:
                raise ValueError('No reconozco el tipo de ecuación %s para la edad de transiciones.' % ec_ed)

            # Y ya pasamos a calcular el número de individuos de esta etapa que se transicionan en este paso de tiempo
            cf = coefs_pr[n]
            if probs[n] == 'Constante':
                # Transiciones en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
                # exponencial.

                # Tomamos el paso en cuenta según las regals de probabilidad:
                #   p(x sucede n veces) = (1 - (1- p(x))^n)

                np.copyto(trans_etp, pobs * (1 - (1 - cf['q']) ** paso))

                # Si la etapa usa cohortes para cualquier otro cálculo (transiciones a parte), actualizar los
                # cohortes ahora.
                if n in cohortes:
                    quitar_de_cohorte(cohortes[n], trans_etp)

            else:
                # Aquí tenemos todas las probabilidades de muerte dependientes en distribuciones de cohortes:
                edad_extra *= paso

                pobs_coh = símismo.predics['Cohortes'][n]['Pobs']
                edades = símismo.predics['Cohortes'][n]['Edades']['Trans']

                if edad_extra is None:
                    raise ValueError('Se debe usar una ecuación de edad para poder usar distribuciones de cohortes'
                                     'en el cálculo de transiciones de inviduos.')

                try:
                    np.copyto(trans_etp, trans_cohorte(pobs=pobs_coh, edades=edades, cambio=edad_extra,
                                                       tipo_dist=probs[n], paráms_dist=cf))
                except ValueError:
                    raise ValueError('Error en el tipo de distribución de probabilidad para muertes naturales.')

        # Redondear las transiciones calculadas
        redondear(trans)

        # Quitar los organismos que transicionaron
        np.subtract(pobs, trans, out=pobs)

        # Si no eran adultos muríendose por viejez, añadirlos a la próxima etapa también
        for n_don, n_recip in enumerate(símismo.orden['trans']):
            if n_recip >= 0:
                np.add(pobs[..., n_recip], trans[..., n_don], out=pobs[..., n_recip])

                # Si la próxima fase también tiene cohortes, añadirlo aquí
                if n_recip in símismo.predics['Cohortes']:
                    añadir_a_cohorte(cohortes[n_recip], trans[..., n_don])

    def _calc_mov(símismo, pobs, paso, extrn):
        """
        Calcula la imigración y emigración de organismos entre parcelas

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
        for n in símismo.predics['Cohortes']:
            añadir_a_cohorte(símismo.predics['Cohortes'][n], mov[..., n])

        # Actualizar la matriz de predicciones
        pobs += mov

    def _limpiar_cohortes(símismo):
        for n, etp in enumerate(símismo.predics['Cohortes']):
            vacíos = (etp['Pobs'] == 0)
            for ed in etp['Edades'].values():
                ed[vacíos] = np.nan

    def incrementar(símismo, paso, i, mov=False, extrn=None):

        # Empezar con las poblaciones del paso anterior
        símismo.predics['Pobs'][..., i] = símismo.predics['Pobs'][..., i - 1]
        pobs = símismo.predics['Pobs'][..., i]

        # Calcular la depredación, crecimiento, reproducción, muertes, transiciones, y movimiento entre parcelas

        # Una especie que mata a otra.
        símismo._calc_depred(pobs=pobs, paso=paso, extrn=extrn)

        # Una población que crece (misma etapa)
        símismo._calc_crec(pobs=pobs, extrn=extrn, paso=paso)

        # Una etapa que crear más individuos de otra etapa
        # para hacer: símismo._calc_reprod(pobs=pobs, extrn=extrn, paso=paso)

        # Muertes por el ambiente
        símismo._calc_muertes(pobs=pobs, extrn=extrn, paso=paso)

        # Una etapa que cambia a otra, o que se muere por su edad.
        símismo._calc_trans(pobs=pobs, extrn=extrn, paso=paso)

        if mov:
            # Movimientos de organismos de una parcela a otra.
            símismo._calc_mov(pobs=pobs, extrn=extrn, paso=paso)

        # Ruido aleatorio; Para hacer: formalizar el proceso de agregación de ruido aleatorio
        _agregar_ruido(pobs=pobs, ruido=0.01)

        # Limpiar los cohortes de los organismos de la Red.
        símismo._limpiar_cohortes()

    def _procesar_validación(símismo):
        """
        Ver documentación de Simulable.
        Esta función valida las predicciones de una corrida de validación.

        :return: Un diccionario, organizado por experimento, organismo y etapa, del ajuste del modelo.
        :rtype: dict

        """

        valids_detalles = {}

        matr_preds_total = None
        vector_obs_total = None

        # Para cada experimento simulado, en orden...
        for exp, predic in sorted(símismo.predics_exps.items()):
            valids_detalles[exp] = {}

            dic_pred_obs = símismo._sacar_vecs_preds_obs(exp=exp)

            for org, d_org in dic_pred_obs.items():

                valids_detalles[exp][org] = {}

                for etp, d_etp in d_org.items():
                    valids_detalles[exp][org][etp] = {}
                    d = dic_pred_obs[org][etp]

                    if d['obs'] is not None:

                        for n_p, parc in enumerate(símismo.info_exps['parcelas'][exp]):
                            matr_predic = d['preds'][n_p, ...]
                            vector_obs = d['obs'][n_p, ...]
                            valids_detalles[exp][org][etp][parc] = validar(matr_predic=matr_predic,
                                                                           vector_obs=vector_obs)
                            if matr_preds_total is None:
                                matr_preds_total = matr_predic
                                vector_obs_total = vector_obs
                            else:
                                matr_preds_total = np.append(matr_preds_total, matr_predic, axis=-1)
                                vector_obs_total = np.append(vector_obs_total, vector_obs, axis=-1)

        valid = validar(matr_predic=matr_preds_total, vector_obs=vector_obs_total)

        return valid, valids_detalles

    def _sacar_vecs_preds_obs(símismo, exp):
        """
        Esta función crea un diccionario con vectores/matrices de predicciones y de observaciones. Es muy útil para
          generar gráficos de una validación y para generar índices de ajustes de modelos desagregados por componente.

        :param exp: El nombre del experimento para cual hay que sacar los vectores.
        :type exp: str

        :return: Un diccionario de la forma:
          {organismo 1: {etapa 1:{'preds': [matriz], 'obs': [vector]}, etapa 2: {...}, ...}, organismo 2: {...}, ...}
          Notar que la matriz de predicciones tendrá 3 ejes: eje 0: parcela, eje 1: repetición estocástica,
           eje 2: repeticiones paramétricas, eje 3: día.
          En casos donde hay observaciones que faltan para unos días para cuales hay predicciones, el vector de
           observaciones tendrá valores de np.nan para los días que faltan. Si una etapa no tienen observaciones,
           el vector de observaciones se reeplazará por None.
        :rtype: dict

        """

        # El diccionario para guardar los vectores de predicciones y de observaciones
        dic_vecs = {}

        # Para simplificar el código
        matr_predics = símismo.predics_exps[exp]['Pobs']
        etps_interés = símismo.info_exps['etps_interés'][exp]
        combin_etps = símismo.info_exps['combin_etps'][exp]

        # Primero, vamos a sacar vectores para cada etapa de la red
        for org, d_org in símismo.núms_etapas.items():

            # Si el organismo no existe en el diccionario de resultados, agregarlo ahora
            if org not in dic_vecs.keys():
                dic_vecs[org] = {}

            for etp in d_org:  # Para cada etapa...

                # Crear los lugares para guardar sus predicciones y observaciones.
                dic_vecs[org][etp] = {'obs': None, 'preds': None}

                n_etp = símismo.núms_etapas[org][etp]  # El número de la etapa

                # Guardar la matriz de predicciones. Eje 0: parcela, 1: rep estoc, 2. rep param, 3: día
                matr_preds_etp = matr_predics[..., n_etp, :]
                if n_etp in símismo.fantasmas:
                    # Si la etapa está en las combinaciones automáticas de la red (etapas fantasmas)...

                    # Hacer las combinaciones necesarias antes de todo.
                    matr_preds_etp += np.sum([matr_predics[..., x, :] for x in símismo.fantasmas[n_etp]], axis=3)

                dic_vecs[org][etp]['preds'] = matr_preds_etp

                # El diccionario de observaciones y de tiempos del Experimento
                dic_obs = símismo.exps[exp].datos['Organismos']['obs']
                tiempos_obs = símismo.exps[exp].datos['Organismos']['tiempo']

                # Ahora, el vector de observaciones. (Es un poco más complicado.)
                if n_etp in etps_interés:
                    # Si hay observaciones para esta etapa...

                    # Los nombre de las columnas y el nombre de la columna de datos que nos interesa
                    nombres_cols = símismo.info_exps['nombres_cols'][exp]
                    nombre_col = nombres_cols[np.where(etps_interés == n_etp)[0]]

                    if n_etp not in combin_etps:
                        # Si la etapa no tiene otras etapas con las cuales combinarse...
                        # El vector para guardar las observaciones, llenado de valores np.nan. Eje 0: parcela, 1: día
                        vector_obs = np.empty((matr_preds_etp.shape[0], matr_preds_etp.shape[3]))
                        vector_obs.fill(np.nan)

                        # Llenar las posiciones en vector_obs que corresponden con los tiempos de las observaciones
                        for n_p, p in enumerate(símismo.info_exps['parcelas'][exp]):
                            vector_obs[n_p, tiempos_obs] = dic_obs[nombre_col][n_p, :]

                        # Guardar el vector
                        dic_vecs[org][etp]['obs'] = vector_obs

                    else:
                        # Si la etapa se combina con otras etapas en las observaciones...

                        # El nombre de esta "etapa" combinada, para guardar los resultados en el diccionario
                        nombre_serie = '% combinada' % etp

                        # La matriz de predicciones
                        matr_preds_etp = matr_preds_etp + np.sum([matr_predics[..., x, :]
                                                                  for x in combin_etps[n_etp]], axis=3)

                        # El vector para guardar las observaciones, llenado de valores np.nan. Eje 0: parcela, 1: día
                        vector_obs = np.empty((matr_preds_etp.shape[0], matr_preds_etp.shape[3]))
                        vector_obs.fill(np.nan)

                        # Llenar las posiciones en vector_obs que corresponden con los tiempos de las observaciones
                        for n_p, p in enumerate(símismo.info_exps['nombres_cols'][exp]):
                            vector_obs[n_p, tiempos_obs] = dic_obs[nombre_col][n_p, :]

                        # Guardar la matriz de predicciones
                        dic_vecs[org][nombre_serie]['preds'] = matr_preds_etp

                        # Guardar el vector de observaciones
                        dic_vecs[org][nombre_serie]['obs'] = vector_obs

        return dic_vecs

    def _sacar_líms_coefs_interno(símismo):
        """
        No hay nada nada que hacer aquí, visto que una red no tiene coeficientes propios. Devolvemos
          una lista vacía.
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

        Esta función llenará el diccionario símismo.formatos_exps, lo cuál contiene la información necesaria para
          conectar las predicciones de una Red con los datos observados en un Experimento. Este diccionario tiene
          cuatro partes:
            1. 'nombres_cols': Una lista de los nombres de las columnas de datos del Experimento, en orden.
            2. 'etps_interés': Una lista de los números de las etapas en la Red que corresponden as nombres_cols
            3. 'combin_etps': Un diccionario de las etapas cuyas predicciones hay que combinar. Tiene la forma
                general {n_etp: [n otras etapas], n_etp2: [], etc.},
                donde las llaves del diccionario son números enteros, no texto.
            4. 'ubic_obs': Un formato tuple con matrices con la información de dónde hay que sacar los datos de
                observaciones para cada día y cada etapa. Para hacer: cada parcela.

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

        # Crear las llaves para este experimento en el diccionario de formatos de la Red, y simplificar el código.
        símismo.info_exps['etps_interés'][nombre] = None
        símismo.info_exps['ubic_obs'][nombre] = ()
        l_nombres_cols = símismo.info_exps['nombres_cols'][nombre] = []
        d_comunes = símismo.info_exps['combin_etps'][nombre] = {}

        l_etps_interés = []

        # Para guardar las ubicaciones de las observaciones:
        ubic_obs_días = np.array([], dtype=int)
        ubic_obs_etps = np.array([], dtype=int)
        ubic_obs_parc = np.array([], dtype=int)

        # Para cada organismo en el diccionario de correspondencias, en orden...
        for org, d_org in sorted(corresp.items()):

            # Para cada etapa del organismo en el diccionario de correspondencias, en orden...
            for etp, d_etp in sorted(d_org.items()):

                l_cols = corresp[org][etp]  # La lista de columna(s) de datos correspondiendo a esta etapa

                # Asegurar el formato correcto
                if type(l_cols) is not list:
                    l_cols = [l_cols]

                # Si hay más que una columna de la base de datos correspondiendo a la etapa, hay que sumarlos. Este
                # código no hará ninguna transformación a los datos o el nombre de la columna en el caso que solamente
                # haya una columna de datos correspondiento a la etapa.

                # El nombre de la nueva columna sumada (en el caso donde l_cols tiene una sola columna, no cambia nada)
                nombre_col = '&'.join(str(x) for x in sorted(l_cols))

                # Hacer la suma (otra vez, no hace nada si l_cols solamente tiene una columna).
                suma = np.sum([experimento.datos['Organismos']['obs'][x] for x in l_cols], axis=0)

                # Guardar la nueva columna en el Experimento
                experimento.datos['Organismos']['obs'][nombre_col] = suma

                # El número de la etapa en la Red
                n_etp = símismo.núms_etapas[org][etp]

                # Verificar ahora para etapas cuyas predicciones hay que combinar
                if nombre_col in l_nombres_cols:
                    # Si ya había otra etapa con estos mismo datos...

                    # Buscar el número de la otra etapa
                    n_otra_etp = l_etps_interés[l_nombres_cols.index(nombre_col)]

                    # Si es la primera vez que la otra etapa se desdoble, agregar su número como llave al diccionario.
                    if n_otra_etp not in d_comunes:
                        d_comunes[n_otra_etp] = []

                    # Agregar el número de esta etapa a la lista.
                    d_comunes[n_otra_etp].append(n_etp)

                else:
                    # Si la columna ya no se utilizó para otra etapa...

                    # Guardar el nombre de la columna de interés, tanto como el número de la etapa
                    l_nombres_cols.append(nombre_col)
                    l_etps_interés.append(n_etp)

                    # Guardar las ubicaciones, en la matriz de predicciones, correspondiendo a las observaciones
                    obs_etp = experimento.datos['Organismos']['obs'][nombre_col]

                    for n_p in range(obs_etp.shape[0]):
                        obs_etp_parc = obs_etp[n_p, :]

                        # Días con observaciones
                        días_con_obs = experimento.datos['Organismos']['tiempo'][~np.isnan(obs_etp_parc.flatten())]
                        ubic_obs_días = np.concatenate((ubic_obs_días, días_con_obs))

                        # Guardar una matriz de forma correspondiente con el número de la etapa:
                        etps_con_obs = np.full(shape=len(días_con_obs), fill_value=n_etp, dtype=int)
                        ubic_obs_etps = np.concatenate((ubic_obs_etps, etps_con_obs))

                        # Y una matriz con los las parcelas con observaciones
                        parc_con_obs = np.full(shape=len(días_con_obs), fill_value=n_p, dtype=int)
                        ubic_obs_parc = np.concatenate((ubic_obs_parc, parc_con_obs))

        # Convertir a matrices numpy
        símismo.info_exps['etps_interés'][nombre] = np.array(l_etps_interés)
        símismo.info_exps['ubic_obs'][nombre] = (ubic_obs_parc, ubic_obs_etps, ubic_obs_días)

        # Agregar la lista de nombres de parcelas, en el orden que aparecen en las matrices de observaciones:
        símismo.info_exps['parcelas'][nombre] = experimento.datos['Organismos']['parcelas']

    def _procesar_predics_calib(símismo):
        """
        Ver la documentación de Simulable.

        :rtype: np.ndarray

        """

        vector_predics = np.array([])

        # Para cada experimento simulado, en orden...
        for nombre, predic in sorted(símismo.predics_exps.items()):

            # La combinaciones de etapas necesarias para procesar los resultados.
            # Tiene el formato general: {exp: {{1: [3,4, etc.]}, etc...], ...}
            combin_etps = símismo.info_exps['combin_etps'][nombre]

            # La ubicación de los datos observados
            ubic_obs = símismo.info_exps['ubic_obs'][nombre]

            # Combinar las etapas que lo necesitan
            for i in símismo.fantasmas:  # Combinaciones automáticas
                predic['Pobs'][..., i, :] += np.sum(predic['Pobs'][..., símismo.fantasmas[i], :], axis=3)
            for i in combin_etps:  # Combinaciones basadas en los datos disponibles
                predic['Pobs'][..., i, :] += np.sum(predic['Pobs'][..., combin_etps[i], :], axis=3)

            # Sacar únicamente las predicciones que corresponden con los datos observados disponibles
            vector_predics = np.concatenate((vector_predics,
                                             predic['Pobs'][ubic_obs[0], :, :, ubic_obs[1], ubic_obs[2]].flatten()))

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
            # Sacamos el objeto correspondiendo al experimento
            obj_exp = símismo.exps[exp]

            # Calculamos el número de parcelas en el experimento
            n_parc = len(símismo.info_exps['parcelas'][exp])

            # El número de pasos necesarios es la última observación en la base de datos de organismos.
            n_pasos = int(obj_exp.datos['Organismos']['tiempo'][-1] + 1)

            # Los índices de las etapas con cohortes para transiciones y para reproducciones
            índ_coh_trans = []
            índ_coh_repr = []
            for nombre_org, org in símismo.núms_etapas.items():
                # Para cada organismo...
                for n_etp in org.values():
                    # Para cara etapa...

                    # Verificar si necesita cohortes
                    if símismo.ecs['Reproducción']['Prob'] != 'Nada':
                        índ_coh_repr.append(n_etp)
                    if símismo.ecs['Transiciones']['Prob'] != 'Nada':
                        índ_coh_trans.append(n_etp)

            # Generamos el diccionario (vacío) de datos iniciales
            datos_inic = símismo._gen_dic_matr_predic(n_parc=n_parc, n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_paráms,
                                                      n_etps=n_etapas, n_pasos=n_pasos,
                                                      índ_coh_trans=índ_coh_trans, índ_coh_repr=índ_coh_repr)

            # Llenamos la poblaciones iniciales
            for i, n_etp in enumerate(símismo.info_exps['etps_interés'][exp]):
                # La matriz de datos iniciales para una etapa. Eje 0 = parcela, eje 1 = tiempo. Quitamos eje 1.
                nombre_col = símismo.info_exps['nombres_cols'][exp][i]
                matr_obs_inic = obj_exp.datos['Organismos']['obs'][nombre_col][:, 0]

                # Llenamos eje 0 (parcela), eje 1 y 2 (repeticiones estocásticas y paramétricas) de la etapa
                # en cuestión (eje 3) a tiempo 0 (eje 4).
                datos_inic['Pobs'][..., n_etp, 0] = matr_obs_inic[:, np.newaxis, np.newaxis]

            # Una cosa un poco a la par: llenar poblaciones iniciales manualmente para plantas con densidades fijas.
            for org in símismo.organismos.values():
                if type(org) is Plt.Constante:
                    n_etp = símismo.núms_etapas[org.nombre]['planta']
                    datos_inic['Pobs'][..., n_etp, 0] = org.densidad['planta']

            # Para hacer: inicializar las poblaciones de cohortes

            # Y, por fin, guardamos este diccionario bajo la llave "datos_inic" del diccionario.
            dic_args['datos_inic'][exp] = datos_inic

            # También guardamos el número de pasos y diccionarios de ingresos externos.
            # Para hacer: implementar clima y aplicaciones
            dic_args['n_pasos'][exp] = n_pasos
            if len(obj_exp.datos['Parcelas']):
                # Para hacer para poder incluir especificaciones de características de parcelas en Experimento
                pass
            else:
                avisar('Tamaño de parcelas no especificado. Se supondrá un tamaño de 1 ha.')
                dic_args['extrn'][exp] = {'superficies': np.ones(n_parc)}

        return dic_args

    def _llenar_coefs(símismo, n_rep_parám, calibs, comunes, usar_especificados):
        """
        Ver la documentación de Coso.

        :type n_rep_parám: int
        :type calibs: list | str
        :type comunes: bool
        :type usar_especificados: bool

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
                coefs_act = símismo.coefs_act[categ][subcateg] = []
                for _ in range(n_etapas):
                    coefs_act.append({})

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
                                                                       comunes=comunes,
                                                                       usar_especificados=usar_especificados)

                        # Si, al contrario, hay interacciones...
                        else:
                            for tipo_inter in d_parám['inter']:

                                if tipo_inter == 'presa' or tipo_inter == 'huésped':
                                    # Generar una matriz para guardar los valores de parámetros. Eje 0 = repetición
                                    # paramétrica, eje 1 = presa.
                                    matr = coefs_act[n_etp][parám] = np.empty(shape=(n_rep_parám, len(símismo.etapas)),
                                                                              dtype=object)
                                    matr[:] = np.nan

                                    # Para cada víctima del organismo...
                                    for org_víc, v in símismo.etapas[n_etp]['conf'][tipo_inter].items():

                                        # Buscar la lista de etapas que caen víctima
                                        if tipo_inter == 'presa':
                                            l_etps_víc = v
                                        else:
                                            l_etps_víc = v['entra']

                                        # Para cada etapa víctima
                                        for etp_víc in l_etps_víc:
                                            n_etp_víc = símismo.núms_etapas[org_víc][etp_víc]

                                            # Incluir etapas fantasmas
                                            l_etps_víc = [n_etp_víc]
                                            if n_etp_víc in símismo.fantasmas:
                                                l_etps_víc += símismo.fantasmas[n_etp_víc]

                                            for n in l_etps_víc:
                                                matr[:, n] = gen_vector_coefs(
                                                    dic_parám=d_parám_etp[org_víc][etp_víc],
                                                    calibs=calibs,
                                                    n_rep_parám=n_rep_parám,
                                                    comunes=comunes,
                                                    usar_especificados=usar_especificados)

                                else:
                                    # Al momento, solamente es posible tener interacciones con las presas de la etapa.
                                    # Si un día alguien quiere incluir más tipos de interacciones (como, por ejemplo,
                                    # interacciones entre competidores), se tendrían que añadir aquí.
                                    raise ValueError('Interacción "%s" no reconocida.' % tipo_inter)

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
                                                  dtype=int)  # eje

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
            for nombre_col in símismo.info_exps['nombres_cols'][exp]:
                # Sacar los datos del Experimento
                datos_etp = símismo.exps[exp].datos['Organismos']['obs'][nombre_col]

                # Guardar los datos aplastados en una única dimensión de matriz numpy (esto combina las dimensiones
                # de parcela (eje 0) y de tiempo (eje 1). También quitamos valores no disponibles (NaN).
                lista_obs.append(datos_etp[~np.isnan(datos_etp)].flatten())

        return np.concatenate(lista_obs)

    @staticmethod
    def _gen_dic_matr_predic(n_parc, n_rep_estoc, n_rep_parám, n_etps, n_pasos, índ_coh_trans, índ_coh_repr):
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
               'Movimiento': np.zeros(shape=tamaño_normal),
               'Cohortes': {},
               }

        # Agregar cohortes
        cohortes = dic['Cohortes']

        for n in índ_coh_repr:
            dic_cohorte = cohortes[n] = {}
            dic_cohorte['Pobs'] = np.zeros(10)
            dic_cohorte['repr'] = np.zeros(10)

        for n in índ_coh_trans:
            try:
                dic_cohorte = cohortes[n]
            except KeyError:
                dic_cohorte = cohortes[n] = {}
                dic_cohorte['Pobs'] = np.zeros(10)

            dic_cohorte['trans'] = np.zeros(10)

        return dic


# Funciones auxiliares

def _agregar_ruido(pobs, ruido):
    """

    :param pobs:
    :type pobs: np.ndarray
    :param ruido:
    :type ruido: float
    """

    np.add(np.round(np.random.normal(0, np.maximum(1, pobs * ruido))), pobs, out=pobs)

    np.maximum(0, pobs, out=pobs)


def redondear(matriz):
    """
    Esta función redondea una matriz de manera estocástica, según el residuo. Por ejemplo, 8.5 se redondeará como
      8 50% del tiempo y como 9 50% del tiempo. 8.01 se redondaría como 8 99% del tiempo y como 9 sólo 1% del
      tiempo. Esta función es indispensable para evitar el "problema del nanozorro." *

      * Así se llama en ecología la situación donde un nanozorro en un modelo ecológico se reproduce y establece
        una población funcional con el tiempo.

    :param matriz: La matriz a redondear
    :type matriz: np.ndarray

    """
    # Quitar los decimales de la matriz
    redondeada = np.floor(matriz)

    # Guardar los residuos
    residuos = matriz - redondeada

    # Generar una matriz de valores aleatorias entre 0 y 1
    prob = np.random.rand(*matriz.shape)

    # Redondear por arriba si el residuos es superior al valor aleatorio correspondiente. Este paso agrega
    # estocasticidad al modelo.
    np.add(redondeada, np.greater(residuos, prob), out=matriz)


def días_grados(mín, máx, umbrales, método='Triangular', corte='Horizontal'):
    """
    Esta función calcula los días grados basados en vectores de temperaturas mínimas y máximas diarias.
    Información sobre los métodos utilizados aquí se puede encontrar en:
    http://www.ipm.ucdavis.edu/WEATHER/ddconcepts.html

    :param mín:
    :type mín: float
    :param máx:
    :type máx: float
    :param umbrales:
    :type umbrales: tuple
    :param método:
    :type método: str
    :param corte:
    :type corte: str
    :return: número de días grados (número entero)
    :rtype: int
    """

    if método == 'Triangular':
        # Método triangular único
        sup_arriba = max(12 * (máx - umbrales[1]) ** 2 / (máx - mín), 0) / 24
        sup_centro = max(12 * (umbrales[1] - umbrales[0]) ** 2 / (umbrales[1] - mín), 0) / 24
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
            sup_arriba = 2 * (intersect_máx * (prom - máx) + 2 * mat.pi / 24 * mat.sin(2 * mat.pi / 24 * intersect_máx))

        if umbrales[0] <= mín:
            intersect_mín = intersect_máx
        else:
            intersect_mín = 24 * mat.acos((umbrales[0] - prom) / amp)

        sup_centro = 2 * intersect_máx * (máx - mín)
        sup_lados = 2 * (2 * mat.pi / 24 * mat.sin(2 * mat.pi / 24 * intersect_mín) -
                         2 * mat.pi / 24 * mat.sin(2 * mat.pi / 24 * intersect_máx) +
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


def trans_cohorte(pobs, edades, cambio, tipo_dist, paráms_dist, quitar=True):
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
    :rtype: np.ndarray()
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

    dist = Ds.dists[tipo_dist]['scipy'](**paráms)

    probs = (dist.cdf(edades + cambio) - dist.cdf(edades)) / (1 - dist.cdf(edades))
    n_cambian = np.random.binomial(pobs, probs)

    if quitar:
        pobs -= n_cambian

    return np.sum(n_cambian, axis=0)


def añadir_a_cohorte(dic_cohorte, nuevos, edad=0):
    """
    Esta función agrega nuevos miembros a un cohorte existente.

    :param dic_cohorte: El diccionario del cohorte. Tiene la forma general siguiente:
      {'Pobs': [matriz de poblaciones]
       'Edades': {'trans': [matriz de edades],
                  'repr': [matriz de edades]
                  }

      Todas las matrices tienen el mismo orden de eje:
          Eje 0: Cohorte
          Eje 1: Parcela
          Eje 2: Repetición estocástica
          Eje 3: Repetición paramétrica

    :type dic_cohorte: dict

    :param nuevos: La matriz de poblaciones para agregar.
        Eje 0: Parcela
        Eje 1: Repetición estocástica
        Eje 2: Repetición paramétrica

    :type nuevos: np.ndarray

    :param edad: Las edades iniciales de los nuevos miembros al cohorte. El valor automático es, naturalmente, 0.
      (Esto se puede cambiar si estamos transicionando cohortes existentes de un otro cohorte.) Si es un
      diccionario, debe tener la forma general siguiente:
      {'trans': matriz Numpy,
       'repr': matriz Numpy},
      donde cada matriz NumPy tiene los ejes siguientes:
          Eje 1: Parcela
          Eje 2: Repetición estocástica
          Eje 3: Repetición paramétrica
    :type edad: int | float | dict
    """

    # Primero, hay que ver si hay suficientemente espacio en la matriz de cohortes.
    try:
        primer_vacío = np.where(dic_cohorte['Pobs'] == 0)[0][0]  # El primero vacío
    except IndexError:
        # Si no había ligar, desdoblar el tañano de las matrices de cohortes

        primer_vacío = dic_cohorte['Pobs'].shape[0]  # El primero vacío (que vamos a crear)
        np.append(dic_cohorte['Pobs'], np.zeros_like(dic_cohorte['Pobs']), axis=0)

        # Extender cada matriz de edades también
        for ed in dic_cohorte['Edades'].values():
            np.append(ed, np.zeros_like(ed), axis=0)

    # Guardar el número de nuevos integrantes del grupo añadido
    dic_cohorte['Pobs'][primer_vacío] = nuevos

    # Inicializar las edades de este nuevo grupo
    for tipo_ed, ed in dic_cohorte['Edades'].items():
        # Para cada matriz de edad...

        # Poner su índice correspondiente a la edad inicial
        ed[primer_vacío] = edad[tipo_ed]


def quitar_de_cohorte(dic_cohorte, muertes, recip=None):
    """

    :param dic_cohorte: El diccionario del cohorte. Tiene la forma general siguiente:
      {'Pobs': [matriz de poblaciones]
       'Edades': {'Trans': [matriz de edades],
                  'Repr': [matriz de edades]
                  }

      Todas las matrices tienen el mismo orden de eje:
          Eje 0: Cohorte
          Eje 1: Parcela
          Eje 2: Repetición estocástica
          Eje 3: Repetición paramétrica

    :type dic_cohorte: dict

    :param muertes: La matriz de muertes aleatorias a quitar del cohorte.
      Eje 0: Cohorte
      Eje 1: Parcela
      Eje 2: Repetición estocástica
      Eje 3: Repetición paramétrica

    :type muertes: np.ndarray

    :param recip: Un diccionario, opcional, de un otro cohorte al cual los organismos quitados del primero cohorte
      se tienen que añadir. Tiene el mismo formato que dic_cohorte.
    :type recip: dict

    """

    # Para simplificar el código
    pobs = dic_cohorte['Pobs']

    muertes = muertes.copy()  # Para no afectar el parámetro que se pasó a la función

    # Dos maneras de hacer las cosas; no estoy seguro de cuál será la más rápida:
    # Una suma cumulativa inversa de la distribución de cohortes
    pobs_cums = np.cumsum(pobs[::-1], axis=0)[::-1]

    for n_día, pobs_día in enumerate(pobs):

        # Probabilidad condicional de morirse para este día, dado las muertes en días anteriores:
        p = muertes / pobs_cums[n_día]

        # Quitar los de esta edad que se murieron
        quitar = np.random.binomial(pobs_día, p)
        np.subtract(pobs_día, quitar, out=pobs_día)

        # Actualizar las muertes que faltan implementar
        np.subtract(muertes, quitar)

        # Si transicion a otro cohorte (de otro organismo), implementarlo aquí
        if recip is not None:
            añadir_a_cohorte(dic_cohorte=recip, nuevos=quitar, edad=dic_cohorte['Edades'])

        # Si ya no hay nada que hacer, parar aquí
        if sum(muertes) == 0:
            return

        """
        # Alternativamente, podríamos hacer esto (primero, quitar las bogues):
        while sum(muertes):
        p = muertes / pobs.sum(axis=0)
        quitar = np.round(p * pobs)

        pobs -= quitar

        muertes -= np.sum(quitar, axis=0)
        """


def probs_conj(matr, máx, eje):
    """
    Esta función utiliza las reglas de probabilidades conjuntas para ajustar depredación con presas o depredadores
      múltiples cuya suma podría sumar más que el total de presas o la capacidad del depredador.

    :param matr: Una matriz con los valores para ajustar.
    :type matr: np.ndarray

    :param máx: Una matriz con los valores máximos para la matriz para ajustar. Debe ser de tamaño compatible con
      matr.
    :type máx: np.ndarray

    :param eje: El eje según cual hay que hacer los ajustes
    :type eje: int

    """

    np.multiply(np.expand_dims(np.product(1 - matr / máx, axis=eje) / np.sum(matr / máx, axis=eje), axis=eje),
                matr, out=matr)

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


def copiar_dic_refs(d, c=None):
    """

    :param d:
    :type d: dict | list

    :param c: Para recursiones. No especificar al llamar la función.
    :type c: dict | list

    :return: d_final
    :rtype: dict | list
    """

    if c is None:
        if type(d) is list:
            c = []
        elif type(d) is dict:
            c = {}

    if type(d) is list:
        for n, v in enumerate(d):
            if type(v) is dict:
                c[n] = {}
                copiar_dic_refs(v, c=c[n])
            elif type(v) is list:
                c[n] = []
                copiar_dic_refs(v, c=c[n])
            else:
                c[n] = v

    elif type(d) is dict:
        for ll, v in d.items():
            if type(v) is dict:
                c[ll] = {}
                copiar_dic_refs(v, c=c[ll])
            if type(v) is list:
                c[ll] = []
                copiar_dic_refs(v, c=c[ll])
            else:
                c[ll] = v

    return c
