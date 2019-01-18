import numpy as np
from scipy import stats as estad
from scipy.special import expit


def validar_matr_pred(matr_predic, vector_obs):
    # Los ejes
    eje_t, eje_estoc, eje_parám = [0, 1, 2]

    # Quitar observaciones que faltan
    faltan = np.isnan(vector_obs)
    matr_predic = matr_predic[~faltan]
    vector_obs = vector_obs[~faltan]

    # El número de días de predicciones y observaciones
    n_días = matr_predic.shape[eje_t]

    # Calcular el promedio de todas las repeticiones de predicciones
    vector_predic = matr_predic.mean(axis=(eje_estoc, eje_parám))

    # Calcular R cuadrado
    r2 = _r2(vector_obs, vector_predic)

    # Raíz cuadrada normalizada del error promedio
    rcnep = _rcnep(vector_obs, vector_predic)

    # Validar el intervalo de incertidumbre
    confianza = np.empty_like(vector_obs, dtype=float)
    for n in range(n_días):
        perc = estad.percentileofscore(matr_predic[n], vector_obs[n]) / 100
        confianza[n] = abs(0.5 - perc) * 2

    confianza.sort()

    percentiles = np.divide(np.arange(1, n_días + 1), n_días)

    r2_percentiles = _r2(confianza, percentiles)
    rcnep_prcntl = _rcnep(confianza, percentiles)

    return {'r2': r2, 'rcnep': rcnep, 'r2_prcntl': r2_percentiles, 'rcnep_prcntl': rcnep_prcntl}


def _r2(y_obs, y_pred):
    """
    Calcula el coeficiente de determinación (R2) entre las predicciones de un modelo y los valores observados.

    Parameters
    ----------
    y_obs: np.ndarray
        Valores observados.
    y_pred: np.ndarray
        Valores predichos. (y_sombrero)

    Returns
    -------
    float:
        El coeficiente de determinación, R2.
    """

    prom_y = np.mean(y_obs)
    sc_rs = np.sum(np.subtract(y_obs, y_pred) ** 2)
    sc_reg = np.sum(np.subtract(y_pred, prom_y) ** 2)
    sc_t = sc_rs + sc_reg

    r2 = 1 - np.divide(sc_rs, sc_t)

    return r2


# para hacer: limpiar
def reps_necesarias(matr, eje_parám, eje_estoc, frac_incert, confianza):
    n_parám = matr.shape[eje_parám]
    n_estoc = matr.shape[eje_estoc]

    otras_dims = [e for i, e in enumerate(matr.shape) if i != eje_estoc]

    n_iter = 100  # podría ser mejor a ~200
    matr_perc_estoc = np.zeros((*otras_dims, n_estoc - 1))
    for i in range(2, n_estoc + 1):
        rango = np.zeros((n_iter, *otras_dims))
        for j in range(n_iter):
            reps_e = np.random.choice(n_estoc, i, replace=False)
            matr_sel = np.take(matr, reps_e, axis=eje_estoc)
            prcntl = np.quantile(matr_sel, q=[(1 - frac_incert) / 2, 0.5 + frac_incert / 2], axis=eje_estoc)
            rango[j] = np.ptp(prcntl, axis=0)
        matr_perc_estoc[..., i - 2] = np.mean(rango, axis=0)

    x = 1 / np.arange(2, n_estoc + 1)
    a_0, b = _reg_lin(x, matr_perc_estoc, eje=-1)
    a = -1 / a_0
    req_n_estoc = np.ceil(np.nanmax(1 / (a * b * (1 - confianza))))

    if np.isnan(req_n_estoc):
        req_n_estoc = 1

    otras_dims = [e for i, e in enumerate(matr.shape) if i != eje_parám and i != eje_estoc]
    matr_perc_prm = np.zeros((*otras_dims, n_parám - 1))
    rango = np.zeros((n_iter, *otras_dims))
    for i in range(2, n_parám + 1):
        for j in range(n_iter):
            reps_e = np.random.choice(n_parám, i, replace=False)
            matr_sel = np.take(matr, reps_e, axis=eje_parám)
            prcntl = np.quantile(matr_sel, q=[(1 - frac_incert) / 2, 0.5 + frac_incert / 2],
                                 axis=(eje_parám, eje_estoc))
            rango[j] = np.ptp(prcntl, axis=0)
        matr_perc_prm[..., i - 2] = np.mean(rango, axis=0)

    x = 1 / np.arange(2, n_parám + 1)
    a_0, b = _reg_lin(x, matr_perc_prm, eje=-1)
    req_n_prm = np.ceil(np.nanmax(-a_0 / (b * (1 - confianza))))

    if np.isnan(req_n_prm):
        req_n_prm = 1
    return {'estoc': req_n_estoc, 'parám': req_n_prm}


def _reg_lin(x, y, eje):
    prom_x, prom_y = np.mean(x), np.mean(y, axis=eje)
    SS_xy = np.sum((x - prom_x) * (y - prom_y[..., np.newaxis]), axis=eje)
    SS_xx = np.sum((x - prom_x) ** 2, axis=eje)
    a = SS_xy / SS_xx
    b = prom_y - a * prom_x
    return a, b


def dens_con_pred(obs, sim):
    res = []
    for s, o in zip(sim, obs):
        d = o * (1 + np.exp(-o * 2)) / (1 - np.exp(-o * 2))
        if np.isnan(d):
            d = 1

        s = s / d
        o = o / d
        try:
            r = estad.gaussian_kde(np.ravel(s))(o)[0]
        except np.linalg.linalg.LinAlgError:
            r = 100 if o == s[0] else 0
        if r == 0:
            r = (max(s) - o if o > max(s) else o - min(s))[0]
        res.append(r)
    return np.mean(expit(res))


def _rcnep(y_obs, y_pred):
    return np.divide(np.sqrt(np.square(y_pred - y_obs).mean()), np.mean(y_obs))
