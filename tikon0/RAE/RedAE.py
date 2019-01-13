import numpy as np

from ..Coso import Simulable


class Red(Simulable):
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
