import math as mat
import os
from copy import deepcopy as copiar_profundo
from datetime import datetime as ft
from warnings import warn as avisar

import numpy as np

from . import Insecto as Ins
from .Gen_organismos import generar_org
from .Organismo import Organismo
from ..Coso import Simulable, dic_a_lista
from ..Matemáticas import Ecuaciones as Ec, Arte
from ..Matemáticas.Incert import validar_matr_pred


class Red(Simulable):
    """
    Una Red representa una red agroecológica. Trae varios `Organismos` juntos para interactuar. Aquí se implementan
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
        :type organismos: list[Organismo]

        """

        super().__init__(nombre=nombre, proyecto=proyecto)

        # Para guardar etapas que siempre se deben combinar antes de reportar resultados (por ejemplo, etapas fantasmas)
        # Tendrá la forma siguiente:
        # {núm_etp_víctima : {'Parasitoide 1': núm_etp_fantasma,
        #                     'Parasitoide 2': núm_etp_fantasma,
        #                     },
        # ...]
        símismo.fantasmas = {}

        # Información de parasitoides:
        símismo.parasitoides = {'índices': (), 'adultos': {}, 'juvs': {}}

        # Un diccionario para guardar información específica a cada experimento asociado para poder procesar
        # las predicciones de la red en función a cada experimento.
        símismo.info_exps = {'etps_interés': {}, 'combin_etps': {}, 'combin_etps_obs': {}, 'parcelas': {},
                             'superficies': {}, 'egrs': {}}

        # La lista de egresos potencialmente incluidos como observaciones
        símismo.l_egresos = ['Pobs', 'Crecimiento', 'Reproducción', 'Transiciones', 'Muertes']

    def actualizar(símismo):
        """
        Actualiza la lista de etapas y las matrices de coeficientes de la red y de sus objetos.

        """

        # Limpiar todo
        símismo.fantasmas.clear()
        símismo.parasitoides['adultos'].clear()
        símismo.parasitoides['juvs'].clear()

        # Crear etapas fantasmas para huéspedes infectados
        for n_etp, etp in enumerate(símismo.etapas):  # type: int, dict
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
                        dic_estr = {
                            'nombre': 'Infectando a %s_%s' % (org_hués, nombre_etp_hués),
                            'posición': 0,
                            'ecs': copiar_profundo(obj_org_hués.receta['estr'][nombre_etp_hués]['ecs'])
                        }  # type: dict

                        # La configuración de la etapa fantasma es la misma que la de su etapa pariente
                        conf = obj_org_hués.config[nombre_etp_hués]

                        # Copiamos el diccionario de coeficientes, pero con referencias a los objetos de distrubuciones
                        # (Comparten los mismos variables).
                        coefs = copiar_dic_coefs(obj_org_hués.receta['coefs'][nombre_etp_hués])

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
                            mult_trans = símismo.etapas[n_larva]['dic']['ecs']['Transiciones']['Mult']
                            coefs_prob_trans = símismo.etapas[n_larva]['coefs']['Transiciones']['Prob'][prob_trans]
                            coefs_edad = símismo.etapas[n_larva]['coefs']['Edad']['Ecuación'][ec_edad]
                            coefs_mult_trans = símismo.etapas[n_larva]['coefs']['Transiciones']['Mult'][mult_trans]

                            dic_estr['ecs']['Transiciones']['Prob'] = prob_trans
                            dic_estr['ecs']['Edad']['Ecuación'] = ec_edad
                            dic_estr['ecs']['Transiciones']['Mult'] = mult_trans
                            coefs['Transiciones']['Prob'][prob_trans] = coefs_prob_trans
                            coefs['Edad']['Ecuación'][ec_edad] = coefs_edad
                            coefs['Transiciones']['Mult'][mult_trans] = coefs_mult_trans

                        dic_estr['trans'] = n_trans

                        dic_etp = dict(org=etp['org'],
                                       nombre=dic_estr['nombre'],
                                       dic=dic_estr,
                                       conf=conf,
                                       coefs=coefs)

                        símismo.etapas.append(dic_etp)

                        símismo.núms_etapas[etp['org']][dic_estr['nombre']] = n_etp_fant

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

        # Desactivar las ecuaciones de transiciones de juveniles de parasitoides (porque estas se implementan
        # por la última fase fantasma de la víctima correspondiente
        for org in símismo.organismos.values():
            if isinstance(org, Ins.Parasitoide):
                n_etp = símismo.núms_etapas[org.nombre]['juvenil']  # type: int

                dic_estr = símismo.etapas[n_etp]['dic']['ecs']['Transiciones']
                dic_edad = símismo.etapas[n_etp]['dic']['ecs']['Edad']
                tipo_ed = dic_edad['Ecuación']
                tipo_mult = dic_estr['Mult']
                tipo_prob = dic_estr['Prob']

                if tipo_prob != 'Nada':
                    símismo.ecs['Transiciones']['Mult'][tipo_mult].remove(n_etp)
                    símismo.ecs['Transiciones']['Prob'][tipo_prob].remove(n_etp)
                if tipo_ed != 'Nada':
                    símismo.ecs['Edad']['Ecuación'][tipo_ed].remove(n_etp)

        # Actualizar los vínculos con los experimentos
        símismo._actualizar_vínculos_exps()

        # La Red ya está lista para simular
        símismo.listo = True

    def dibujar(símismo, mostrar=True, directorio=None, exper=None, n_líneas=0, incert='componentes'):
        """
        Ver la documentación de `Simulable`.

        :type mostrar: bool
        :type directorio: str
        :type n_líneas: int
        :type exper: list[str]

        :param incert: El tipo de incertidumbre que querremos incluir en el gráfico.
        :type incert: str

        """

        # Si no se especificó experimento, tomar todos los experimentos de la validación o calibración la más recién.
        if exper is None:
            exper = list(símismo.predics_exps.keys())

        # Asegurar el formato correcto para 'exper'.
        if type(exper) is str:
            exper = [exper]

        l_m_preds = símismo.dic_simul['l_m_preds_todas']
        l_ubic_m_preds = símismo.dic_simul['l_ubics_m_preds']
        l_m_obs = símismo.dic_simul['l_m_obs_todas']
        l_días_obs_todas = símismo.dic_simul['l_días_obs_todas']

        for i, m in enumerate(l_m_preds):  # Eje 0: parc, 1: estoc, 2: parám, 3: etp, [4: etp víctima], -1: día
            n_parc = m.shape[0]
            n_etp = len(símismo.etapas)
            ubic = l_ubic_m_preds[i]  # Lista de exper, egreso
            exp = ubic[0]
            egr = ubic[1]

            # Saltar experimentos que no nos interesan
            if exp not in exper:
                continue

            # El archivo para guardar el imagen
            dir_img = os.path.join(directorio, *ubic)

            for i_parc in range(n_parc):
                prc = símismo.info_exps['parcelas'][exp][i_parc]
                for i_etp, d_etp in enumerate(símismo.etapas):

                    etp = d_etp['nombre']
                    org = d_etp['org']

                    if len(m.shape) == 5:
                        # Si no es una matriz de depredación...

                        try:
                            if l_m_obs[i] is None:
                                vec_obs = None
                            else:
                                vec_obs = l_m_obs[i][i_parc, i_etp, :]
                                días_obs = l_días_obs_todas[i]
                        except IndexError:
                            vec_obs = días_obs = None

                        matr_pred = m[i_parc, :, :, i_etp, :]

                        # Generar el titulo del gráfico. Incluir el nombre de la parcela, si necesario:
                        if egr == 'Transiciones':
                            op = 'Recip- '
                        elif egr == 'Reproducción':
                            op = 'Desde- '
                        else:
                            op = ''
                        if n_parc > 1:
                            título = 'Parcela "{prc}", {op}"{org}", etapa "{etp}"' \
                                .format(prc=prc, op=op, org=org, etp=etp)
                        else:
                            título = '{op}{org}, etapa "{etp}"'.format(op=op, org=org, etp=etp)

                        Arte.graficar_pred(matr_predic=matr_pred, título=título, vector_obs=vec_obs,
                                           tiempos_obs=días_obs, etiq_y=egr, incert=incert, n_líneas=n_líneas,
                                           directorio=dir_img)
                    else:
                        # Si es una matriz de depredación...

                        # ... todavía no incorporamos observaciones.

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

                            # La matriz de predicciones
                            # Eje 0: parcela, 1: rep estoc, 2: rep parám, 3: etp depred, 4: etp víctima, 5: día
                            matr_pred = m[n_parc, ..., n_etp, n_etp_víc, :]  # Eje 0: estoc, 1: parám, 2: día

                            if n_parc > 1:
                                título = 'Parcela "{prc}", {org}, etapa "{etp}" ' \
                                         'atacando a "{org_víc}", etapa "{etp_víc}"' \
                                    .format(prc=prc, org=org, etp=etp, org_víc=org_víc, etp_víc=etp_víc)
                            else:
                                título = '{org}, etapa "{etp}" ' \
                                         'atacando a "{org_víc}", etapa "{etp_víc}"' \
                                    .format(org=org, etp=etp, org_víc=org_víc, etp_víc=etp_víc)

                            # Generar el gráfico
                            Arte.graficar_pred(matr_predic=matr_pred, título=título, etiq_y='Depredación',
                                               incert=incert, n_líneas=n_líneas, directorio=dir_img)

    def _inic_pobs_const(símismo):
        # El diccionario de crecimiento
        dic = símismo.ecs['Crecimiento']['Ecuación']

        if 'Constante' in dic.keys():
            # Si hay al menos una etapa con ecuaciones constantes...

            # Llenar poblaciones iniciales manualmente para organismos con poblaciones fijas.
            for n_etp in dic['Constante']:
                # Si la etapa tiene una población constante...

                í_etp = dic['Constante'].index(n_etp)

                # La población inicial se determina por el coeficiente de población constante del organismo
                pobs_inic = símismo.coefs_act_númzds['Crecimiento']['Ecuación']['Constante']['n'][:, í_etp]

                # Guardamos las poblaciones iniciales en la matriz de predicciones de poblaciones.
                símismo.predics['Pobs'][..., n_etp, 0] = pobs_inic


    def _incrementar_depurar(símismo, paso, i, detalles, d_tiempo, mov=False, extrn=None):
        """

        :param paso:
        :type paso: int
        :param i:
        :type i: int
        :param detalles:
        :type detalles: bool
        :param d_tiempo:
        :type d_tiempo: dict
        :param mov:
        :type mov: bool
        :param extrn:
        :type extrn: dict
        :return:
        :rtype: dict
        """

        # Empezar con las poblaciones del paso anterior
        símismo.predics['Pobs'][..., i] = símismo.predics['Pobs'][..., i - 1]
        pobs = símismo.predics['Pobs'][..., i]

        def verificar_estado(punto):
            """
            Verifica la consistencia interna del modelo.

            :param punto: El punto de ejecución (para mensajes de error)
            :type punto: str
            """

            etps_ins = [j for j, x in enumerate(símismo.etapas)
                        if isinstance(símismo.organismos[x['org']], Ins.Insecto)]

            mnsg = '\tSi acabas de agregar nuevas ecuaciones, es probablemente culpa tuya.\n\tSino, es culpa mía.'

            if pobs.min() < 0:
                raise ValueError('Población inferior a 0 justo después de calcular {}.\n{}'.format(punto, mnsg))
            if np.any(np.isnan(pobs)):
                raise ValueError('Población "nan" justo después de calcular {}.\n{}'.format(punto, mnsg))
            if np.any(np.not_equal(pobs[..., etps_ins].astype(int), pobs[..., etps_ins])):
                raise ValueError('Población fraccional justo después de calcular {}\n{}.'.format(punto, mnsg))
            if len(símismo.predics['Cohortes']):
                pobs_coh = símismo.predics['Cohortes']['Pobs']
                if pobs_coh.min() < 0:
                    raise ValueError('Población de cohorte inferior a 0 justo después de calcular {}.\n{}'
                                     .format(punto, mnsg))
                if np.any(np.not_equal(pobs_coh.astype(int), pobs_coh)):
                    raise ValueError('Población de cohorte fraccional justo después de calcular {}.\n{}'
                                     .format(punto, mnsg))
                if np.any(np.isnan(pobs_coh)):
                    raise ValueError('Población de cohorte "nan" justo después de calcular {}.\n{}'.format(punto, mnsg))
                if np.any(np.not_equal(pobs_coh.sum(axis=0), pobs[..., símismo.índices_cohortes])):
                    raise ValueError('Población de cohorte no suma a población total justo después de calcular {}.'
                                     .format(punto))

        if not len(d_tiempo):
            d_tiempo = {'Depredación': 0, 'Crecimiento': 0, 'Muertes': 0, 'Edad': 0, 'Transiciones': 0,
                        'Reproducción': 0, 'Movimiento': 0, 'Ruido': 0}

        # Calcular la depredación, crecimiento, reproducción, muertes, transiciones, y movimiento entre parcelas

        # Ruido aleatorio
        antes = ft.now()
        símismo._calc_ruido(pobs=pobs, paso=paso)
        ahora = ft.now()
        d_tiempo['Ruido'] += (ahora - antes).seconds + (ahora - antes).microseconds / 1000000
        verificar_estado('Ruido')

        # Una especie que mata a otra.
        verificar_estado('Inicio')
        antes = ft.now()
        símismo._calc_depred(pobs=pobs, paso=paso, depred=depred, extrn=extrn)
        ahora = ft.now()
        d_tiempo['Depredación'] += (ahora - antes).seconds + (ahora - antes).microseconds / 1000000
        verificar_estado('Depredación')

        # Una población que crece (misma etapa)
        antes = ft.now()
        símismo._calc_crec(pobs=pobs, extrn=extrn, crec=crec, paso=paso)
        ahora = ft.now()
        d_tiempo['Crecimiento'] += (ahora - antes).seconds + (ahora - antes).microseconds / 1000000
        verificar_estado('Crecimiento')

        # Muertes por el ambiente
        antes = ft.now()
        símismo._calc_muertes(pobs=pobs, muertes=muertes, extrn=extrn, paso=paso)
        ahora = ft.now()
        d_tiempo['Muertes'] += (ahora - antes).seconds + (ahora - antes).microseconds / 1000000
        verificar_estado('Muertes')

        # Calcular cambios de edades
        antes = ft.now()
        símismo._calc_edad(extrn=extrn, paso=paso, edades=edades)
        ahora = ft.now()
        d_tiempo['Edad'] += (ahora - antes).seconds + (ahora - antes).microseconds / 1000000
        verificar_estado('Edad')

        # Una etapa que cambia a otra, o que se muere por su edad.
        antes = ft.now()
        símismo._calc_trans(pobs=pobs, paso=paso, trans=trans)
        ahora = ft.now()
        d_tiempo['Transiciones'] += (ahora - antes).seconds + (ahora - antes).microseconds / 1000000
        verificar_estado('Transiciones')

        # Una etapa que se reproduce para producir más de otra etapa
        antes = ft.now()
        símismo._calc_reprod(pobs=pobs, paso=paso, reprod=reprod, depred=depred)
        ahora = ft.now()
        d_tiempo['Reproducción'] += (ahora - antes).seconds + (ahora - antes).microseconds / 1000000
        verificar_estado('Reproducción')

        if mov:
            # Movimientos de organismos de una parcela a otra.
            símismo._calc_mov(pobs=pobs, extrn=extrn, paso=paso)
            ahora = ft.now()
            d_tiempo['Movimiento'] += (ahora - antes).seconds + (ahora - antes).microseconds / 1000000
            verificar_estado('Movimiento')

        return d_tiempo


    def _procesar_simul(símismo):
        """
        Ver la documentación de `Simulable`.
        """

        for exp, predic in símismo.dic_simul['d_predics_exps'].items():
            # Para cada experimento...

            # El tamaño de las parcelas
            tamaño_superficies = símismo.info_exps['superficies'][exp]

            for egr in símismo.info_exps['egrs'][exp]:
                # Para cada egreso de interés...

                # Convertir poblaciones a unidades de organismos por hectárea
                np.divide(predic[egr], tamaño_superficies, out=predic[egr])  # Notar que este cambia la matriz inicial

                # Agregamos etapas fantasmas a las etapas originales de los huéspedes
                for i, fants in símismo.fantasmas.items():
                    índ_fants = list(fants.values())  # Los índices de las etapas fantasmas
                    predic[egr][..., i, :] += np.sum(predic[egr][..., índ_fants, :], axis=-2)

                # Agregamos etapas fantasmas a la etapa juvenil del parasitoide también
                for ad, dic in símismo.parasitoides['adultos'].items():
                    índ_fants = dic['n_fants']  # Los índices de las etapas fantasmas

                    d_juvs = símismo.parasitoides['juvs']
                    índ_juv = next(x for x in d_juvs if d_juvs[x] == ad)

                    predic[egr][..., índ_juv, :] += np.sum(predic[egr][..., índ_fants, :], axis=-2)

                # Combinaciones basadas en los datos disponibles (combinaciones manuales)
                # Tiene el formato general: {exp: {{1: [3,4, etc.]}, etc...], ...}
                try:
                    combin_etps = símismo.info_exps['combin_etps'][exp][egr]
                    for i in combin_etps:
                        predic[egr][..., i, :] += np.sum(predic[egr][..., combin_etps[i], :], axis=-2)
                except KeyError:
                    pass


    def _analizar_valid(símismo):
        """
        Ver documentación de Simulable.
        Esta función valida las predicciones de una corrida de validación.

        :return: Un diccionario, organizado por experimento, organismo y etapa, del ajuste del modelo.
        :rtype: dict

        """

        # El diccionario de validación por etapa
        valids_detalles = {}

        # El diccionario de observaciones en formato validación
        d_obs_valid = símismo.dic_simul['d_obs_valid']

        # El diccionario de matrices de validación
        d_matrs_valid = símismo.dic_simul['matrs_valid']

        n_etps = len(símismo.etapas)

        d_res_valid = {}

        # Para cada experimento...
        for exp, d_obs_exp in d_obs_valid.items():

            valids_detalles[exp] = {}

            for egr, matr in d_obs_exp.items():
                n_parc = d_obs_exp[egr].shape[0]

                for n_p in range(n_parc):

                    parc = símismo.info_exps['parcelas'][exp][n_p]

                    for n_etp in range(n_etps):

                        vec_obs = matr[n_p, n_etp, :]  # Eje 2 = día

                        if np.sum(~np.isnan(vec_obs)) == 0:
                            continue

                        matr_preds = d_matrs_valid[exp][egr][n_p, ..., n_etp, :]  # Eje 0 parc, 1 estoc, 2 parám, 3 día

                        org = símismo.etapas[n_etp]['org']
                        etp = símismo.etapas[n_etp]['nombre']

                        if org not in valids_detalles[exp]:
                            valids_detalles[exp][org] = {}

                        valids_detalles[exp][org][etp] = {}

                        valids = validar_matr_pred(
                            matr_predic=matr_preds,
                            vector_obs=vec_obs
                        )
                        valids_detalles[exp][org][etp][parc] = valids
                        for ll, v in valids.items():
                            if ll not in d_res_valid:
                                d_res_valid[ll] = []
                            d_res_valid[ll].append(v)

        d_res_valid = {ll: np.mean(v) for ll, v in d_res_valid.items()}

        return {'Valid': d_res_valid, 'Valid detallades': valids_detalles}


    def _actualizar_vínculos_exps(símismo):
        """
        Ver la documentación de Simulable.

        Esta función llenará el diccionario símismo.info_exps, lo cuál contiene la información necesaria para
          conectar las predicciones de una Red con los datos observados en un Experimento. Este diccionario tiene
          cuatro partes:
            2. 'etps_interés': Una lista de los números de las etapas en la Red que corresponden
            3. 'combin_etps': Un diccionario de las etapas cuyas predicciones hay que combinar. Tiene la forma
                general {n_etp: [n otras etapas], n_etp2: [], etc.},
                donde las llaves del diccionario son números enteros, no texto.
            4. 'ubic_obs': Un formato tuple con matrices con la información de dónde hay que sacar los datos de
                observaciones para cada día y cada etapa. Para hacer: cada parcela.

        """

        # Borrar los datos anteriores, en caso que existían simulaciones anteriores
        for categ_info in símismo.info_exps.values():
            categ_info.clear()

        # Para cada experimento que está vinculado con la Red...
        for exp, d in símismo.exps.items():

            # El objeto y diccionario de correspondencias del experimento
            obj_exp = d['Exp']
            d_corresp = d['Corresp'].copy()  # Hacer una copia, en caso que tengamos que quitarle unos organismos

            # Crear las llaves para este experimento en el diccionario de formatos de la Red, y simplificar el código.
            etps_interés = símismo.info_exps['etps_interés'][exp] = {}
            combin_etps = símismo.info_exps['combin_etps'][exp] = {}
            combin_etps_obs = símismo.info_exps['combin_etps_obs'][exp] = {}
            egrs = símismo.info_exps['egrs'][exp] = []

            # Agregar la lista de nombres de parcelas, en el orden que aparecen en las matrices de observaciones:
            parc = símismo.info_exps['parcelas'][exp] = obj_exp.obt_parcelas(tipo=símismo.ext)

            # Guardar el tamaño de las parcelas
            símismo.info_exps['superficies'][exp] = obj_exp.superficies(parc)

            for egr in símismo.l_egresos:
                # Para cada tipo de egreso posible...

                # Ver si hay observaciones de este egreso en el experimento actual
                if obj_exp.obt_datos_rae(egr) is not None:
                    # Si hay datos, hacemos una notita para después
                    egrs.append(egr)

            # Para cada tipo de correspondencia (poblaciones, muertes, etc...)
            for egr, corresp in d_corresp.items():

                # Verificar si este tipo de egreso tiene observaciones disponibles en este experimento
                if egr not in egrs:
                    # Si no hay datos, mejor pasamos al próximo tipo de egreso de una vez
                    continue

                # Crear diccionarios apropiados y simplificar el código
                etps_interés_egr = etps_interés[egr] = {}
                combin_etps_egr = combin_etps[egr] = {}
                combin_etps_obs_egr = combin_etps_obs[egr] = {}

                # Una lista, en orden, de los nombres de las columnas en la base de datos
                nombres_cols = obj_exp.obt_datos_rae(egr)['cols']

                # Verificar que los nombres de organismos y etapas estén correctos
                for org in corresp:
                    d_org = corresp[org]
                    if org not in símismo.receta['estr']['Organismos']:
                        # Si el organismo no existe en la Red, avisar el usuario y borrarlo del diccionario de
                        # correspondencias
                        avisar('El organismo "{}" no existe en la red "{}". Se excluirá del experimento "{}".'
                               .format(org, símismo.nombre, exp))
                        corresp.pop(org)

                    for etp in list(d_org):
                        if etp not in símismo.núms_etapas[org]:
                            # Si la etapa no existe para el organismo, avisar el usuario y borrarla del diccionario de
                            # correspondencias
                            avisar('Organismo "{}" no tiene etapa "{}". Se excluirá del experimento "{}".'
                                   .format(org, etp, exp))
                            d_org.pop(etp)

                # Para guardar cuenta de combinaciones de columnas de datos.
                l_cols_cum = []
                l_etps_cum = []

                # Para cada organismo en el diccionario de correspondencias...
                for org, d_org in corresp.items():

                    # Para cada etapa del organismo en el diccionario de correspondencias...
                    for etp, d_etp in d_org.items():

                        # La lista de columna(s) de datos correspondiendo a esta etapa
                        l_cols = d_etp

                        # Asegurar el formato correcto
                        if type(l_cols) is not list:
                            l_cols = [l_cols]
                        l_cols.sort()  # Para poder ver si esta combinación de columnas ya existía (abajo)

                        # El número de la etapa en la Red
                        n_etp = símismo.núms_etapas[org][etp]

                        # Guardar la lista de observaciones que hay que combinar, si aplica
                        if len(l_cols) > 1:
                            # Si hay más que una columna de datos para esta etapa...

                            # Guardar la lista de índices de columnas que hay que combinar
                            combin_etps_obs_egr[n_etp] = [nombres_cols.index(c) for c in l_cols]

                        # Verificar ahora para etapas cuyas predicciones hay que combinar
                        if l_cols in l_cols_cum:
                            # Si ya había otra etapa con estos mismo datos...

                            # Buscar el número de la otra etapa
                            n_otra_etp = l_etps_cum[l_cols_cum.index(l_cols)]

                            # Si es la primera vez que la otra etapa se desdoble, agregar su número como llave al
                            # diccionario.
                            if n_otra_etp not in combin_etps_egr:
                                combin_etps_egr[n_otra_etp] = []

                            # Agregar el número de esta etapa a la lista.
                            combin_etps_egr[n_otra_etp].append(n_etp)

                        else:
                            # Si la columna (o combinación de columnas) no se utilizó todavía para otra etapa...

                            # Guardar el nombre de la columna de interés, tanto como el número de la etapa
                            l_cols_cum.append(l_cols)
                            l_etps_cum.append(n_etp)
                            etps_interés_egr[n_etp] = nombres_cols.index(l_cols[0])  # El número de la columna en Exper


    def _gen_dic_predics_exps(símismo, exper, n_rep_estoc, n_rep_parám, paso, n_pasos, detalles):
        """

        :return:
        :rtype: dict
        """

        # El diccionario (vacío) de predicciones
        d_predics_exps = símismo.dic_simul['d_predics_exps']

        # El número de etapas se toma de la Red sí misma
        n_etps = len(símismo.etapas)

        n_cohs = len(símismo.índices_cohortes)

        # Para cada experimento...
        for exp in exper:

            # Sacamos el objeto correspondiendo al experimento
            try:
                obj_exp = símismo.exps[exp]['Exp']
            except KeyError:
                raise ValueError('El experimento "{}" no está vinculado con esta Red.'.format(exp))

            # El número de parcelas y de pasos del Experimento
            n_parc = len(obj_exp.obt_parcelas(tipo=símismo.ext))
            n_pasos_exp = n_pasos[exp]

            # Generamos el diccionario de predicciones en función de esta simulación
            dic_predics = símismo._gen_dic_matr_predic(
                n_parc=n_parc, n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_parám, n_etps=n_etps, n_pasos=n_pasos_exp,
                n_cohs=n_cohs, detalles=detalles
            )

            # Ahora para los datos de población iniciales (evidentemente, no hay que inicializar datos de
            # muertes, etc.)...

            # Una lista de las poblaciones iniciales ajustadas (tomando en cuenta columnas de datos compartidas)
            l_pobs_inic = [None] * len(símismo.etapas)
            combin_etps = símismo.info_exps['combin_etps'][exp]['Pobs']

            for n_etp, i in símismo.info_exps['etps_interés'][exp]['Pobs'].items():  # type: int
                # Para cada etapa de interés...

                # La matriz de datos iniciales para una etapa. Eje 0 = parcela, eje 1 = etapa, eje 2 = tiempo.
                # Quitamos el eje 1. "i" es el número de la etapa en la matriz de observaciones.
                matr_obs_inic = obj_exp.obt_datos_rae('Pobs', por_parcela=True)['datos'][:, i, 0]

                # Si hay múltiples columnas de observaciones para esta etapa...
                combin_etps_obs = símismo.info_exps['combin_etps_obs'][exp]
                if n_etp in combin_etps_obs:

                    # Para cada otra columna que hay que combinar con esta...
                    for col_otra in combin_etps_obs[n_etp]:
                        # Sumar las observaciones.
                        datos_otra = obj_exp.obt_datos_rae('Pobs', por_parcela=True)['datos'][:, col_otra, 0]
                        np.sum(matr_obs_inic, datos_otra, out=matr_obs_inic)

                # Ajustar para etapas compartidas
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
            for n_etp, i in símismo.info_exps['etps_interés'][exp]['Pobs'].items():  # type: int
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
                    dic_predics['Pobs'][..., n_etp, 0] = matr_obs_inic[:, np.newaxis, np.newaxis]

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
                        raise ValueError(
                            'Tenemos una complicacioncita con los datos inicales para el experimento"{}".\n'
                            'No es posible tener más poblaciones iniciales de juveniles de parasitoides que hay\n'
                            'indivíduos de etapas potencialmente hospederas.\n'
                            '¿No estás de acuerdo?')

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
                        dic_predics['Pobs'][..., n_etp_fant, 0] += pobs

                        # Quitar de la población de la etapa víctima (no infectada) correspondiente.
                        dic_predics['Pobs'][..., n_etp_víc, 0] -= pobs

            # Ahora, inicializamos los cohortes.
            símismo._añadir_a_cohortes(dic_predic=dic_predics,
                                       nuevos=dic_predics['Pobs'][..., símismo.índices_cohortes, 0])

            # Las poblaciones iniciales de organismos con poblaciones constantes se actualizarán antes de cada
            # simulación según los valores de sus parámetros.

            # Guardar el diccionario creado bajo el nombre de su experimento correspondiente.
            d_predics_exps[exp] = dic_predics

        # Ahora, listas e información de matrices de predicciones (para gráficos y análises de sensibilidad).

        # Diccionario de predicciones excluyendo matrices temporarias y de información, etc.
        if detalles:
            d_preds = {x: {e: d_x[e] for e in símismo.l_egresos} for x, d_x in d_predics_exps.items()}
        else:
            d_preds = {x: {'Pobs': d_x['Pobs']} for x, d_x in d_predics_exps.items()}

        # Generamos la lista de matrices de predicciones. Las ubicaciones se guardan automáticamente.
        l_preds = símismo.dic_simul['l_m_preds_todas']
        dic_a_lista(d=d_preds, l=l_preds, l_u=símismo.dic_simul['l_ubics_m_preds'])

        # Generamos una copia de los datos iniciales, para poder reinicializar corridas. Para Redes, solamente tenemos
        # que hacer una copia de los cohortes, y del primer día de poblaciones.
        símismo.dic_simul['inic_d_predics_exps'] = {
            exp: {'Cohortes': copiar_profundo(d_exp['Cohortes']),
                  'Pobs': d_exp['Pobs'][..., 0].copy()}
            for exp, d_exp in símismo.dic_simul['d_predics_exps'].items()
        }


    def _gen_dics_valid(símismo, exper, paso, n_pasos, n_rep_estoc, n_rep_parám):
        # Simplificar el código
        d_obs = símismo.dic_simul['d_obs_valid']  # El diccionario de matrices de observaciones para la validación
        d_valid = símismo.dic_simul['matrs_valid']  # El diciconario de matrices de la validación
        d_preds_v = {}  # El diccionario de matrices de simulación que vinculados con observaciones
        d_días_obs = {}

        # Diccionario temporario para organizar los índices
        d_índs = {}

        for exp in exper:
            # Para cada experimento...

            obj_exp = símismo.exps[exp]['Exp']  # El objeto del Experimento
            nombres_parc = obj_exp.obt_parcelas(tipo=símismo.ext)
            n_parc = len(nombres_parc)  # El número de parcelas
            t_final = paso * n_pasos[exp]

            for egr in símismo.l_egresos:
                # Para cada egreso posible...

                if egr in símismo.info_exps['egrs'][exp]:
                    # Si el egreso ha sido observado en el Experimento...

                    # Asegurarse que el nombre del experimento existe en los diccionarios necesarios
                    for d in [d_obs, d_días_obs, d_valid, d_preds_v, d_índs]:
                        if exp not in d:
                            d[exp] = {}

                    # El diccionario de datos del Experimento. Los tomamos en unidades de observaciones por ha, porque
                    # así se reportarán los resultados de la simulación.
                    datos = obj_exp.obt_datos_rae(egr, t_final=t_final, por_parcela=False)
                    # Los días con estas observaciones
                    d_días_obs[exp][egr] = días = datos['días']
                    n_días = len(días)  # El número de días con observaciones
                    n_etps = len(símismo.etapas)  # El número de etapas en la Red

                    # Crear una matriz de NaN para las observaciones
                    d_obs[exp][egr] = matr_obs = np.empty((n_parc, n_etps, n_días))
                    matr_obs[:] = np.nan

                    # Llenar la matriz de observaciones
                    parc = [nombres_parc.index(x) for x in datos['parc']]  # Los índices de las parcelas
                    etps = list(símismo.info_exps['etps_interés'][exp][egr].keys())  # Los índices de las etapas en rae
                    etps_bd = list(símismo.info_exps['etps_interés'][exp][egr].values())  # Los índices de etps en Exper
                    vals = datos['datos'][:, etps_bd, :]  # Los valores. Eje 0 = parc, 1 = etp, 2 = día
                    matr_obs[parc, etps, :] = vals  # Llenar los valores. eje 2 = día. Excluimos días sin datos obs.

                    # Combinar datos de etapas en las observaciones, si necesario.
                    for e, l_c in símismo.info_exps['combin_etps_obs'][exp][egr].items():
                        vals = datos['datos'][:, l_c, :]
                        matr_obs[:, e, :] += np.sum(vals, axis=1)

                    # Guardar el diccionario correspondiente de las predicciones en el diccionario de predicciones
                    # con vículos a la validación.
                    d_preds_v[exp][egr] = símismo.dic_simul['d_predics_exps'][exp][egr]

                    # Crear la matriz vacía para los datos de validación
                    d_valid[exp][egr] = np.empty((n_parc, n_rep_estoc, n_rep_parám, n_etps, n_días))

                    # Los índices para convertir de matriz de predicción a matriz de validación
                    días_ex = [d for d in días if d % paso == 0]
                    días_inter = [d for d in días if d % paso != 0]

                    í_p_ex = [d // paso for d in días_ex]  # Índices exactos (en la matriz pred)
                    í_v_ex = [np.where(días == d)[0][0] for d in días_ex]  # Índices exactos (en la matriz valid)
                    í_v_ínt = [i for i in range(n_días) if i not in í_v_ex]  # Índices para interpolar (matriz valid)
                    í_p_ínt_0 = [mat.floor(d / paso) for d in días_inter]  # Índices interpol inferiores (matr pred)
                    í_p_ínt_1 = [mat.ceil(d / paso) for d in días_inter]  # Índices interpol superiores (matr pred)
                    pesos = [(d % paso) / paso for d in días_inter]  # La distancia de la interpolación

                    índs = {'exactos': (í_v_ex, í_p_ex),
                            'interpol': (í_v_ínt, í_p_ínt_0, í_p_ínt_1, pesos)}
                    d_índs[exp][egr] = índs

        # Linearizar los diccionarios de validación y de predicciones vinculadas.
        símismo.dic_simul['d_l_m_valid'] = {'Normal': dic_a_lista(d_valid)}
        símismo.dic_simul['d_l_m_predics_v'] = {'Normal': dic_a_lista(d_preds_v)}
        símismo.dic_simul['d_l_í_valid'] = {'Normal': dic_a_lista(d_índs, ll_f='exactos')}

        # Crear la lista completa de matrices de observaciones, para gráficos y análisis de sensibilidad
        l_m_preds_v = dic_a_lista(d_preds_v)
        l_m_obs_v = dic_a_lista(d_obs)
        l_días_obs_v = dic_a_lista(d_días_obs)
        l_m_preds_todas = símismo.dic_simul['l_m_preds_todas']

        def temp(m, l):
            try:
                return l.index(m)
            except ValueError:
                return None

        # Guardar las matrices de observaciones que corresponden con las matrices de predicciones, en el mismo orden.
        # Poner None para matrices de predicciones que no tienen observaciones correspondientes.
        l_m_obs_todas = [l_m_obs_v[temp(m, l_m_preds_v)] if temp(m, l_m_preds_v) is not None else None
                         for m in l_m_preds_todas]

        # La lista de índices de días para las observaciones. Poner None para los que no tienen observaciones.
        # Posiblemente podrîa ser más elegante.
        l_días_obs_todas = [l_días_obs_v[temp(m, l_m_preds_v)] if temp(m, l_m_preds_v) is not None else None
                            for m in l_m_preds_todas]
        símismo.dic_simul['l_m_obs_todas'].extend(l_m_obs_todas)
        símismo.dic_simul['l_días_obs_todas'].extend(l_días_obs_todas)


    def _gen_dics_calib(símismo, exper, n_rep_estoc):
        # El diccionario de observaciones para la validación...
        l_obs_v = dic_a_lista(símismo.dic_simul['d_obs_valid'])

        # ... y para la calibración
        d_obs_c = símismo.dic_simul['d_obs_calib']

        # El diccionario de índices para la calibración (lo llenaremos aquí)
        d_índs_calib = símismo.dic_simul['d_l_í_calib']
        d_índs_calib['Normal'] = []

        # El número de observaciones válidas cumulativas (empezar en 0)
        n_obs_cumul = 0

        for m in l_obs_v:
            # Para cada matriz de observaciones de validación...

            # El número de observaciones válidas (no NaN)
            válidos = ~np.isnan(m)
            n_obs = np.sum(válidos)

            # Los índices de las parcelas, etapas y días con observaciones válidas
            parc, etps, días = np.where(válidos)

            # El diccionario con los índices y el rango en la matriz de predicciones
            d_info = {'índs': (parc, etps, días), 'rango': [n_obs_cumul, n_obs_cumul + n_obs]}
            d_índs_calib['Normal'].append(d_info)  # Agregar el diccionario de índices

            # Guardar cuenta del número de observaciones hasta ahora
            n_obs_cumul += n_obs

        # El diccionario vacío para guardar predicciones
        símismo.dic_simul['d_calib']['Normal'] = np.empty((n_obs_cumul, n_rep_estoc))

        # El diccionario de observaciones para la calibración
        d_obs_c['Normal'] = np.empty(n_obs_cumul)

        # Guardar las observaciones en su lugar correspondiente en el vector de observaciones para calibraciones
        for i, m in enumerate(l_obs_v):
            # Para cada observación...

            parc, etps, días = d_índs_calib['Normal'][i]['índs']  # Los índices de valores válidos
            r = d_índs_calib['Normal'][i]['rango']  # El rango en el vector de obs para calibraciones

            # Guardar los valores
            d_obs_c['Normal'][r[0]:r[1]] = m[parc, etps, días]


    def _llenar_coefs(símismo, nombre_simul, n_rep_parám, ubics_paráms=None, calibs=None, dib_dists=False):
        """
        Ver la documentación de Coso.

        :type n_rep_parám: int
        :type ubics_paráms: list[list[str]]
        :type calibs: list | str
        :type dib_dists: bool
        :type ecs: list

        """

        #
        if calibs is None:
            calibs = []

        # El número de etapas en la Red
        n_etapas = len(símismo.etapas)

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

                                matr_etp[:] = d_parám_etp[nombre_simul]

                                # Dibujar la distribución, si necesario
                                if dib_dists:
                                    directorio_dib = os.path.join(símismo.proyecto, símismo.nombre, nombre_simul,
                                                                  'Grf simul', 'Dists',
                                                                  categ, subcateg, tipo_ec, parám)

                                    directorio_dib = símismo._prep_directorio(directorio=directorio_dib)

                                    título = símismo.etapas[n_etp]['org'] + ', ' + símismo.etapas[n_etp]['nombre']

                                    if ubics_paráms is None:
                                        calibs_i = []
                                    else:
                                        org = símismo.etapas[n_etp]['org']
                                        etp = símismo.etapas[n_etp]['nombre']
                                        i_hués = next((i_f for i_f, d in símismo.fantasmas.items()
                                                       if org in d and d[org] == n_etp), None)
                                        if i_hués is None:
                                            ubic = [org, etp, categ, subcateg, parám]
                                            i_c = ubics_paráms.index(ubic)
                                        else:
                                            org_hués = símismo.etapas[i_hués]['org']
                                            etp_hués = símismo.etapas[i_hués]['nombre']
                                            try:
                                                ubic = [org_hués, etp_hués, categ, subcateg, parám]
                                                i_c = ubics_paráms.index(ubic)
                                            except ValueError:
                                                ubic = [org, 'juvenil', categ, subcateg, parám]
                                                i_c = ubics_paráms.index(ubic)
                                        calibs_i = calibs[i_c]
                                    Arte.graficar_dists(dists=[d for x, d in d_parám_etp.items() if x in calibs_i
                                                               and type(d) is str], valores=matr_etp, título=título,
                                                        archivo=directorio_dib)

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
                                                try:
                                                    n_etp_víc = símismo.núms_etapas[org_víc][etp_víc]
                                                except KeyError:
                                                    # Seguir si esta etapa o organismo no existe en la Red.
                                                    continue

                                                # Incluir etapas fantasmas, pero NO para parasitoides (así que una etapa
                                                # fantasma puede caer víctima de un deprededor o de una enfermedad que
                                                # se ataca la etapa no infectada correspondiente, pero NO puede caer
                                                # víctima de otro (o del mismo) parasitoide que afecta la etapa
                                                # original.
                                                l_n_etps_víc = [n_etp_víc]
                                                if n_etp_víc in símismo.fantasmas:
                                                    obj_org = símismo.organismos[símismo.etapas[n_etp]['org']]
                                                    if not isinstance(obj_org, Ins.Parasitoide):
                                                        l_n_etps_víc += list(símismo.fantasmas[n_etp_víc].values())

                                                for n in l_n_etps_víc:
                                                    matr_etp[:, n] = d_parám_etp[org_víc][etp_víc][nombre_simul]

                                                    # Dibujar la distribución, si necesario
                                                    if dib_dists:
                                                        directorio_dib = os.path.join(
                                                            símismo.proyecto, símismo.nombre, nombre_simul,
                                                            'Grf simul', 'Dists',
                                                            categ, subcateg, tipo_ec, parám)

                                                        directorio_dib = símismo._prep_directorio(
                                                            directorio=directorio_dib)

                                                        título = símismo.etapas[n_etp]['org'] + ', ' + \
                                                                 símismo.etapas[n_etp][
                                                                     'nombre'] + ' _ ' + org_víc + ', ' + etp_víc

                                                        if ubics_paráms is None:
                                                            calibs_i = []
                                                        else:
                                                            org = símismo.etapas[n_etp]['org']
                                                            etp = símismo.etapas[n_etp]['nombre']
                                                            i_hués = next((i_f for i_f, d in símismo.fantasmas.items()
                                                                           if org in d and d[org] == n_etp), None)
                                                            if i_hués is None:
                                                                ubic = [org, etp, categ, subcateg, parám, org_víc,
                                                                        etp_víc]
                                                                i_c = ubics_paráms.index(ubic)
                                                            else:
                                                                org_hués = símismo.etapas[i_hués]['org']
                                                                etp_hués = símismo.etapas[i_hués]['nombre']
                                                                try:
                                                                    ubic = [org_hués, etp_hués, categ, subcateg, parám,
                                                                            org_víc, etp_víc]
                                                                    i_c = ubics_paráms.index(ubic)
                                                                except ValueError:
                                                                    ubic = [org, 'juvenil', categ, subcateg, parám,
                                                                            org_víc, etp_víc]
                                                                    i_c = ubics_paráms.index(ubic)

                                                            calibs_i = calibs[i_c]

                                                        Arte.graficar_dists(
                                                            dists=[d for x, d in d_parám_etp[org_víc][etp_víc].items()
                                                                   if x in calibs_i and type(d) is str],
                                                            valores=matr_etp[:, n], título=título,
                                                            archivo=directorio_dib)

                                    else:
                                        # Al momento, solamente es posible tener interacciones con las presas de la
                                        # etapa. Si un día alguien quiere incluir más tipos de interacciones (como, por
                                        # ejemplo, interacciones entre competidores), se tendrían que añadir aquí.
                                        raise ValueError('Interacción "%s" no reconocida.' % tipo_inter)


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



def copiar_dic_coefs(d, c=None):
    """
    Esta función copia un diccionario pero deja las referencias a matrices y variables PyMC intactos (no hace copia
    del último diccionario anidado, sino una referencia a este). Esto permite dejar que etapas fantasmas de una víctima
    de parasitoide tengan los mismos variables que la etapa original y evita desdoblar variables en la calibración.

    :param d: El diccionario de coeficientes para copiar_profundo.
    :type d: dict

    :param c: Para recursiones. No especificar al llamar la función.
    :type c: dict

    :return: Una copia del diccionario con referencias a los últimos diccionarios anidados.
    :rtype: dict
    """

    # Inicializar la copia del diccionario
    if c is None:
        c = {}

    for ll, v in d.items():
        # Para cada llave y valor del diccionario...

        if type(v) is dict:
            # Si es otro diccionario...

            if any(type(x) is dict for x in v.values()):
                # Si el diccionario contiene otros diccionarios, hacer una copia.
                c[ll] = {}
                copiar_dic_coefs(v, c=c[ll])
            else:
                # Si el diccionario no contiene otros diccionarios, poner una referencia.
                c[ll] = v
        else:
            # Si no es un diccionario, seguro que hay que ponerle una referencia (y no una copia).
            c[ll] = v

    return c
