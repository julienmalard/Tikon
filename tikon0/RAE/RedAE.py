import math as mat
import os
from copy import deepcopy as copiar_profundo
from warnings import warn as avisar

import numpy as np

from . import Insecto as Ins
from .Organismo import Organismo
from ..Coso import Simulable, dic_a_lista
from ..Matemáticas import Arte


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

    def _gen_dic_predics_exps(símismo, exper, n_rep_estoc, n_rep_parám, paso, n_pasos, detalles):
        """

        :return:
        :rtype: dict
        """

            # Ahora para los datos de población iniciales (evidentemente, no hay que inicializar datos de
            # muertes, etc.)...

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

            # Las poblaciones iniciales de organismos con poblaciones constantes se actualizarán antes de cada
            # simulación según los valores de sus parámetros.

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
