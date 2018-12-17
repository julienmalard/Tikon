import numpy as np


class Validación(object):
    def __init__(símismo, mods):
        símismo._mods = mods

    def _validar(símismo):
        vld = {}
        for nmb, m in símismo._mods.items():
            vld[nmb] = m.valid()
        return vld


def validar_matr_pred(matr_predic, vector_obs, eje_parám, eje_estoc, eje_t):

    # Quitar observaciones que faltan
    matr_predic = matr_predic[:, :, ~np.isnan(vector_obs)]
    vector_obs = vector_obs[~np.isnan(vector_obs)]

    # El número de días de predicciones y observaciones
    n_rep_estoc, n_rep_parám, n_días = matr_predic.shape

    # Combinar los dos ejes de incertidumbre (repeticiones estocásticas y paramétricas)
    matr_predic = matr_predic.reshape((n_rep_estoc * n_rep_parám, n_días))

    # Calcular el promedio de todas las repeticiones de predicciones
    vector_predic = matr_predic.mean(axis=0)

    # Calcular R cuadrado
    r2 = calc_r2(vector_predic, vector_obs)

    # Raíz cuadrada normalizada del error promedio
    rcnep = np.divide(np.sqrt(np.square(vector_predic - vector_obs).mean()), np.mean(vector_obs))

    # Validar el intervalo de incertidumbre
    confianza = np.empty_like(vector_obs, dtype=float)
    for n in range(n_días):
        perc = estad.percentileofscore(matr_predic[..., n], vector_obs[n]) / 100
        confianza[n] = abs(0.5 - perc) * 2

    confianza.sort()

    percentiles = np.divide(np.arange(1, n_días + 1), n_días)

    r2_percentiles = calc_r2(confianza, percentiles)

    return {'r2': r2, 'rcnep': rcnep, 'r2_percentiles': r2_percentiles}


def calc_r2(y_obs, y_pred):
    """
    Calcula el coeficiente de determinación (R2) entre las predicciones de un modelo y los valores observados.
    Notar que calcula R2 *entre valores predichos y observados*, y *no* entre un variable predictor y dependiente.
    Para este últimeo, emplear `scipy.stats.linregress`.

    :param y_obs: Valores observados.
    :type y_obs: np.ndarray
    :param y_pred: Valores predichos. (y_sombrero)
    :type y_pred: np.ndarray
    :return: El coeficiente de determinación, R2.
    :rtype: float
    """
    prom_y = np.mean(y_obs)
    sc_rs = np.sum(np.subtract(y_obs, y_pred) ** 2)
    sc_reg = np.sum(np.subtract(y_pred, prom_y) ** 2)
    sc_t = sc_rs + sc_reg

    r2 = 1 - np.divide(sc_rs, sc_t)

    return r2
