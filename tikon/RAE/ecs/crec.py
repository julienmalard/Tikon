import numpy as np

from tikon.calibs import CategEc, SubCategEc, Ecuación, Parám, FuncEc

inf = np.inf


class FuncNinguna(FuncEc):
    def __call__(self, cf, paso, módulo, matr_egr=None):
        # Sin modificación a r.
        return np.multiply(cf['r'], paso, out=matr_egr)


class FuncLogNormTemp(FuncEc):
    def __call__(self, cf, paso, módulo, matr_egr=None):
        # r responde a la temperatura con una ecuación log normal.
        temp_máx = módulo.obt_val_extern(['clima', 'temp_máx'])

        return np.multiply(
            cf['r'] * paso,
            np.exp(-0.5 * (np.log(temp_máx / cf['t']) / cf['p']) ** 2),
            out=matr_egr
        )


class FuncExpon(object):
    def __call__(self, cf, paso, módulo, matr_egr=None):
        pobs_etps =
        crec_etps =
        return np.multiply(pobs_etps, crec_etp, out=matr_egr)


def _f_logíst(cf, paso, matr_egr):
    # Ecuación logística sencilla
    return np.multiply(crec_etp, pobs_etps * (1 - pobs_etps / cf['K']), out=matr_egr)


def _f_logíst_presa(cf, paso, matr_egr):
    # Crecimiento logístico. 'K' es un parámetro repetido para cada presa de la etapa y indica
    # la contribución individual de cada presa a la capacidad de carga de esta etapa (el depredador).

    k = np.nansum(np.multiply(pobs[..., np.newaxis, :], cf['K']), axis=-1)  # Calcular la capacidad de carga
    np.multiply(crec_etp, pobs_etps * (1 - pobs_etps / k), out=crec_etp)  # Ecuación logística sencilla

    # Evitar pérdidas de poblaciones superiores a la población.
    np.maximum(crec_etp, -pobs_etps, out=crec_etp)


def _f_logíst_depred(cf, paso, matr_egr):
    # Crecimiento proporcional a la cantidad de presas que se consumió el depredador.

    depred = símismo.predics['Depred'][..., í_etps, :]  # La depredación por esta etapa
    k = np.nansum(np.multiply(depred, cf['K']), axis=3)  # Calcular la capacidad de carga
    np.multiply(crec_etp, pobs_etps * (1 - pobs_etps / k), out=crec_etp)  # Ecuación logística sencilla

    # Evitar péridadas de poblaciones superiores a la población.
    np.maximum(crec_etp, -pobs_etps, out=crec_etp)


ec_ninguna = Ecuación(
    'Ninguna',
    paráms=[
        Parám('r', (0, inf))
    ],
    fun=FuncNinguna()
)

ec_log_norm_temp = Ecuación(
    'Log Normal Temperatura',
    paráms=[
        Parám('t', (0, inf)),
        Parám('p', (0, inf))
    ]
)

ec_nada = Ecuación('Nada')

ec_expon = Ecuación('Exponencial', fun=_f_expon)  # El exponencial no tiene parámetros a parte de r

ec_logíst = Ecuación(
    'Logístico',
    paráms=[
        Parám('K', (0, inf)),

    ],
    fun=_f_logíst
)

ec_logíst_presa = Ecuación(
    'Logístico Presa',
    paráms=[
        Parám('K', (0, inf), inter='presa')
    ],
    fun=_f_logíst_presa
)

ec_logíst_depred = Ecuación(
    'Logístico Depredación',
    paráms=[
        Parám('K', (0, inf), inter='presa')
    ],
    fun=_f_logíst_depred
)

ec_constante = Ecuación(
    'Constante',
    paráms=[
        Parám('n', (0, inf))
    ]
)

ecs_crec = CategEc(
    'Crecimiento',
    subs=[
        SubCategEc('Modif', ecs=[ec_nada, ec_ninguna, ec_log_norm_temp]),
        SubCategEc(
            'Ecuación',
            ecs=[ec_nada, ec_expon, ec_logíst, ec_logíst_presa, ec_logíst_depred, ec_constante]
        )
    ]
)
