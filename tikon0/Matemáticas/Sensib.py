import SALib.analyze.delta as delta
import SALib.analyze.dgsm as dgsm
import SALib.analyze.fast as fast
import SALib.analyze.ff as ff_anlz
import SALib.analyze.morris as morris_anlz
import SALib.analyze.sobol as sobol
import SALib.sample.fast_sampler as fast_sampler
import SALib.sample.ff as ff_muestra
import SALib.sample.latin as latin
import SALib.sample.morris as morris_muestra
import SALib.sample.saltelli as saltelli


def prep_anal_sensib(método, n, problema, opciones):
    """

    :param método:
    :type método: str
    :param n:
    :type n: int
    :param problema:
    :type problema: dict
    :param opciones:
    :type opciones: dict
    :return:
    :rtype:
    """

    método_mín = método.lower()

    if método_mín == 'sobol':
        # Preparar opciones
        conv_ops_muestrear = {'calc_segundo_orden': 'calc_second_order'}
        conv_ops_anlz = {'calc_segundo_orden': 'calc_second_order', 'núm_remuestreos': 'num_resamples',
                         'nivel_conf': 'conf_level', 'paralelo': 'parallel', 'n_procesadores': 'n_processors'}

        # La opciones para las funciones de de muestreo y de análisis
        ops_muestrear = {conv_ops_muestrear[a]: val for a, val in opciones.items() if a in conv_ops_muestrear}
        ops_anlz = {conv_ops_anlz[a]: val for a, val in opciones.items() if a in conv_ops_anlz}

        # Calcular cuáles valores de parámetros tenemos que poner para el análisis Sobol
        vals_paráms = saltelli.sample(problem=problema, N=n, **ops_muestrear)

        # La función de análisis
        fun_anlz = sobol.analyze

    elif método_mín == 'fast':
        # Preparar opciones
        if 'M' in opciones:
            ops_muestrear = ops_anlz = {'M': opciones['M']}
        else:
            ops_muestrear = ops_anlz = {}

        # Calcular para FAST
        vals_paráms = fast_sampler.sample(problem=problema, N=n, **ops_muestrear)

        # La función de análisis
        fun_anlz = fast.analyze

    elif método_mín == 'morris':
        # Preparar opciones
        conv_ops_muestrear = {'núm_niveles': 'num_levels', 'salto_cuadr': 'grid_jump',
                              'traj_optimal': 'optimal_trajectories', 'opt_local': 'local_optimization'}
        conv_ops_anlz = {'núm_remuestreos': 'num_resamples', 'nivel_conf': 'conf_level',
                         'salto_cuadr': 'grid_jump', 'núm_niveles': 'num_levels'}

        # La opciones para las funciones de de muestreo y de análisis
        ops_muestrear = {conv_ops_muestrear[a]: val for a, val in opciones.items() if a in conv_ops_muestrear}
        ops_anlz = {conv_ops_anlz[a]: val for a, val in opciones.items() if a in conv_ops_anlz}

        # Calcular para Morris
        vals_paráms = morris_muestra.sample(problem=problema, N=n, **ops_muestrear)
        ops_anlz['X'] = vals_paráms

        # La función de análisis
        fun_anlz = morris_anlz

    elif método_mín == 'dmim':
        # Preparar opciones
        conv_ops_anlz = {'núm_remuestreos': 'num_resamples', 'nivel_conf': 'conf_level'}
        ops_anlz = {conv_ops_anlz[a]: val for a, val in opciones.items() if a in conv_ops_anlz}

        # Calcular para DMIM
        vals_paráms = latin.sample(problem=problema, N=n)
        ops_anlz['X'] = vals_paráms

        # La función de análisis
        fun_anlz = delta.analyze

    elif método_mín == 'dgsm':  # para hacer: verificar
        # Preparar opciones
        conv_ops_anlz = {'núm_remuestreos': 'num_resamples', 'nivel_conf': 'conf_level'}
        ops_anlz = {conv_ops_anlz[a]: val for a, val in opciones.items() if a in conv_ops_anlz}

        # Calcular para DGSM
        vals_paráms = saltelli.sample(problem=problema, N=n)
        ops_anlz['X'] = vals_paráms

        # La función de análisis
        fun_anlz = dgsm

    elif método_mín == 'ff':

        # Preparar opciones
        if 'segundo_orden' in opciones:
            ops_anlz = {'second_order': opciones['segundo_orden']}
        else:
            ops_anlz = {}

        # Calcular para FF
        vals_paráms = ff_muestra.sample(problem=problema)
        ops_anlz['X'] = vals_paráms

        # La función de análisis
        fun_anlz = ff_anlz

    else:
        raise ValueError('Método de análisis de sensibilidad "{}" no reconocido.'.format(método))

    return vals_paráms, fun_anlz, ops_anlz
