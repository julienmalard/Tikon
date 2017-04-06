import math as mat
import os
from warnings import warn as avisar

import numpy as np

from tikon.Coso import Simulable
from tikon.Matemáticas import Distribuciones as Ds, Ecuaciones as Ec
from tikon.Matemáticas.Arte import gráfico
from tikon.Matemáticas.Incert import validar, gen_vector_coefs
from . import Insecto as Ins
from .Organismo import Organismo
from .Gen_organismos import generar_org


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

    # Una Red tiene ni ecuaciones, ni parámetros propios.
    dic_info_ecs = None

    def __init__(símismo, nombre, proyecto, organismos=None):

        """
        :param nombre: El nombre de la red.
        :type nombre: str

        :param organismos: Una lista de objetos o nombres de organismos para añadir a la red, o una instancia única
        de un tal objeto.
        :type organismos: list
        
        """

        super().__init__(nombre=nombre, proyecto=proyecto)

        # La información necesaria para recrear la Red
        símismo.receta['estr']['Organismos'] = {}

        # Unas referencias internas para facilitar el manejo de la red.
        símismo.organismos = {}  # Para guardar una referencia a los objetos de los organismos en la red
        símismo.etapas = []  # Una lista de las recetas (y más) de las etapas de los organismos en la red
        símismo.núms_etapas = {}

        # Un diccionario para las distribuciones de transiciones y de reproducción
        símismo.dists = {'Trans': {}, 'Repr': {}}

        # Para guardar los tipos de ecuaciones de los organismos en la red
        símismo.ecs = {}

        # Para guardar el orden relativo de transiciones y de reproducciones entre etapas
        símismo.orden = {}

        # Para guardar los índices de las etapas con cohortes
        símismo.índices_cohortes = []

        # Para guardar etapas que siempre se deben combinar antes de reportar resultados (por ejemplo, etapas fantasmas)
        # Tendrá la forma siguiente:
        # {núm_etp_víctima : {'Parasitoide 1': núm_etp_fantasma,
        #                     'Parasitoide 2': núm_etp_fantasma,
        #                     },
        # ...]
        símismo.fantasmas = {}

        # Información de parasitoides:
        símismo.parasitoides = {'índices': (), 'adultos': {}, 'juvs': {}}

        # La matriz de datos de las simulaciones (incluso los datos de poblaciones)
        símismo.predics = {'Pobs': np.array([]),
                           'Depredación': np.array([]),
                           'Crecimiento': np.array([]),
                           'Reproducción': np.array([]),
                           'Muertes': np.array([]),
                           'Transiciones': np.array([]),
                           'Movimiento': np.array([]),
                           'Cohortes': {},
                           'Matrices': {}
                           }

        # Un diccionario para guardar información específica a cada experimento asociado para poder procesar
        # las predicciones de la red en función a cada experimento.
        símismo.info_exps = {'etps_interés': {}, 'combin_etps': {}, 'nombres_cols': {},
                             'ubic_obs': {}, 'parcelas': {}, 'superficies': {}}

        # Si ya se especificaron organismos en la inicialización, añadirlos a la red.
        if type(organismos) is not list:
            organismos = [organismos]

        if organismos is not None:
            for org in organismos:
                símismo.añadir_org(org)

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
        else:
            # Si organismo no es objeto de Organismo, hay un error.
            raise TypeError('"{}" debe ser de tipo Organismo o de texto.'.format(organismo))

        # Añadir el organismo a la receta
        dic_org = símismo.receta['estr']['Organismos'][nombre] = {}
        dic_org['config'] = organismo.config
        dic_org['proyecto'] = organismo.proyecto
        dic_org['ext'] = organismo.ext

        # Poner el organismo en la lista activa
        símismo.organismos[nombre] = obj_org

        # Guardar el Organismo en la lista de objetos de la red.
        símismo.objetos.append(obj_org)

        # Notar que ahora hay que actualizar la Red
        símismo.listo = False

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

        # Notar que ahora hay que actualizar la Red
        símismo.listo = False

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

                # Extraer y generar el archivo donde se ubica el organismo
                archivo_org = os.path.join(dic_org['proyecto'], nombre + dic_org['ext'])
                archivo_org_prep = símismo._prep_directorio(directorio=archivo_org)

                # Crear una instancia de la subclase apropiada de Organismo, si es que extista el archivo pedido.
                if os.path.isfile(archivo_org_prep):
                    símismo.organismos[nombre] = generar_org(archivo_org_prep)
                else:
                    raise ValueError('No se encontró el organismo "{}" donde lo esperábamos: \n\t{}'
                                     .format(nombre, archivo_org_prep))

                # ...y aplicar las configuraciones guardadas en la red
                símismo.organismos[nombre].config = dic_org['config']

        for org in símismo.organismos:
            if org not in símismo.receta['estr']['Organismos']:
                # Si un organismo activo en la Red no existe en la receta de la Red...

                # ...quitar el organismo del diccionario de organismos activos
                símismo.organismos.pop(org)

        # Limpiar todo
        símismo.etapas.clear()  # Borrar la lista de etapas existentes
        símismo.fantasmas.clear()
        símismo.núms_etapas.clear()
        símismo.parasitoides['adultos'].clear()
        símismo.parasitoides['juvs'].clear()

        # Guardar las etapas de todos los organismos de la red y sus coeficientes en un orden reproducible
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

        # Crear etapas fantasmas para huéspedes infectados
        for n_etp, etp in enumerate(símismo.etapas):
            # Para cada etapa de la Red...

            # El diccionario de huéspedes de la etapa
            dic_hués = etp['conf']['huésped']

            if len(dic_hués):
                # Si esta etapa tiene huéspedes

                # El objeto del organismo al cual esta etapa pertenece
                obj_org_inf = símismo.organismos[etp['org']]

                # Agregar el organismo a la lista de parasitoides
                d_info_parás = símismo.parasitoides['adultos'][n_etp] = {'n_fants': [], 'n_vícs': [],
                                                                         'n_entra': []}

                n_juv = símismo.núms_etapas[obj_org_inf.nombre]['juvenil']
                símismo.parasitoides['juvs'][n_juv] = n_etp

                # Para cada organismo que se ve infectado por esta etapa
                for org_hués, d_org_hués in dic_hués.items():

                    # Una referencia al objeto del organismo hospedero
                    obj_org_hués = símismo.organismos[org_hués]

                    # El índice de la primera y la última etapa del huésped que pueden tener la infección
                    n_prim = min([símismo.núms_etapas[org_hués][x] for x in d_org_hués['entra']])  # type: int
                    n_sale = símismo.núms_etapas[org_hués][d_org_hués['sale']]  # type: int

                    # Guardar los índices de las etapas de la víctima en las cuales el parasitoide puede entrar
                    d_info_parás['n_entra'] = [símismo.núms_etapas[org_hués][x] for x in d_org_hués['entra']]

                    # Los índices relativos (internos al organismo)
                    n_rel_prim = símismo.etapas[n_prim]['dic']['posición']
                    n_rel_sale = símismo.etapas[n_sale]['dic']['posición']

                    # Una lista con todas las etapas del huésped que pueden tener la infección.
                    l_d_etps_hués = [x for x in símismo.organismos[org_hués].etapas[n_rel_prim: n_rel_sale + 1]]

                    # El nombre de la fase larval del organismo que infecta
                    nombre_etp_larva_inf = obj_org_inf.etapas[0]['nombre']
                    n_larva = símismo.núms_etapas[obj_org_inf.nombre][nombre_etp_larva_inf]  # type: int

                    # Crear las etapas fantasmas para las etapas infectadas del huésped
                    for d_etp_hués in l_d_etps_hués:

                        # El indice, en el organismo, de la etapa hospedera
                        n_etp_hués = d_etp_hués['posición']

                        # El índice de la etapa fantasma
                        n_etp_fant = len(símismo.etapas)

                        # Agregar los números de etapas al diccionario de información de parasitismo.
                        d_info_parás['n_fants'].append(n_etp_fant)
                        d_info_parás['n_vícs'].append(n_etp_hués)

                        # El nombre de la etapa hospedera original
                        nombre_etp_hués = d_etp_hués['nombre']

                        # Crear un diccionario para la etapa fantasma. Queremos la misma estructura de diccionario que
                        # la etapa original del huésped; tiene que ser un diccionario distinto pero con referencias
                        # a los mismos objetos de matrices o variables PyMC (para coefs).
                        dic_trans = copiar_dic_refs(obj_org_hués.receta['estr'][nombre_etp_hués])
                        dic_trans['nombre'] = '%s infectando a %s_%s' % (etp['org'], org_hués, nombre_etp_hués)
                        dic_trans['posición'] = 0  # No hay posición relativa para etapas fantasmas

                        # La configuración de la etapa fantasma es la misma que la de su etapa pariente
                        conf = obj_org_hués.config[nombre_etp_hués]

                        # Copiamos el diccionario de coeficientes, pero con referencias a los objetos de distrubuciones
                        # (Comparten los mismos variables).
                        coefs = copiar_dic_refs(obj_org_hués.receta['coefs'][nombre_etp_hués])

                        # Verificar si la etapa hospedera es la última de este organismo que puede estar infectada
                        if n_etp_hués <= len(l_d_etps_hués) - 1:
                            # Si no es la última, esta etapa transicionará a la próxima etapa fantasma de este
                            # organismo.

                            # Buscar la primera etapa existente del organismo que infecta
                            nombre_etp_inf_0 = obj_org_inf.etapas[0]['nombre']
                            n_etp_inf_0 = símismo.núms_etapas[obj_org_inf.nombre][nombre_etp_inf_0]

                            # Se guarda la posición relativa al organismo infectuoso
                            n_trans = n_etp_fant + 1 - n_etp_inf_0

                        else:
                            # Si lo es, transicionará a la etapa recipiente (siempre la segunda) del organismo
                            # infectuoso.
                            n_trans = 1

                            # Usar las ecuaciones de transiciones de la larva del agente infectuoso para las
                            # transiciones de la última etapa infectada de la víctima.
                            prob_trans = símismo.etapas[n_larva]['dic']['ecs']['Transiciones']['Prob']
                            ec_edad = símismo.etapas[n_larva]['dic']['ecs']['Edad']['Ecuación']
                            coefs_prob_trans = símismo.etapas[n_larva]['coefs']['Transiciones']['Prob'][prob_trans]
                            coefs_edad = símismo.etapas[n_larva]['coefs']['Edad']['Ecuación'][ec_edad]

                            dic_trans['ecs']['Transiciones']['Prob'] = prob_trans
                            dic_trans['ecs']['Edad']['Ecuación'] = ec_edad
                            coefs['Transiciones']['Prob'][prob_trans] = coefs_prob_trans
                            coefs['Edad']['Ecuación'][ec_edad] = coefs_edad

                        dic_trans['trans'] = n_trans

                        dic_etp = dict(org=etp['org'],
                                       nombre=dic_trans['nombre'],
                                       dic=dic_trans,
                                       conf=conf,
                                       coefs=coefs)

                        símismo.etapas.append(dic_etp)

                        símismo.núms_etapas[etp['org']][dic_trans['nombre']] = n_etp_fant

                        # Guardar el vínculo entre la etapa víctima y la(s) etapa(s) fanstasma(s) correspondiente(s)
                        n_etp_hués_abs = símismo.núms_etapas[org_hués][nombre_etp_hués]
                        if n_etp_hués_abs not in símismo.fantasmas.keys():
                            símismo.fantasmas[n_etp_hués_abs] = {}
                        símismo.fantasmas[n_etp_hués_abs][etp['org']] = n_etp_fant

                        # Para hacer: agregar aquí un vínculo en símismo.etapas para enfermedades de etapas
                        # víctimas de parasitoides.

        # Índices para luego poder encontrar las interacciones entre parasitoides y víctimas en las matrices de
        # depredación
        índs_parás = [p for n_p, d_p in símismo.parasitoides['adultos'].items() for p in [n_p] * len(d_p['n_entra'])]
        índs_víc = [v for d in símismo.parasitoides['adultos'].values() for v in d['n_entra']]
        símismo.parasitoides['índices'] = (índs_parás, índs_víc)

        # Crear el diccionario de los tipos de las ecuaciones activas para cada etapa.
        símismo.ecs.clear()  # Borrar todo en el diccionario existente para evitar posibilidades de cosas raras

        for categ in Ec.ecs_orgs:
            # Para cada tipo de ecuación posible...

            # Crear la llave correspondiente en el diccionario de tipos de ecuaciones de la red.
            símismo.ecs[categ] = {}

            # Para cada subcategoría de ecuación posible...
            for sub_categ in Ec.ecs_orgs[categ]:

                # Crear una lista
                símismo.ecs[categ][sub_categ] = {}

                # Para cada tipo de ecuación posible para la subcategoría...
                for tipo_ec in Ec.ecs_orgs[categ][sub_categ]:

                    # Si el tipo no es "Nada"...
                    if tipo_ec != 'Nada':

                        # Sacar los índices de las etapas de la Red con este tipo de ecuación.
                        índs_etps = [n for n, d in enumerate(símismo.etapas) if
                                     d['dic']['ecs'][categ][sub_categ] == tipo_ec]

                        # Si hay etapas con este tipo de ecuación...
                        if len(índs_etps):
                            # Guardar los índices bajo el nombre del tipo de ecuación.
                            símismo.ecs[categ][sub_categ][tipo_ec] = índs_etps

        # Desactivar las ecuaciones de transiciones de juveniles de parasitoides (porque estas se implementan
        # por la última fase fantasma de la víctima correspondiente
        for org in símismo.organismos.values():
            if isinstance(org, Ins.Parasitoide):
                n_etp = símismo.núms_etapas[org.nombre]['juvenil']  # type: int

                dic_trans = símismo.etapas[n_etp]['dic']['ecs']['Transiciones']
                dic_edad = símismo.etapas[n_etp]['dic']['ecs']['Edad']
                tipo_ed = dic_edad['Ecuación']
                tipo_mult = dic_trans['Mult']
                tipo_prob = dic_trans['Prob']

                if tipo_prob != 'Nada':
                    símismo.ecs['Transiciones']['Mult'][tipo_mult].remove(n_etp)
                    símismo.ecs['Transiciones']['Prob'][tipo_prob].remove(n_etp)
                if tipo_ed != 'Nada':
                    símismo.ecs['Edad']['Ecuación'][tipo_ed].remove(n_etp)

        # Desactivar las ecuaciones de depredación para etapas que tienen ni presas, ni huéspedes
        for n_etp, d_etp in enumerate(símismo.etapas):

            # Si la etapa tiene ni presa, ni huésped...
            if not len(d_etp['conf']['presa']) and not len(d_etp['conf']['huésped']):

                # ...Desactivar sus ecuaciones de depredación.
                tipo_depred = símismo.etapas[n_etp]['dic']['ecs']['Depredación']['Ecuación']

                if tipo_depred != 'Nada':
                    símismo.ecs['Depredación']['Ecuación'][tipo_depred].remove(n_etp)

        # Guardar el orden de transiciones y de reproducciones
        símismo.orden['trans'] = np.full(len(símismo.etapas), -1, dtype=np.int)
        símismo.orden['repr'] = np.full(len(símismo.etapas), -1, dtype=np.int)

        for nombre_org, org in símismo.núms_etapas.items():
            # Para cada organismo...

            # Encontrar el índice de la primera etapa del organismo
            n_etp_mín = min(org.values())

            for etp, n_etp in org.items():  # type: int
                # Para cada etapa del organismo...

                # Buscar el diccionario de la etapa
                d_etp = símismo.etapas[n_etp]['dic']

                # Si la etapa tiene transiciones y/o reproducciones, ajustar el número de la etapas a la cual esta
                # etapa transiciona o se reproduce
                if d_etp['ecs']['Transiciones']['Prob'] != 'Nada':
                    símismo.orden['trans'][n_etp] = d_etp['trans'] + n_etp_mín if d_etp['trans'] != -1 else -1
                if d_etp['ecs']['Reproducción']['Prob'] != 'Nada':
                    símismo.orden['repr'][n_etp] = d_etp['repr'] + n_etp_mín if d_etp['repr'] != -1 else -1

        # Actualizar la información de los cohortes.
        í_cohs = símismo.índices_cohortes
        í_cohs.clear()

        for n_etp, etp in enumerate(símismo.etapas):
            # Para cara etapa de cada organismo...

            # Verificar si necesita cohortes
            req_cohs = any([n_etp in l_etps for l_etps in símismo.ecs['Edad']['Ecuación'].values()])

            if req_cohs:
                í_cohs.append(n_etp)

        # Actualizar los vínculos con los experimentos
        símismo._actualizar_vínculos_exps()

        # La Red ya está lista para simular
        símismo.listo = True

    def dibujar(símismo, mostrar=True, directorio=None, exper=None, todas_líneas=False, incert='componentes'):
        """
        Ver la documentación de Simulable.

        :type mostrar: bool
        :type directorio: str
        :type exper: list

        :param todas_líneas: Si queremos incluir las líneas de cada repetición individual en el gráfico.
        :type todas_líneas: bool

        :param incert: El tipo de incertidumbre que querremos incluir en el gráfico.
        :type incert: str

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

            dic_preds_obs_pobs = símismo._sacar_vecs_preds_obs(exp=exp)

            # Primero, vamos a dibujar las poblaciones

            # Para cada organismo en la red...
            for org, d_org in dic_preds_obs_pobs.items():
                dic_título['org'] = org

                # Para cada etapa de este organismo...
                for etp in d_org:
                    dic_título['etp'] = etp

                    # El vector de observaciones y la matriz de predicciones para poblaciones.
                    # Eje 0: parcela, 1: rep estoc, 2: rep parám, 3: día
                    matr_predic = dic_preds_obs_pobs[org][etp]['preds']
                    vector_obs = dic_preds_obs_pobs[org][etp]['obs']  # Eje 0: parcela, eje 2: día

                    # Para cada parcela en las predicciones...
                    for n_p in range(matr_predic.shape[0]):

                        # Las matrices de predicciones y observaciones de poblaciones, con una única parcela
                        matr_predic_prc = matr_predic[n_p, :, :]
                        if vector_obs is None:
                            vector_obs_prc = None
                        else:
                            vector_obs_prc = vector_obs[n_p, :]

                        # El archivo para guardar la imagen
                        dir_img = os.path.join(directorio, 'Pobs')

                        # Generar el titulo del gráfico. Incluir el nombre de la parcela, si necesario:
                        if len(símismo.info_exps['parcelas'][exp]) > 1:
                            prc = símismo.info_exps['parcelas'][exp][n_p]
                            título = '{exp}, Parcela {prc}, {org}, etapa {etp}'.format(**dic_título, prc=prc)
                        else:
                            título = '{exp}, {org}, etapa {etp}'.format(**dic_título)

                            # Generar el gráfico
                        gráfico(matr_predic=matr_predic_prc, vector_obs=vector_obs_prc,
                                título=título, etiq_y='Población',
                                todas_líneas=todas_líneas, incert=incert,
                                mostrar=mostrar, directorio=dir_img)

            # Ahora, vamos a dibujar los detalles de la simulación
            if símismo.predics_exps[exp]['Reproducción'].shape == símismo.predics_exps[exp]['Pobs'].shape:

                # Para cada organismo en la red...
                for org, d_org in dic_preds_obs_pobs.items():
                    dic_título['org'] = org

                    # Para cada etapa de este organismo...
                    for etp in d_org:
                        dic_título['etp'] = etp

                        n_etp = símismo.núms_etapas[org][etp]  # type: int

                        for det in ['Crecimiento', 'Muertes', 'Transiciones', 'Reproducción']:

                            if not any([n_etp in x
                                        for s_c in símismo.ecs[det].values()
                                        for x in s_c.values()]):
                                continue

                            if det == 'Reproducción':
                                tipo = 'Recipiente'
                                n_etp_dib = símismo.orden['repr'][n_etp]
                            elif det == 'Transiciones':
                                tipo = 'Recipiente'
                                n_etp_dib = símismo.orden['trans'][n_etp]
                            else:
                                tipo = 'Etapa'
                                n_etp_dib = n_etp

                            # La matriz de predicciones
                            # Eje 0: parcela, 1: rep estoc, 2: rep parám, 4: día
                            matr_predic = símismo.predics_exps[exp][det][..., n_etp_dib, :]

                            # Para cada parcela en las predicciones...
                            for n_p in range(matr_predic.shape[0]):

                                # Las matrices de predicciones y observaciones, con una única parcela
                                matr_predic_prc = matr_predic[n_p, ...]

                                # El archivo para guardar la imagen
                                dir_img = os.path.join(directorio, det)

                                # Generar el titulo del gráfico. Incluir el nombre de la parcela, si necesario:
                                if len(símismo.info_exps['parcelas'][exp]) > 1:
                                    prc = símismo.info_exps['parcelas'][exp][n_p]
                                    título = '{exp}, Parcela {prc}, {org}, {tipo} {etp}'\
                                        .format(**dic_título, prc=prc, tipo=tipo)
                                else:
                                    título = '{exp}, {org}, {tipo} {etp}'.format(**dic_título, tipo=tipo)

                                # Generar el gráfico
                                gráfico(matr_predic=matr_predic_prc,
                                        título=título, etiq_y=det,
                                        todas_líneas=todas_líneas, incert=incert,
                                        mostrar=mostrar, directorio=dir_img)

                        # Ahora para la depredación
                        if not any([n_etp in x for x in símismo.ecs['Depredación']['Ecuación'].values()]):
                            continue

                        # La matriz de predicciones
                        # Eje 0: parcela, 1: rep estoc, 2: rep parám, 4: etp víctima, 5: día
                        matr_predic = símismo.predics_exps[exp]['Depredación'][..., n_etp, :, :]

                        # Para cada parcela en las predicciones...
                        for n_p in range(matr_predic.shape[0]):

                            # Las matrices de predicciones y observaciones, con una única parcela
                            matr_predic_prc = matr_predic[n_p, ...]

                            # El archivo para guardar la imagen
                            dir_img = os.path.join(directorio, 'Depredación')

                            presas = [símismo.núms_etapas[o][e]
                                      for o, d_e in símismo.etapas[n_etp]['conf']['presa'].items()
                                      for e in d_e]
                            huéspedes = [símismo.núms_etapas[o][e]
                                         for o, d_e in símismo.etapas[n_etp]['conf']['huésped'].items()
                                         for e in d_e['entra']]
                            víctimas = presas + huéspedes

                            for n_etp_víc in víctimas:  # type: int

                                etp_víc = símismo.etapas[n_etp_víc]['nombre']
                                org_víc = símismo.etapas[n_etp_víc]['org']

                                dic_título['víc'] = etp_víc

                                matr_predic_prc_víc = matr_predic_prc[..., n_etp_víc, :]

                                # Generar el titulo del gráfico. Incluir el nombre de la parcela, si necesario:
                                if len(símismo.info_exps['parcelas'][exp]) > 1:
                                    prc = símismo.info_exps['parcelas'][exp][n_p]
                                    título = '{exp}, Parcela {prc}, ' \
                                             '{org}, {etp} atacando a {org_víc}, etapa {etp_víc}'.\
                                        format(**dic_título, prc=prc, org_víc=org_víc, etp_víc=etp_víc)
                                else:
                                    título = '{exp}, {org}, {etp} atacando a {org_víc}, etapa {etp_víc}'\
                                        .format(**dic_título, org_víc=org_víc, etp_víc=etp_víc)

                                # Generar el gráfico
                                gráfico(matr_predic=matr_predic_prc_víc,
                                        título=título, etiq_y='Depredación',
                                        todas_líneas=todas_líneas, incert=incert,
                                        mostrar=mostrar, directorio=dir_img)

    def _calc_depred(símismo, pobs, depred, extrn, paso):
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
                y = a*(1 - e^(-P/(a*D))) * (P^2 / (P^2 + b)

                  a es el máximo de consumo de presa por depredador (cuando las presas son abundantes y los
                    depredadores no compiten entre sí mismos)

                  b^0.5 es la densidad de presas a la cuál, donde hay suficientemente pocos depredadores para causar
                    competition entre ellos, los depredadores consumirán a/2 presas por depredador.

        :param pobs: matriz numpy de poblaciones actuales.
        :type pobs: np.ndarray
        
        :param extrn: Un diccionario con datos externos
        :type extrn: dict

        :param paso: El paso de tiempo de la simulación.
        :type paso: int

        """

        # Calcular cuántas presas cada especie de depredador podría comerse

        # A este punto, depred representa la depredación potencial per cápita de depredador
        tipos_ec = símismo.ecs['Depredación']['Ecuación']  # type: dict

        # Si no hay nada que hacer, devolver ahora
        if not len(tipos_ec):
            return

        # La lista de los coeficientes de cada etapa para la depredación
        coefs = símismo.coefs_act_númzds['Depredación']['Ecuación']

        # Densidades de poblaciones
        dens = np.divide(pobs, extrn['superficies'].reshape(pobs.shape[0], 1, 1, 1))

        for tp_ec, í_etps in tipos_ec.items():  # Para cada tipo de ecuación...

            # Los coeficientes para las etapas con este tipo de ecuación
            cf = coefs[tp_ec]  # type: dict

            # Una COPIA de la parte de la matriz que representa la depredación por estas etapas
            depred_etp = depred[:, :, :, í_etps, :]

            # Calcular la depredación según la ecuación de esta etapa.
            if tp_ec == 'Tipo I_Dependiente presa':
                # Depredación de respuesta funcional tipo I con dependencia en la población de la presa.
                np.multiply(pobs, cf['a'], out=depred_etp)

            elif tp_ec == 'Tipo II_Dependiente presa':
                # Depredación de respuesta funcional tipo II con dependencia en la población de la presa.
                np.multiply(dens, cf['a'] / (dens + cf['b']), out=depred_etp)

            elif tp_ec == 'Tipo III_Dependiente presa':
                # Depredación de respuesta funcional tipo III con dependencia en la población de la presa.
                np.multiply(np.square(dens), cf['a'] / (np.square(dens) + cf['b']), out=depred_etp)

            elif tp_ec == 'Tipo I_Dependiente ratio':
                # Depredación de respuesta funcional tipo I con dependencia en el ratio de presa a depredador.
                dens_depred = dens[:, :, :, í_etps]  # La población de esta etapa
                np.multiply(dens / dens_depred, cf['a'], out=depred_etp)

            elif tp_ec == 'Tipo II_Dependiente ratio':
                # Depredación de respuesta funcional tipo II con dependencia en el ratio de presa a depredador.
                dens_depred = dens[:, :, :, í_etps]  # La población de esta etapa
                np.multiply(dens / dens_depred, cf['a'] / (dens / dens_depred + cf['b']), out=depred_etp)

            elif tp_ec == 'Tipo III_Dependiente ratio':
                # Depredación de respuesta funcional tipo III con dependencia en el ratio de presa a depredador.
                dens_depred = dens[:, :, :, í_etps]  # La población de esta etapa
                np.multiply(np.square(dens / dens_depred), cf['a'] / (np.square(dens / dens_depred) + cf['b']),
                            out=depred_etp)

            elif tp_ec == 'Beddington-DeAngelis':
                # Depredación de respuesta funcional Beddington-DeAngelis. Incluye dependencia en el depredador.
                dens_depred = dens[:, :, :, í_etps]  # La población de esta etapa
                np.multiply(dens, cf['a'] / (cf['b'] + dens + cf['c'] * dens_depred), out=depred_etp)

            elif tp_ec == 'Tipo I_Hassell-Varley':
                # Depredación de respuesta funcional Tipo I con dependencia Hassell-Varley.
                dens_depred = dens[:, :, :, í_etps]  # La población de esta etapa
                np.multiply(dens / dens_depred ** cf['m'], cf['a'], out=depred_etp)

            elif tp_ec == 'Tipo II_Hassell-Varley':
                # Depredación de respuesta funcional Tipo II con dependencia Hassell-Varley.
                dens_depred = dens[:, :, :, í_etps]  # La población de esta etapa
                np.multiply(dens / dens_depred ** cf['m'], cf['a'] / (dens / dens_depred ** cf['m'] + cf['b']),
                            out=depred_etp)

            elif tp_ec == 'Tipo III_Hassell-Varley':
                # Depredación de respuesta funcional Tipo III con dependencia Hassell-Varley.
                dens_depred = dens[:, :, :, í_etps]  # La población de esta etapa
                np.multiply(dens / dens_depred ** cf['m'], cf['a'] / (dens / dens_depred ** cf['m'] + cf['b']),
                            out=depred_etp)

            elif tp_ec == 'Kovai':
                # Depredación de respuesta funcional de asíntota doble (ecuación Kovai).
                dens_depred = dens[:, :, :, í_etps]  # La población de esta etapa (depredador)
                ratio = dens / dens_depred[..., np.newaxis]

                np.multiply(cf['a'],
                            np.multiply(
                                np.subtract(1,
                                            np.exp(
                                                np.divide(
                                                    -np.where(ratio == np.inf, [0], ratio),
                                                    cf['a'])
                                            )
                                            ),
                                np.divide(np.square(dens),
                                          np.square(dens) + cf['b']
                                          )
                            ),
                            out=depred_etp)

                # Ajustar por la presencia de múltiples presas (eje 4 = presas)
                probs_conj(depred_etp, pesos=cf['a'], máx=1, eje=4)

            else:
                # Si el tipo de ecuación no estaba definida arriba, hay un error.
                raise ValueError('Tipo de ecuación "%s" no reconodico para cálculos de depradación.' % tp_ec)

            depred[:, :, :, í_etps, :] = depred_etp

        # Reemplazar valores NaN con 0.
        depred[np.isnan(depred)] = 0

        # Ajustar por superficies
        np.multiply(depred, extrn['superficies'].reshape(depred.shape[0], 1, 1, 1, 1), out=depred)

        # Convertir depredación potencial por depredador a depredación potencial total (multiplicar por la población
        # de cada depredador). También multiplicamos por el paso de la simulación. 'depred' ahora está en unidades
        # del número total de presas comidas por cada tipo de depredador por unidad de tiempo.
        np.multiply(depred, np.multiply(pobs, paso)[..., np.newaxis], out=depred)

        # Ajustar por la presencia de varios depredadores (eje 3 = depredadores)
        probs_conj(depred, pesos=1, máx=pobs, eje=3)

        depred[np.isnan(depred)] = 0

        # Redondear (para evitar de comer, por ejemplo, 2 * 10^-5 moscas). NO usamos la función "np.round()", porque
        # esta podría darnos valores superiores a los límites establecidos por probs_conj() arriba.
        np.floor(depred, out=depred)

        # Depredación únicamente por presa (todos los depredadores juntos)
        depred_por_presa = np.sum(depred, axis=3)

        # Actualizar la matriz de poblaciones
        np.subtract(pobs, depred_por_presa, out=pobs)

        # Dividir las depredaciones entre las de depredación normal y las de infecciones
        depred_infec = np.zeros_like(depred)
        índs_parás, índs_víc = símismo.parasitoides['índices']
        depred_infec[..., índs_parás, índs_víc] = depred[..., índs_parás, índs_víc]
        depred_por_presa_sin_infec = np.subtract(depred_por_presa, np.sum(depred_infec, axis=3))

        # Para las depredaciones normales, es fácul quitarlas de los cohortes
        símismo._quitar_de_cohortes(muertes=depred_por_presa_sin_infec[..., símismo.índices_cohortes])

        # Para cada parasitoide...
        for n_parás, d_parás in símismo.parasitoides['adultos'].items():
            índ_entra = d_parás['n_entra']
            índ_recip = d_parás['n_fants'][:len(índ_entra)]
            símismo._quitar_de_cohortes(muertes=depred_infec[..., n_parás, símismo.índices_cohortes],
                                        í_don=índ_entra, í_recip=índ_recip)

            # Agregar las adiciones a las etapas fantasmas a la matriz de poblaciones general
            pobs[..., índ_recip] += depred_infec[..., n_parás, índ_entra]

    def _calc_crec(símismo, pobs, crec, extrn, paso):
        """
        Calcula las reproducciones y las transiciones de etapas de crecimiento

        :param pobs: Matriz numpy de poblaciones actuales. Eje 0 =
        :type pobs: np.ndarray

        :param extrn: Diccionario de factores externos a la red (plantas, clima, etc.)
        :type extrn: dict

        :param paso: El paso para la simulación.
        :type paso: int

        """

        tipos_ec = símismo.ecs['Crecimiento']['Ecuación']  # type: dict
        modifs = símismo.ecs['Crecimiento']['Modif']  # type: dict

        # Si no hay nada que hacer, devolver ahora
        if not len(tipos_ec):
            return

        coefs_ec = símismo.coefs_act_númzds['Crecimiento']['Ecuación']
        coefs_mod = símismo.coefs_act_númzds['Crecimiento']['Modif']

        if len(modifs):
            r = np.zeros_like(coefs_mod['r'])

        for mod, í_etps in modifs.items():

            cf = coefs_mod[mod]  # type: dict

            # Modificaciones ambientales a la taza de crecimiento intrínsica
            if mod == 'Ninguna':
                # Sin modificación a r.
                r[:, í_etps] = np.multiply(cf['r'], paso)

            elif mod == 'Log Normal Temperatura':
                # r responde a la temperatura con una ecuación log normal.
                r[:, í_etps] = (cf['r'] * paso) * mat.exp(-0.5 * (mat.log(extrn['temp_máx'] / cf['t']) / cf['p']) ** 2)

            else:
                raise ValueError

        # Calcular el crecimiento de la población
        for tp_ec, í_etps in tipos_ec.items():

            crec_etp = crec[:, :, :, í_etps]  # COPIA de la parte de la matriz "crec" de esta etapa.

            pobs_etps = pobs[:, :, :, í_etps]  # La población de esta etapa
            cf = coefs_ec[tp_ec]  # type: dict

            if tp_ec == 'Exponencial':
                # Crecimiento exponencial

                np.multiply(pobs_etps, r, out=crec_etp)

            elif tp_ec == 'Logístico':
                # Crecimiento logístico.

                np.multiply(r, pobs_etps * (1 - pobs_etps / cf['K']), out=crec_etp)  # Ecuación logística sencilla

            elif tp_ec == 'Logístico Presa':
                # Crecimiento logístico. 'K' es un parámetro repetido para cada presa de la etapa y indica
                # la contribución individual de cada presa a la capacidad de carga de esta etapa (el depredador).

                k = np.nansum(np.multiply(pobs, cf['K']), axis=3)  # Calcular la capacidad de carga
                np.multiply(r, pobs_etps * (1 - pobs_etps / k), out=crec_etp)  # Ecuación logística sencilla

                # Evitar péridadas de poblaciones superiores a la población.
                np.maximum(crec_etp, -pobs_etps, out=crec_etp)

            elif tp_ec == 'Logístico Depredación':
                # Crecimiento proporcional a la cantidad de presas que se consumió el depredador.

                depred = símismo.predics['Depred'][..., í_etps, :]  # La depredación por esta etapa
                k = np.nansum(np.multiply(depred, cf['K']), axis=3)  # Calcular la capacidad de carga
                np.multiply(r, pobs_etps * (1 - pobs_etps / k), out=crec_etp)  # Ecuación logística sencilla

                # Evitar péridadas de poblaciones superiores a la población.
                np.maximum(crec_etp, -pobs_etps, out=crec_etp)

            elif tp_ec == 'Constante':
                nueva_pob = cf['n']
                np.subtract(nueva_pob, pobs_etps, out=crec_etp)

            elif tp_ec == 'Externo Cultivo':
                # Esta ecuación guarda la población del organismo a un nivel constante, no importe qué esté pasando
                # en el resto de la red. Puede ser útil para representar plantas donde los herbívoros están bien
                # abajo de sus capacidades de carga.

                try:
                    np.subtract(extrn['Plantas'], pobs_etps, out=crec_etp)
                except (KeyError, TypeError):
                    # Si la planta no ha sido conectada a través de una parcela, no hacemos nada. Esto dejará un valor
                    # de 0 para la población de la planta.
                    pass

            else:
                raise ValueError('Ecuación de crecimiento "%s" no reconocida.' % tp_ec)

            crec[:, :, :, í_etps] = crec_etp

        crec[np.isnan(crec)] = 0

        np.floor(crec)

        # Actualizar la matriz de poblaciones
        np.add(pobs, crec, out=pobs)

    def _calc_edad(símismo, extrn, edades, paso):
        """

        :param extrn:
        :type extrn:
        :param paso:
        :type paso:

        """

        # Simplificamos el código un poco.
        edad_extra = edades

        tipos_edad = símismo.ecs['Edad']['Ecuación']  # type: dict
        coefs_ed = símismo.coefs_act_númzds['Edad']['Ecuación']  # type: dict

        # Para cada etapa que guarda cuenta de edades (es decir, cohortes)...
        for tp_ed, í_etps in tipos_edad.items():

            # Si hay que guardar cuenta de cohortes, hacerlo aquí
            cf_ed = coefs_ed[tp_ed]  # type: dict

            if tp_ed == 'Días':
                # Edad calculada en días.
                edad_extra[..., í_etps] = 1

            elif tp_ed == 'Días Grados':
                # Edad calculada por días grados.
                edad_extra[..., í_etps] = días_grados(extrn['temp_máx'], extrn['temp_mín'],
                                                 umbrales=(cf_ed['mín'], cf_ed['máx'])
                                                 )

            elif tp_ed == 'Brière Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura Briere. En esta ecuación,
                # tal como en las otras con taza de desarrollo, quitamos el parámetro típicamente multiplicado por
                # toda la ecuación, porque eso duplicaría el propósito del parámetro de ubicación de las distribuciones
                # de probabilidad empleadas después.
                #
                # Mokhtar, Abrul Monim y Salem Saif al Nabhani. 2010. Temperature-dependent development of dubas bug,
                #   Ommatissus lybicus (Hemiptera: Tropiduchidae), an endemic pest of date palm, Phoenix dactylifera.
                #   Eur. J. Entomol. 107: 681–685
                edad_extra[..., í_etps] = extrn['temp_prom'] * (extrn['temp_prom'] - cf_ed['t_dev_mín']) * \
                                        mat.sqrt(cf_ed['t_letal'] - extrn['temp_prom'])

            elif tp_ed == 'Brière No Linear Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura no linear de Briere.
                #
                # Youngsoo Son et al. 2012. Estimation of developmental parameters for adult emergence of Gonatocerus
                #   morgani, a novel egg parasitoid of the glassy-winged sharpshooter, and development of a degree-day
                #   model. Biological Control 60(3): 233-260.

                edad_extra[..., í_etps] = extrn['temp_prom'] * (extrn['temp_prom'] - cf_ed['t_dev_mín']) * \
                                        mat.pow(cf_ed['t_letal'] - extrn['temp_prom'], 1 / cf_ed['m'])

            elif tp_ed == 'Logan Temperatura':
                # Edad calculada con la taza de desarrollo de la ecuación de temperatura Logan:
                #
                # Youngsoo Son y Lewis, Edwin E. 2005. Modelling temperature-dependent development and survival of
                #   Otiorhynchus sulcatus (Coleoptera: Curculionidae). Agricultural and Forest Entomology 7(3): 201–209.

                edad_extra[..., í_etps] = mat.exp(cf_ed['rho'] * extrn['temp_prom']) - \
                                        mat.exp(cf_ed['rho'] * cf_ed['t_letal'] - (cf_ed['t_letal'] -
                                                                                   extrn['temp_prom'])
                                                / cf_ed['delta'])

            else:
                raise ValueError('No reconozco el tipo de ecuación "%s" para la edad.' % tp_ed)

        np.multiply(edad_extra, paso, out=edad_extra)

    def _calc_reprod(símismo, pobs, paso, reprod, depred):
        """
        Esta función calcula las reproducciones de las etapas.

        :param pobs: La matriz de poblaciones actuales de la red. Ejes tales como indicado arriba.
        :type pobs: np.ndarray

        :param paso: El paso para la simulación.
        :type paso: int

        """

        # Simplificamos el código un poco.
        tipos_probs = símismo.ecs['Reproducción']['Prob']  # type: dict

        coefs_pr = símismo.coefs_act_númzds['Reproducción']['Prob']

        # Iterar a través de los tipos de distribuciones de probabilidad activos
        for tp_prob, í_etps in tipos_probs.items():

            # Y ya pasamos a calcular el número de individuos de esta etapa que se reproducen en este paso de tiempo
            cf = coefs_pr[tp_prob]
            pob_etp = pobs[:, :, :, í_etps]

            # Una referencia a la parte apriopiada de la matriz de reproducciones
            n_recip = [símismo.orden['repr'][n] for n in í_etps]  # para hacer: simplificar
            repr_etp_recip = reprod[..., í_etps]

            if tp_prob == 'Constante':
                # Reproducciones en proporción al tamaño de la población.

                # Tomamos el paso en cuenta según las regals de probabilidad:
                #   p(x sucede n veces) = (1 - (1- p(x))^n)

                np.multiply(cf['n'] * pob_etp, (1 - (1 - cf['q']) ** paso), out=repr_etp_recip)

            elif tp_prob == 'Depredación':
                # Reproducciones en función de la depredación (útil para avispas esfécidas)
                np.sum(np.multiply(cf['n'], depred[..., í_etps, :]), axis=-1, out=repr_etp_recip)

            else:
                # Aquí tenemos todas las probabilidades de reproducción dependientes en distribuciones de cohortes:
                edad_extra = símismo.predics['Edades']

                símismo._trans_cohortes(cambio_edad=edad_extra[..., í_etps], etps=í_etps,
                                        dists=símismo.dists['Repr'][tp_prob],
                                        matr_egr=repr_etp_recip, quitar=False)

                np.multiply(cf['n'], repr_etp_recip, out=repr_etp_recip)

            reprod[..., n_recip] = repr_etp_recip

        # Redondear las reproducciones calculadas
        np.round(reprod, out=reprod)

        # Agregar las reproducciones a las poblaciones
        np.add(pobs, reprod, out=pobs)

        # Actualizar cohortes ahora, si necesario
        if len(símismo.índices_cohortes):
            símismo._añadir_a_cohortes(nuevos=reprod[..., símismo.índices_cohortes])

    def _calc_muertes(símismo, pobs, muertes, extrn, paso):

        """
        Esta función calcula las muertes de causas ambientales de la etapa.

        :param extrn: Un diccionario con las condiciones exógenas a la red
        :type extrn: dict

        :param pobs: La matriz de poblaciones actuales de la red. Ejes tales como indicado arriba.
        :type pobs: np.ndarray

        :param paso: El paso para la simulación.
        :type paso: int

        """

        # Simplificamos el código un poco.
        tipos_ec = símismo.ecs['Muertes']['Ecuación']  # type: dict

        if not len(tipos_ec):
            return

        coefs = símismo.coefs_act_númzds['Muertes']['Ecuación']

        for tp_ec, í_etps in tipos_ec.items():

            cf = coefs[tp_ec]
            muerte_etp = muertes[:, :, :, í_etps]
            pob_etp = pobs[:, :, :, í_etps]  # La población de estas etapas

            if tp_ec == 'Constante':
                # Muertes en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
                # exponencial.

                np.multiply(pob_etp, cf['q'], out=muerte_etp)

            elif tp_ec == 'Log Normal Temperatura':
                # Muertes dependientes en la temperatura, calculadas con la ecuación mencionada en:
                #
                # Sunghoon Baek, Youngsoo Son, Yong-Lak Park. 2014. Temperature-dependent development and survival of
                #   Podisus maculiventris (Hemiptera: Pentatomidae): implications for mass rearing and biological
                #   control. Journal of Pest Science 87(2): 331-340.

                sobrevivencia = mat.exp(-0.5 * (mat.log(extrn['temp_máx'] / cf['t']) / cf['p']) ** 2)
                np.multiply(pob_etp, (1 - sobrevivencia), out=muerte_etp)

            elif tp_ec == 'Asimptótico Humedad':

                # M. P. Lepage, G. Bourgeois, J. Brodeur, G. Boivin. 2012. Effect of Soil Temperature and Moisture on
                #   Survival of Eggs and First-Instar Larvae of Delia radicum. Environmental Entomology 41(1): 159-165.

                sobrevivencia = np.maximum([0], np.subtract(1, mat.exp(-cf['a'] * (extrn['humedad'] - cf['b']))))
                np.multiply(pob_etp, (1 - sobrevivencia), out=muerte_etp)

            elif tp_ec == 'Sigmoidal Temperatura':

                sobrevivencia = 1 / (1 + mat.exp((extrn['temp_máx'] - cf['a']) / cf['b']))
                np.multiply(pob_etp, (1 - sobrevivencia), out=muerte_etp)

            else:
                raise ValueError

            muertes[:, :, :, í_etps] = muerte_etp

        np.multiply(muertes, paso, out=muertes)
        np.round(muertes, out=muertes)

        # Actualizar los cohortes ahora, si necesario.
        if len(símismo.índices_cohortes):
            símismo._quitar_de_cohortes(muertes[..., símismo.índices_cohortes])

        # Actualizar la matriz de predicciones
        np.subtract(pobs, muertes, out=pobs)

    def _calc_trans(símismo, pobs, paso, trans):
        """
        Esta función calcula las transiciones de organismos de una etapa a otra. Esto puede incluir muerte por
          viejez.

        :param pobs:
        :type pobs: np.ndarray

        :param paso:
        :type paso: int

        """

        # Simplificamos el código un poco.
        tipos_probs = símismo.ecs['Transiciones']['Prob']  # type: dict
        tipos_mult = símismo.ecs['Transiciones']['Mult']  # type: dict

        coefs_pr = símismo.coefs_act_númzds['Transiciones']['Prob']
        coefs_mt = símismo.coefs_act_númzds['Transiciones']['Mult']

        for tp_prob, í_etps in tipos_probs.items():

            # Y ya pasamos a calcular el número de individuos de esta etapa que se transicionan en este paso de tiempo
            cf = coefs_pr[tp_prob]

            # Una COPIA de la parte apriopiada de la matriz de transiciones
            trans_etp = trans[..., í_etps]

            if tp_prob == 'Constante':
                # Transiciones en proporción al tamaño de la población. Sin crecimiento, esto da una decomposición
                # exponencial.

                # Tomamos el paso en cuenta según las regals de probabilidad:
                #   p(x sucede n veces) = (1 - (1- p(x))^n)

                np.multiply(pobs, (1 - (1 - cf['q']) ** paso), out=trans_etp)

            else:
                # Aquí tenemos todas las probabilidades de muerte dependientes en distribuciones de cohortes:
                edad_extra = símismo.predics['Edades']

                símismo._trans_cohortes(cambio_edad=edad_extra[..., í_etps], etps=í_etps,
                                        dists=símismo.dists['Trans'][tp_prob],
                                        matr_egr=trans_etp)

            trans[..., í_etps] = trans_etp

        # Redondear las transiciones calculadas
        np.floor(trans, out=trans)

        # Quitar los organismos que transicionaron
        np.subtract(pobs, trans, out=pobs)

        # Posibilidades de transiciones multiplicadoras (por ejemplo, la eclosión de parasitoides)
        for tp_mult, í_etps in tipos_mult.items():
            if tp_mult == 'Linear':
                trans[..., í_etps] *= coefs_mt[tp_mult]['a']
            else:
                raise ValueError('Tipo de multiplicación "{}" no reconocida.'.format(tp_mult))

        # Si no eran adultos muríendose por viejez, añadirlos a la próxima etapa también
        orden_recip = símismo.orden['trans']
        nuevos = np.zeros_like(trans)

        for i in range(len(símismo.etapas)):
            i_recip = orden_recip[i]
            if i != -1:
                nuevos[..., i_recip] += trans[..., i]

        np.add(pobs, nuevos, out=pobs)

        if len(símismo.índices_cohortes):
            símismo._añadir_a_cohortes(nuevos=nuevos[..., símismo.índices_cohortes])

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

        coefs = símismo.coefs_act_númzds['Movimiento']

        for ec in tipos_ec:
            mobil = NotImplemented
            modif_peso = NotImplemented
            superficie = NotImplemented
            peso = superficie * modif_peso

            mov = NotImplemented

        edades = NotImplemented
        # Si la etapa usa cohortes para cualquier otro cálculo, acutlizar los cohortes ahora.
        símismo._añadir_a_cohortes(nuevos=mov, edad=edades)

        # Actualizar la matriz de predicciones
        pobs += mov

    def _inic_pobs_const(símismo):

        # Llenar poblaciones iniciales manualmente para organismos con poblaciones fijas.
        for n_etp in range(len(símismo.etapas)):

            dic = símismo.ecs['Crecimiento']['Ecuación']
            if 'Constante' in dic.keys() and n_etp in dic['Constante']:
                # Si la etapa tiene una población constante...

                # La población inicial se determina por el coeficiente de población constante del organismo
                pobs_inic = símismo.coefs_act_númzds['Crecimiento']['Ecuación']['Constante']['n'][:, n_etp]

                # Guardamos las poblaciones iniciales en la matriz de predicciones de poblaciones.
                símismo.predics['Pobs'][..., n_etp, 0] = pobs_inic

    def incrementar(símismo, paso, i, detalles, mov=False, extrn=None):

        # Empezar con las poblaciones del paso anterior
        símismo.predics['Pobs'][..., i] = símismo.predics['Pobs'][..., i - 1]
        pobs = símismo.predics['Pobs'][..., i]

        # Especificar las matrices de depredación, crecimiento, etc.
        if detalles:
            depred = símismo.predics['Depredación'][..., i]
            crec = símismo.predics['Crecimiento'][..., i]
            muertes = símismo.predics['Muertes'][..., i]
            trans = símismo.predics['Transiciones'][..., i]
            reprod = símismo.predics['Reproducción'][..., i]

        else:
            depred = símismo.predics['Depredación']
            crec = símismo.predics['Crecimiento']
            muertes = símismo.predics['Muertes']
            trans = símismo.predics['Transiciones']
            reprod = símismo.predics['Reproducción']

        edades = símismo.predics['Edades']

        # Calcular la depredación, crecimiento, reproducción, muertes, transiciones, y movimiento entre parcelas
        # Una especie que mata a otra.
        símismo._calc_depred(pobs=pobs, paso=paso, depred=depred, extrn=extrn)

        # Una población que crece (misma etapa)
        símismo._calc_crec(pobs=pobs, extrn=extrn, crec=crec, paso=paso)

        # Muertes por el ambiente
        símismo._calc_muertes(pobs=pobs, muertes=muertes, extrn=extrn, paso=paso)

        # Calcular cambios de edades
        símismo._calc_edad(extrn=extrn, paso=paso, edades=edades)

        # Una etapa que cambia a otra, o que se muere por su edad.
        símismo._calc_trans(pobs=pobs, paso=paso, trans=trans)

        # Una etapa que se reproduce para producir más de otra etapa
        símismo._calc_reprod(pobs=pobs, paso=paso, reprod=reprod, depred=depred)

        if mov:
            # Movimientos de organismos de una parcela a otra.
            símismo._calc_mov(pobs=pobs, extrn=extrn, paso=paso)

        # Ruido aleatorio; Para hacer: formalizar el proceso de agregación de ruido aleatorio
        símismo._agregar_ruido(pobs=pobs, ruido=0.01)

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

        # Convertir poblaciones a unidades de organismos por hectárea
        tamaño_superficies = símismo.info_exps['superficies'][exp]  # type: np.ndarray
        np.divide(matr_predics, tamaño_superficies.reshape((tamaño_superficies.shape[0], 1, 1, 1, 1)), out=matr_predics)

        # Primero, vamos a sacar vectores para cada etapa de la red
        for org, d_org in símismo.núms_etapas.items():

            # Agregar el organismo al diccionario de resultados
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
                    matr_preds_etp += np.sum([matr_predics[..., x, :] for x in símismo.fantasmas[n_etp].values()],
                                             axis=0)

                if n_etp in símismo.parasitoides['juvs']:
                    n_adulto = símismo.parasitoides['juvs'][n_etp]
                    d_paras = símismo.parasitoides['adultos'][n_adulto]  # type: dict
                    matr_preds_etp += np.sum([matr_predics[..., x, :] for x in d_paras['n_fants']],
                                             axis=0)

                dic_vecs[org][etp]['preds'] = matr_preds_etp

                # El diccionario de observaciones y de tiempos del Experimento
                dic_obs = símismo.exps[exp]['Exp'].datos['Organismos']['obs']
                tiempos_obs = símismo.exps[exp]['Exp'].datos['Organismos']['tiempo']

                # Ahora, el vector de observaciones. (Es un poco más complicado.)
                if n_etp in etps_interés:
                    # Si hay observaciones para esta etapa...

                    # Los nombre de las columnas y el nombre de la columna de datos que nos interesa
                    nombres_cols = símismo.info_exps['nombres_cols'][exp]
                    nombre_col = nombres_cols[np.where(etps_interés == n_etp)[0][0]]

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
                        matr_preds_etp += np.sum([matr_predics[..., x, :]
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
        No hay nada nada que hacer, visto que una Red no tiene coeficientes propios.
        """

        return []

    def _actualizar_vínculos_exps(símismo):
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

        """

        for categ_info in símismo.info_exps.values():
            categ_info.clear()

        # Para cada experimento que está vinculado con la Red...
        for nombre_exp, d in símismo.exps.items():

            # El objeto y diccionario de correspondencias del experimento
            obj_exp = d['Exp']
            corresp = d['Corresp'].copy()  # Hacer una copia, en caso que tengamos que quitarle unos organismos

            # Guardar el tamaño de las parcelas
            n_parc = len(obj_exp.datos['Parcelas'])
            if n_parc > 0:
                # Para hacer para poder incluir especificaciones de características de parcelas en Experimento
                raise NotImplementedError()
            else:
                avisar('Tamaño de parcelas no especificado. Se supondrá un tamaño de 1 ha.')
                símismo.info_exps['superficies'][nombre_exp] = np.ones(1)

            # Verificar que los nombres de organismos y etapas estén correctos
            for org in list(corresp):
                d_org = corresp[org]
                if org not in símismo.receta['estr']['Organismos']:
                    # Si el organismo no existe en la Red, avisar el usuario y borrarlo del diccionario de
                    # correspondencias
                    avisar('El organismo "%s" no existe en la red. '
                           'Se excluirá del experimento %s.' % (org, nombre_exp))
                    corresp.pop(org)

                for etp in list(d_org):
                    if etp not in símismo.núms_etapas[org]:
                        # Si la etapa no existe para el organismo, avisar el usuario y borrarla del diccionario de
                        # correspondencias
                        avisar('Organismo "%s" no tiene etapa "%s". Se excluirá del experimento %s.' %
                               (org, etp, nombre_exp))
                        d_org.pop(etp)

            # Crear las llaves para este experimento en el diccionario de formatos de la Red, y simplificar el código.
            símismo.info_exps['etps_interés'][nombre_exp] = None
            símismo.info_exps['ubic_obs'][nombre_exp] = ()
            l_nombres_cols = símismo.info_exps['nombres_cols'][nombre_exp] = []
            d_comunes = símismo.info_exps['combin_etps'][nombre_exp] = {}

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
                    # código no hará ninguna transformación a los datos o el nombre de la columna en el caso que
                    # solamente haya una columna de datos correspondiento a la etapa.

                    # El nombre de la nueva columna sumada (en el caso donde l_cols tiene una sola columna, no cambia
                    # nada)
                    nombre_col = '&'.join(str(x) for x in sorted(l_cols))

                    # Hacer la suma (otra vez, no hace nada si l_cols solamente tiene una columna).
                    suma = np.sum([obj_exp.datos['Organismos']['obs'][x] for x in l_cols], axis=0)

                    # Guardar la nueva columna en el Experimento
                    obj_exp.datos['Organismos']['obs'][nombre_col] = suma

                    # El número de la etapa en la Red
                    n_etp = símismo.núms_etapas[org][etp]

                    # Verificar ahora para etapas cuyas predicciones hay que combinar
                    if nombre_col in l_nombres_cols:
                        # Si ya había otra etapa con estos mismo datos...

                        # Buscar el número de la otra etapa
                        n_otra_etp = l_etps_interés[l_nombres_cols.index(nombre_col)]

                        # Si es la primera vez que la otra etapa se desdoble, agregar su número como llave al
                        # diccionario.
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
                        obs_etp = obj_exp.datos['Organismos']['obs'][nombre_col]

                        for n_p in range(obs_etp.shape[0]):
                            obs_etp_parc = obs_etp[n_p, :]

                            # Días con observaciones
                            días_con_obs = obj_exp.datos['Organismos']['tiempo'][~np.isnan(obs_etp_parc.flatten())]
                            ubic_obs_días = np.concatenate((ubic_obs_días, días_con_obs))

                            # Guardar una matriz de forma correspondiente con el número de la etapa:
                            etps_con_obs = np.full(shape=len(días_con_obs), fill_value=n_etp, dtype=int)
                            ubic_obs_etps = np.concatenate((ubic_obs_etps, etps_con_obs))

                            # Y una matriz con los las parcelas con observaciones
                            parc_con_obs = np.full(shape=len(días_con_obs), fill_value=n_p, dtype=int)
                            ubic_obs_parc = np.concatenate((ubic_obs_parc, parc_con_obs))

            # Convertir a matrices numpy
            símismo.info_exps['etps_interés'][nombre_exp] = np.array(l_etps_interés)
            símismo.info_exps['ubic_obs'][nombre_exp] = (ubic_obs_parc, ubic_obs_etps, ubic_obs_días)

            # Agregar la lista de nombres de parcelas, en el orden que aparecen en las matrices de observaciones:
            símismo.info_exps['parcelas'][nombre_exp] = obj_exp.datos['Organismos']['parcelas']

    def _procesar_predics_calib(símismo):
        """
        Ver la documentación de Simulable.

        :rtype: np.ndarray

        """

        vector_predics = np.array([])

        # Para cada experimento simulado, en orden...
        for nombre, predic in sorted(símismo.predics_exps.items()):

            # Convertir poblaciones a unidades de organismos por hectárea
            tamaño_superficies = símismo.info_exps['superficies'][nombre]
            np.divide(predic['Pobs'], tamaño_superficies, out=predic['Pobs'])

            # La combinaciones de etapas necesarias para procesar los resultados.
            # Tiene el formato general: {exp: {{1: [3,4, etc.]}, etc...], ...}
            combin_etps = símismo.info_exps['combin_etps'][nombre]

            # La ubicación de los datos observados
            ubic_obs = símismo.info_exps['ubic_obs'][nombre]  # type: tuple

            # Combinar las etapas que lo necesitan
            for i, fants in símismo.fantasmas.items():  # Combinaciones automáticas
                índ_fant = list(fants.values())  # Los índices de las etapas fantasmas
                predic['Pobs'][..., i, :] += np.sum(predic['Pobs'][..., índ_fant, :], axis=3)
            for i in combin_etps:  # Combinaciones basadas en los datos disponibles
                predic['Pobs'][..., i, :] += np.sum(predic['Pobs'][..., combin_etps[i], :], axis=3)

            # Sacar únicamente las predicciones que corresponden con los datos observados disponibles
            vector_predics = np.concatenate((vector_predics,
                                             predic['Pobs'][ubic_obs[0], :, :, ubic_obs[1], ubic_obs[2]].flatten()))

        return vector_predics

    def _prep_args_simul_exps(símismo, exper, n_rep_estoc, n_rep_paráms, tiempo_final, detalles):
        """
        Ver la documentación de Coso.

        :type exper: list[str]
        :type n_rep_estoc: int
        :type n_rep_paráms: int
        :type tiempo_final: dict | None
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
            try:
                obj_exp = símismo.exps[exp]['Exp']
            except KeyError:
                raise ValueError('El experimento "{}" no está vinculado con esta Red.'.format(exp))

            # Calculamos el número de parcelas en el experimento
            n_parc = len(símismo.info_exps['parcelas'][exp])

            # La superficie de cada parcela (en ha)
            tamaño_parcelas = símismo.info_exps['superficies'][exp]

            # El número de pasos necesarios es la última observación en la base de datos de organismos o el valor
            # especificado.
            if tiempo_final is None:
                n_pasos = int(obj_exp.datos['Organismos']['tiempo'][-1] + 1)
            else:
                n_pasos = tiempo_final[exp]

            # Generamos el diccionario (vacío) de datos iniciales
            n_cohs = len(símismo.índices_cohortes)
            datos_inic = símismo._gen_dic_matr_predic(n_parc=n_parc, n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_paráms,
                                                      n_etps=n_etapas, n_pasos=n_pasos,
                                                      n_cohs=n_cohs,
                                                      detalles=detalles)

            # Una lista de las poblaciones iniciales ajustadas (tomando en cuenta columnas de datos compartidas)
            l_pobs_inic = [None] * len(símismo.etapas)
            combin_etps = símismo.info_exps['combin_etps'][exp]

            for i, n_etp in enumerate(símismo.info_exps['etps_interés'][exp]):  # type: int
                # Para cada etapa de interés...

                # La matriz de datos iniciales para una etapa. Eje 0 = parcela, eje 1 = tiempo. Quitamos el eje 1.
                nombre_col = símismo.info_exps['nombres_cols'][exp][i]
                matr_obs_inic = obj_exp.datos['Organismos']['obs'][nombre_col][:, 0]

                # Convertir a unidades de organismos por parcela
                # Para hacer: URGENTE: esto debe arreglarse en Experimento directamente
                np.multiply(matr_obs_inic, tamaño_parcelas, out=matr_obs_inic)

                # Asegurarse que tenemos números enteros.
                matr_obs_inic = matr_obs_inic.astype(int)

                if n_etp not in combin_etps:
                    # Si la etapa no comparte datos...

                    l_pobs_inic[n_etp] = matr_obs_inic

                else:
                    # ...sino, si la etapa tiene una columna compartida

                    # Los índices de las etapas compartidas con esta, incluyendo esta
                    etps_compart = [n_etp] + combin_etps[n_etp]

                    # Una división igual de la población inicial
                    div = np.floor(np.divide(matr_obs_inic, len(etps_compart)))

                    # El resto
                    resto = np.remainder(matr_obs_inic, len(etps_compart))

                    for j, n in enumerate(etps_compart):
                        l_pobs_inic[n] = np.add(div, np.less(j, resto))

            # Ahora, podemos llenar la poblaciones iniciales en la matriz de poblaciones
            for i, n_etp in enumerate(símismo.info_exps['etps_interés'][exp]):  # type: int
                # Para cada etapa de interés...

                # La matriz de poblaciones
                matr_obs_inic = l_pobs_inic[n_etp]

                # Llenamos la población inicial y los cohortes. Llenamos eje 0 (parcela), eje 1 y 2 (repeticiones
                # estocásticas y paramétricas) de la etapa en cuestión (eje 3) a tiempo 0 (eje 4).

                org = símismo.organismos[símismo.etapas[n_etp]['org']]
                etp = símismo.etapas[n_etp]['nombre']
                juvenil_paras = isinstance(org, Ins.Parasitoide) and etp == 'juvenil'

                if not juvenil_paras:
                    # Si la etapa no es la larva de un parasitoide...

                    # Agregarla directamente al diccionario de poblaciones iniciales
                    datos_inic['Pobs'][..., n_etp, 0] = matr_obs_inic[:, np.newaxis, np.newaxis]

                else:
                    # ...pero si la etapa es una larva de parasitoide, es un poco más complicado. Hay que dividir
                    # sus poblaciones entre las etapas fantasmas, y, además, hay que quitar estos valores de las
                    # poblaciones de las víctimas.

                    # Primero, tenemos que hacer unas aproximaciones para estimar cuántos de estas larvas
                    # están en cada etapa de la víctima potencialmente infectada.

                    # Una lista de las etapas potencialmente hospederas de TODAS las víctimas del parasitoide.
                    l_etps_víc = [víc for víc, d in símismo.fantasmas.items() if org.nombre in d]
                    n_etps_víc = len(l_etps_víc)

                    # Una lista de las etapas fantasmas correspondientes
                    l_etps_fant = [d[org.nombre] for d in símismo.fantasmas.values() if org.nombre in d]

                    # Calcular el total de las poblaciones iniciales de todas las etapas víctimas no infectadas.
                    l_pobs_víc = np.array([l_pobs_inic[j] for j in l_etps_víc])
                    pobs_total_etps_víc = np.sum(l_pobs_víc, axis=0)

                    if np.sum(matr_obs_inic > pobs_total_etps_víc):
                        # Si hay más juveniles de parasitoides que de etapas potencialmente hospederas en cualquier
                        # parcela, hay un error.
                        raise ValueError('Tenemos una complicacioncita con los datos inicales para el experimento'
                                         '"{}". No es posible tener más poblaciones iniciales de juveniles'
                                         'de parasitoides que hay indivíduos de etapas potencialmente hospederas.')

                    # Dividir la población del parasitoide juvenil entre las etapas fantasmas, según las
                    # poblaciones iniciales de las etapas víctimas (no infectadas) correspondientes

                    # Una matriz de poblaciones iniciales. eje 0 = etp víctima, eje 1 = parcela
                    matr_pobs_etps_fant = np.zeros((n_etps_víc, *matr_obs_inic.shape), dtype=int)

                    # Empleamos un método iterativo para distribuir las infecciones entre las etapas potencialmente
                    # infectadas (etapas víctimas). No es muy elegante, pero es lo único que encontré que parece
                    # funcionar. Si tienes mejor idea, por favor no hesites en ayudar aquí.

                    copia_matr = matr_obs_inic.copy()  # Para no cambiar los datos del Experimento sí mismo

                    matr_pobs_etps_fant_cum = np.cumsum(l_pobs_víc[::-1], axis=0)[::-1]

                    for v in range(n_etps_víc):

                        p = np.divide(copia_matr, matr_pobs_etps_fant_cum[v])

                        # Alocar según una distribución binomial
                        aloc = np.minimum(np.random.binomial(l_pobs_víc[v], p), copia_matr)
                        if v < n_etps_víc - 1:
                            aloc = np.maximum(aloc, copia_matr - matr_pobs_etps_fant_cum[v + 1])
                        else:
                            aloc = np.maximum(aloc, copia_matr)

                        # Agregar las alocaciones a la matriz
                        matr_pobs_etps_fant[v] += aloc

                        # Quitar las alocaciones de las poblaciones que quedan a alocar
                        copia_matr -= aloc

                    # Dar las poblaciones iniciales apropiadas
                    for n_etp_víc, n_etp_fant, pobs in zip(l_etps_víc, l_etps_fant, matr_pobs_etps_fant):
                        # Agregar a la población de la etapa fantasma
                        datos_inic['Pobs'][..., n_etp_fant, 0] += pobs

                        # Quitar de la población de la etapa víctima (no infectada) correspondiente.
                        datos_inic['Pobs'][..., n_etp_víc, 0] -= pobs

            # Ahora, inicializamos los cohortes.
            símismo._añadir_a_cohortes(dic_predic=datos_inic,
                                       nuevos=datos_inic['Pobs'][..., símismo.índices_cohortes, 0])

            # Las poblaciones iniciales de organismos con poblaciones constantes se actualizarán antes de cada
            # simulación.

            # Y, por fin, guardamos este diccionario bajo la llave "datos_inic" del diccionario.
            dic_args['datos_inic'][exp] = datos_inic

            # También guardamos el número de pasos y las superficies de las parcelas.
            dic_args['n_pasos'][exp] = n_pasos
            dic_args['extrn'][exp] = {'superficies': símismo.info_exps['superficies'][exp]}

        return dic_args

    def _llenar_coefs(símismo, n_rep_parám, calibs, comunes, usar_especificadas):
        """
        Ver la documentación de Coso.

        :type n_rep_parám: int
        :type calibs: list | str
        :type comunes: bool
        :type usar_especificadas: bool

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

                # Crear una llave correspondiente en coefs_act
                símismo.coefs_act[categ][subcateg] = {}

                # Para cada tipo de ecuación activa para esta subcategoría...
                for tipo_ec, índs_etps in símismo.ecs[categ][subcateg].items():

                    # Crear una diccionario en coefs_act para de los parámetros de cada etapa
                    coefs_act = símismo.coefs_act[categ][subcateg][tipo_ec] = {}

                    # Para cada parámetro en el diccionario de las ecuaciones activas de esta etapa
                    # (Ignoramos los parámetros para ecuaciones que no se usarán en esta simulación)...
                    for parám, d_parám in Ec.ecs_orgs[categ][subcateg][tipo_ec].items():

                        # El tamaño de la matriz de parámetros
                        if d_parám['inter'] is None:
                            # Si no hay interacciones, # Eje 0: repetición paramétrica, eje 1: etapa
                            tamaño_matr = (n_rep_parám, len(índs_etps))
                        else:
                            # Pero si hay interacciones...
                            # Eje 0: repetición paramétrica, eje 1: etapa, eje 2: etapa con la cuál hay la interacción.
                            tamaño_matr = (n_rep_parám, len(índs_etps), n_etapas)

                        # La matriz de parámetros
                        coefs_act[parám] = np.empty(tamaño_matr, dtype=object)
                        coefs_act[parám][:] = np.nan

                        # Para cada etapa en la lista de diccionarios de parámetros de interés de las etapas...
                        for i, n_etp in enumerate(índs_etps):  # type: int

                            matr_etp = coefs_act[parám][:, i, ...]

                            # El diccionario del parámetro en los coeficientes de la etapa
                            d_parám_etp = símismo.etapas[n_etp]['coefs'][categ][subcateg][tipo_ec][parám]

                            # Si no hay interacciones entre este parámetro y otras etapas...
                            if d_parám['inter'] is None:
                                # Generar la matríz de valores para este parámetro de una vez

                                matr_etp[:] = gen_vector_coefs(dic_parám=d_parám_etp, calibs=calibs,
                                                               n_rep_parám=n_rep_parám,
                                                               comunes=comunes,
                                                               usar_especificados=usar_especificadas)

                            else:
                                # Si, al contrario, hay interacciones...

                                for tipo_inter in d_parám['inter']:

                                    if tipo_inter == 'presa' or tipo_inter == 'huésped':

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

                                                # Incluir etapas fantasmas, pero NO para parasitoides (así que una etapa
                                                # fantasma puede caer víctima de un deprededor o de una enfermedad que
                                                # se ataca la etapa no infectada correspondiente, pero NO puede caer
                                                # víctima de otro (o del mismo) parasitoide que afecta la etapa
                                                # original.
                                                l_etps_víc = [n_etp_víc]
                                                if n_etp_víc in símismo.fantasmas:
                                                    obj_org = símismo.organismos[símismo.etapas[n_etp]['org']]
                                                    if not isinstance(obj_org, Ins.Parasitoide):
                                                        l_etps_víc += list(símismo.fantasmas[n_etp_víc].values())

                                                for n in l_etps_víc:
                                                    matr_etp[:, n] = gen_vector_coefs(
                                                        dic_parám=d_parám_etp[org_víc][etp_víc],
                                                        calibs=calibs,
                                                        n_rep_parám=n_rep_parám,
                                                        comunes=comunes,
                                                        usar_especificados=usar_especificadas)

                                    else:
                                        # Al momento, solamente es posible tener interacciones con las presas de la
                                        # etapa. Si un día alguien quiere incluir más tipos de interacciones (como, por
                                        # ejemplo, interacciones entre competidores), se tendrían que añadir aquí.
                                        raise ValueError('Interacción "%s" no reconocida.' % tipo_inter)

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
                datos_etp = símismo.exps[exp]['Exp'].datos['Organismos']['obs'][nombre_col]

                # Guardar los datos aplastados en una única dimensión de matriz numpy (esto combina las dimensiones
                # de parcela (eje 0) y de tiempo (eje 1). También quitamos valores no disponibles (NaN).
                lista_obs.append(datos_etp[~np.isnan(datos_etp)].flatten())

        return np.concatenate(lista_obs)

    @staticmethod
    def _gen_dic_matr_predic(n_parc, n_rep_estoc, n_rep_parám, n_etps, n_pasos, n_cohs, detalles, n_grupos_coh=10):
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

        :param n_cohs: El número de etapas con cohortes para algo.
        :type n_cohs: int

        :param n_grupos_coh: El número de categorías de edad distintas en cada cohorte.
        :type n_grupos_coh: int

        :return: Un diccionario del formato de símismo.predics según las especificaciones en los argumentos de la
        función.
        :rtype: dict
        """

        # Tamaño estándardes para matrices de resultados (algunos resultados tienen unas dimensiones adicionales).
        if detalles:
            tamaño_normal = (n_parc, n_rep_estoc, n_rep_parám, n_etps, n_pasos)
            tamaño_pobs = tamaño_normal
            tamaño_depr = (n_parc, n_rep_estoc, n_rep_parám, n_etps, n_etps, n_pasos)
        else:
            tamaño_normal = (n_parc, n_rep_estoc, n_rep_parám, n_etps)
            tamaño_pobs = (n_parc, n_rep_estoc, n_rep_parám, n_etps, n_pasos)
            tamaño_depr = (n_parc, n_rep_estoc, n_rep_parám, n_etps, n_etps)

        tamaño_edades = (n_parc, n_rep_estoc, n_rep_parám, n_etps)

        # El diccionario en formato símismo.predics
        dic = {'Pobs': np.zeros(shape=tamaño_pobs),
               'Depredación': np.zeros(shape=tamaño_depr),
               'Crecimiento': np.zeros(shape=tamaño_normal),
               'Edades': np.zeros(shape=tamaño_edades),
               'Reproducción': np.zeros(shape=tamaño_normal),
               'Muertes': np.zeros(shape=tamaño_normal),
               'Transiciones': np.zeros(shape=tamaño_normal),
               'Movimiento': np.zeros(shape=tamaño_normal),
               'Cohortes': {},
               'Matrices': {
                   'í_ejes_cohs': (),  # Para la función de agregar a cohortes.
                   'tmñ_para_cohs': (n_parc, n_rep_estoc, n_rep_parám, n_cohs)  # Para la función de agregar a cohortes.
               }  # Para guardar matrices para cálculos internos
               }

        # Agregar cohortes. Todas las matrices de cohortes tienen el mismo orden de eje:
        #   Eje 0: Cohorte
        #   Eje 1: Parcela
        #   Eje 2: Repetición estocástica
        #   Eje 3: Repetición paramétrica
        #   Eje 4: Etapa

        if n_cohs > 0:
            # Si hay etapas con cohortes...

            cohortes = dic['Cohortes']

            # Generar la matriz de poblaciones para todas las etapas con cohortes
            cohortes['Pobs'] = np.zeros(shape=(n_grupos_coh, n_parc, n_rep_estoc, n_rep_parám, n_cohs))

            # ...y generar la matriz de edades
            cohortes['Edades'] = np.zeros(shape=(n_grupos_coh, n_parc, n_rep_estoc, n_rep_parám, n_cohs))

            í_ejes_cohs = (np.repeat(range(n_parc), n_rep_estoc * n_rep_parám * n_cohs),
                           np.tile(np.repeat(range(n_rep_estoc), n_rep_parám * n_cohs), [n_parc]),
                           np.tile(np.repeat(range(n_rep_parám), n_cohs), [n_parc * n_rep_estoc]),
                           np.tile(range(n_cohs), [n_parc * n_rep_estoc * n_rep_parám])
            )

            dic['Matrices']['í_ejes_cohs'] = í_ejes_cohs

        return dic

    def especificar_apriori(símismo, **kwargs):
        """
        Una Red no tiene parámetros para especificar.
        """
        raise NotImplementedError('No hay parámetros para especificar en una Red.')

    def _agregar_ruido(símismo, pobs, ruido):
        """

        :param pobs:
        :type pobs: np.ndarray
        :param ruido:
        :type ruido: float
        """

        # Una distribución normal
        ruido = np.round(np.random.normal(0, np.maximum(1, pobs * ruido)))

        # Verificara que no quitamos más que existen
        ruido = np.where(-ruido > pobs, -pobs, ruido)

        # Aplicar el cambio
        np.add(ruido, pobs, out=pobs)

        # Actualizar los cohortes
        símismo._ajustar_cohortes(cambio=ruido[..., símismo.índices_cohortes])

    def _justo_antes_de_simular(símismo):
        """
        Esta función hace cosas que hay que hacer justo antes de cada simulación (en particular, cosas que tienen
        que ver con los valores de los parámetros, pero que no hay que hacer a cada paso de la simulación.

        """

        # Primero, vamos a crear unas distribuciones de SciPy para las probabilidades de transiciones y de
        # reproducciones. Si no me equivoco, accelerará de manera importante la ejecución del programa.
        símismo._prep_dists()

        # Ahora, iniciar las poblaciones de organismos con poblaciones fijas
        símismo._inic_pobs_const()

    def _prep_dists(símismo):
        """
        Esta función inicializa los diccionarios de distribuciones de la Red.
        """

        # Inicializar los diccionarios de distribuciones
        símismo.dists['Trans'].clear()
        símismo.dists['Repr'].clear()

        # Para transiciones y para reproducciones...
        for categ, corto in zip(['Transiciones', 'Reproducción'], ['Trans', 'Repr']):

            # Para cada tipo de distribución...
            for tp_dist, í_etps in símismo.ecs[categ]['Prob'].items():

                if tp_dist not in ['Nada', 'Constante']:
                    # Si el tipo de distribución merece una distribución de SciPy...

                    # Los parámetros, numerizados, de la distribución
                    paráms_dist = símismo.coefs_act_númzds[categ]['Prob'][tp_dist]

                    # Convertir los parámetros a formato SciPy
                    if tp_dist == 'Normal':
                        paráms = dict(loc=paráms_dist['mu'], scale=paráms_dist['sigma'])
                    elif tp_dist == 'Triang':
                        paráms = dict(loc=paráms_dist['a'], scale=paráms_dist['b'], c=paráms_dist['c'])
                    elif tp_dist == 'Cauchy':
                        paráms = dict(loc=paráms_dist['u'], scale=paráms_dist['f'])
                    elif tp_dist == 'Gamma':
                        paráms = dict(loc=paráms_dist['u'], scale=paráms_dist['f'], a=paráms_dist['a'])
                    elif tp_dist == 'T':
                        paráms = dict(loc=paráms_dist['mu'], scale=paráms_dist['sigma'], df=paráms_dist['k'])
                    else:
                        raise ValueError('La distribución "{}" no tiene definición.'.format(tp_dist))

                    # Guardar la distribución multidimensional en el diccionario de distribuciones.
                    símismo.dists[corto][tp_dist] = Ds.dists[tp_dist]['scipy'](**paráms)

    def _trans_cohortes(símismo, cambio_edad, etps, dists, matr_egr, quitar=True):
        """
        Esta funcion maneja transiciones desde cohortes (basadas en edades).

        :param cambio_edad: Una matriz multidimensional con los cambios en las edades de cada cohorte de la etapa.
        Notar que la edad puede ser 'edad' en el sentido tradicional del término, tanto como la 'edad' del organismo
        medida por otro método (por ejemplo, exposición cumulativo a días grados). Los ejes son iguales que en 'pobs'.
        :type cambio_edad: np.ndarray

        :param etps: Los índices de las etapas (en la lista de etapas de la Red) que estamos transicionando ahora.
        :type etps: list

        :param dists: Una distribución con parámetros en forma de matrices.
        :type dists: estad._distn_infrastructure.rv_frozen.

        :param matr_egr: Una matriz en la cual guardar los resultados.
        :type matr_egr: np.ndarray

        :param quitar: Si hay que quitar las etapas que transicionaron (útil para cálculos de reproducción).
        :type quitar: bool

        """

        # Los índices (en la matriz de cohortes) de las etapas que transicionan.
        í_etps_coh = [símismo.índices_cohortes.index(x) for x in etps]

        # Las edades y las poblaciones actuales de estas etapas.
        edades = símismo.predics['Cohortes']['Edades'][..., í_etps_coh]
        pobs = símismo.predics['Cohortes']['Pobs'][..., í_etps_coh]

        # Calcualar la probabilidad de transición.
        probs = np.divide(np.subtract(dists.cdf(edades + cambio_edad),
                                      dists.cdf(edades)),
                          np.subtract(1, dists.cdf(edades))
                          )

        probs[np.isnan(probs)] = 1

        # Calcular el número que transicionan.
        n_cambian = np.floor(np.multiply(pobs, probs))

        # Aplicar el cambio de edad.
        símismo.predics['Cohortes']['Edades'][..., í_etps_coh] += cambio_edad

        # Si hay que quitar las etapas que transicionario, hacerlo aquí.
        if quitar:
            símismo.predics['Cohortes']['Pobs'][..., í_etps_coh] -= n_cambian

        # Agregar las transiciones a la matriz de egresos.
        np.sum(n_cambian, axis=0, out=matr_egr)

    def _añadir_a_cohortes(símismo, nuevos, edad=0, dic_predic=None):
        """
        Esta función agrega nuevos miembros a un cohorte existente.

        :param nuevos: La matriz de poblaciones para agregar. Eje 0: Parcela, Eje 1: Repetición estocástica, Eje 2:
        Repetición paramétrica, Eje 3: Etapa.
        :type nuevos: np.ndarray

        :param edad: Las edades iniciales de los nuevos miembros al cohorte. El valor automático es, naturalmente, 0.
        (Esto se puede cambiar si estamos transicionando cohortes existentes de un otro cohorte.) Si es una
        matriz, debe tener la misma forma que `nuevos`.
        :type edad: np.ndarray

        :param dic_predic: Un diccionario opcional con la matriz de predicciones. Si cohortes es `None`, se
        utilizará la matriz de la simulación actual.
        :type dic_predic: dict
        """

        # Si no se especificaron cohortes en particular, usar los cohortes de la simulación actual.
        if dic_predic is None:
            dic_predic = símismo.predics

        cohortes = dic_predic['Cohortes']

        # Si no hay cohortes, no hay nada que hacer aquí.
        if not len(símismo.índices_cohortes):
            return

        if not np.sum(nuevos):
            return

        # Para simplificar el código.
        matr_pobs = cohortes['Pobs']
        matr_eds = cohortes['Edades']

        # Limpiar edades de cohortes
        matr_eds[matr_pobs == 0] = 0

        # Los índices de los días (eje 0) cuyos cohortes tienen la edad mínima. Si hay más que un día (cohorte) con la
        # edad mínima, tomará el primero.
        i_cohs = np.argmin(matr_eds, axis=0).flatten()

        í_parc, í_estoc, í_parám, í_etps = dic_predic['Matrices']['í_ejes_cohs']
        # Las edades de los cohortes con las edades mínimas.
        tmñ = dic_predic['Matrices']['tmñ_para_cohs']  # El tamaño de los cohortes, sin el eje de día
        eds_min = matr_eds[i_cohs, í_parc, í_estoc, í_parám, í_etps].reshape(tmñ)

        # Las poblaciones que corresponden a estas edades mínimas.
        pobs_coresp_í = matr_pobs[i_cohs, í_parc, í_estoc, í_parám, í_etps].reshape(tmñ)

        # Dónde no hay población existente, reinicializamos la edad.
        eds_min = np.where(pobs_coresp_í == 0, [0], eds_min)

        # Calcular el peso de las edades existentes, según sus poblaciones existentes (para combinar con el nuevo
        # cohorte si hay que combinarla con un cohorte existente).
        peso_ed_ya = np.divide(pobs_coresp_í, np.add(nuevos, pobs_coresp_í))
        peso_ed_ya[np.isnan(peso_ed_ya)] = 0

        # Los edades promedios. Si no había necesidad de combinar cohortes, será la población del nuevo cohorte.
        eds_prom = np.add(np.multiply(eds_min, peso_ed_ya), np.multiply(edad, np.subtract(1, peso_ed_ya)))

        # Guardar las edades actualizadas en los índices apropiados
        matr_eds[i_cohs, í_parc, í_estoc, í_parám, í_etps] = eds_prom.flatten()

        # Guardar las poblaciones actualizadas en los índices apropiados
        matr_pobs[i_cohs, í_parc, í_estoc, í_parám, í_etps] += nuevos.flatten()

    def _quitar_de_cohortes(símismo, muertes, í_don=None, í_recip=None):
        """
        Esta funciôn quita individuos de los cohortes de la Red.

        :param muertes: La matriz de muertes aleatorias a quitar del cohorte. Eje 0: Parcela,
        Eje 1: Repetición estocástica, Eje 2: Repetición paramétrica, Eje 3: Etapa.
        :type muertes: np.ndarray
        
        :param í_don:
        :type í_don: np.ndarray

        :param í_recip:
        :type í_recip: np.ndarray

        """

        # Para simplificar el código
        pobs = símismo.predics['Cohortes']['Pobs']
        edades = símismo.predics['Cohortes']['Edades']

        muertes = muertes.copy()  # Para no afectar el parámetro que se pasó a la función

        # Una suma cumulativa inversa de la distribución de cohortes
        pobs_cums = np.cumsum(pobs[::-1], axis=0)[::-1]

        # Para cada cohorte...
        for n_día in range(pobs.shape[0]):

            # Si ya no hay nada que hacer, parar aquí
            if np.sum(muertes) == 0:
                return

            pobs_coh = pobs[n_día, ...]

            if n_día < pobs.shape[0] - 1:
                # Si no es la última categoría de los cohortes...

                # Quitar los de esta edad que se murieron
                quitar = np.floor(np.multiply(np.divide(pobs_coh, pobs_cums[n_día]), muertes))

                quitar[np.isnan(quitar)] = 0

                quitar = np.minimum(np.maximum(quitar, muertes - pobs_cums[n_día + 1]), muertes)

                # Actualizar las muertes que faltan implementar
                np.subtract(muertes, quitar, out=muertes)

            else:
                # Si es la última categoría de cohortes, hay que quitar todo lo que queda en muertes
                quitar = muertes

            np.subtract(pobs_coh, quitar, out=pobs_coh)

            # Si transiciona a otro cohorte (de otra etapa), implementarlo aquí
            if í_recip is not None:

                if í_don is None:
                    raise ValueError

                # Los índices (en la matriz de cohortes) de las etapas recipientes.
                í_recip_coh = [símismo.índices_cohortes.index(x) for x in í_recip]

                í_don_coh = [símismo.índices_cohortes.index(x) for x in í_don]

                # Las edades de las etapas que se quitaron
                eds = edades[n_día, ...]

                # Cambiar el orden de las etapas para los cohortes recipientes
                nuevos = np.zeros_like(quitar)
                nuevos[..., í_recip_coh] = quitar[..., í_don_coh]
                símismo._añadir_a_cohortes(nuevos=nuevos, edad=eds)

    def _ajustar_cohortes(símismo, cambio):
        """
        Esta función ajusta las poblaciones de cohortes. Es muy útil cuando no sabemos si el cambio es positivo o
        negativo.

        :param cambio: El cambio en poblaciones, en el mismo formato que la matriz de población.
        :type cambio: np.ndarray

        """

        # Detectar dónde el cambio es positivo y dónde es negativo
        positivos = np.where(cambio > 0, cambio, [0])
        negativos = np.where(cambio < 0, -cambio, [0])

        # Agregar los positivos...
        símismo._añadir_a_cohortes(nuevos=positivos)

        # ...y quitar los negativos.
        símismo._quitar_de_cohortes(muertes=negativos)


# Funciones auxiliares

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
        días_grd = sup_centro + sup_lados
    elif corte == 'Intermediario':
        días_grd = sup_centro + sup_lados - sup_arriba
    elif corte == 'Vertical':
        días_grd = sup_lados
    elif corte == 'Ninguno':
        días_grd = sup_lados + sup_centro + sup_arriba
    else:
        raise ValueError

    return días_grd


def probs_conj(matr, eje, pesos=1, máx=1):
    """
    Esta función utiliza las reglas de probabilidades conjuntas para ajustar depredación con presas o depredadores
    múltiples cuya suma podría sumar más que el total de presas o la capacidad del depredador.

    :param matr: Una matriz con los valores para ajustar.
    :type matr: np.ndarray

    :param eje: El eje según cual hay que hacer los ajustes
    :type eje: int

    :param pesos: Un peso inverso opcional para aplicar a la matriz ántes de hacer los cálculos.
    :type pesos: float | int | np.ndarray

    :param máx: Una matriz o número con los valores máximos para la matriz para ajustar. Si es matriz, debe ser de
    tamaño compatible con matr.
    :type máx: float | int | np.ndarray

    """

    if not isinstance(máx, np.ndarray):
        tamaño = list(matr.shape)
        tamaño.pop(eje)
        máx = np.full(tuple(tamaño), máx)

    ajustados = np.divide(matr, pesos)

    ratio = np.divide(ajustados, np.expand_dims(máx, eje))

    np.multiply(
        np.expand_dims(
            np.divide(
                np.subtract(
                    1,
                    np.product(
                        np.subtract(1,
                                    np.where(np.isnan(ratio), [0], ratio)
                                    ), axis=eje
                    )
                ),
                np.nansum(ratio, axis=eje)
            ),
            axis=eje),
        ajustados,
        out=ajustados)

    ajustados[np.isnan(ajustados)] = 0

    suma = np.sum(ajustados, axis=eje)
    extra = np.where(suma > máx, suma - máx, [0])

    np.multiply(ajustados, np.expand_dims(np.subtract(1, np.divide(extra, suma)), axis=eje), out=ajustados)

    np.multiply(ajustados, pesos, out=matr)


def copiar_dic_refs(d, c=None):
    """
    Esta función copia un diccionario pero deja las referencias a matrices y variables PyMC intactos. Esto permite
    dejar que etapas fantasmas de una víctima de parasitoide tengan los mismos variables que la etapa original y evita
    desdoblar variables en la calibración.

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
