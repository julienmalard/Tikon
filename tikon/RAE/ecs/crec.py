import numpy as np

from tikon.calibs import CategEc, SubCategEc, Ecuación, Parám

inf = np.inf


def _f_ninguna(cf, paso, matr_egr=None):
    # Sin modificación a r.
    return np.multiply(cf['r'], paso, out=matr_egr)


def _f_log_norm_temp(cf, paso, temp_máx, matr_egr=None):
    # r responde a la temperatura con una ecuación log normal.
    return np.multiply(
        cf['r'] * paso,
        np.exp(-0.5 * (np.log(temp_máx / cf['t']) / cf['p']) ** 2),
        out=matr_egr
    )

def _f_expon(cf, paso, matr_egr):
    return np.multiply(pobs_etps, crec_etp, out=matr_egr)

def _f_logíst(cf, paso, matr_egr):
    # Ecuación logística sencilla
    return np.multiply(crec_etp, pobs_etps * (1 - pobs_etps / cf['K']), out=matr_egr)


ec_ninguna = Ecuación(
    'Ninguna',
    paráms=[
        Parám('r', (0, inf))
    ],
    fun=_f_ninguna
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
    ]
)

ec_logíst_depred = Ecuación(
    'Logístico Depredación',
    paráms=[
        Parám('K', (0, inf), inter='presa')
    ]
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
