from math import pi as π

import numpy as np
import xarray as xr

from tikon.central.matriz import f_numpy, donde, máximo, mínimo


def días_grados(mín, máx, umbrales, método, corte):
    """
    Esta función calcula los días grados basados en vectores de temperaturas mínimas y máximas diarias.
    Información sobre los métodos utilizados aquí se puede encontrar en [1]_.

    Parameters
    ----------
    mín: xr.DataArray
    máx: xr.DataArray
    umbrales: tuple
    método: str
    corte: str

    References
    ----------
    ..[1] UC IPM: How to Manage Pests: Degree-Days. http://www.ipm.ucdavis.edu/WEATHER/ddconcepts.html
    """

    método = método.lower()
    corte = corte.lower()
    umbr_mín, umbr_máx = umbrales

    if método == 'triangular':
        # Método triangular único
        dif = máx - umbr_máx
        sup_arriba = donde(dif > 0, dif ** 2 / (máx - mín) + máximo(mín - umbr_máx, 0), 0)
        sup_centro = donde(dif > 0, (1 - máximo((umbr_máx - mín) / (máx - mín), 0)) * (umbr_máx - umbr_mín), 0)

        altura = mínimo(umbr_máx, máx) - máximo(umbr_mín, mín)
        sup_lados = donde(
            altura > 0,
            0.5 * altura * donde(
                dif > 0,
                (umbr_máx - umbr_mín) / (máx - mín),
                1 - máximo((umbr_mín - mín) / (máx - mín), 0)
            ) + máximo(mín - umbr_mín, 0) * donde(
                dif > 0,
                1 - (umbr_máx - mín) / (máx - mín),
                1
            ),
            0
        )

    elif método == 'sinusoidal':
        # Método sinusoidal único
        amp = (máx - mín) / 2
        ubic = mín + 1
        umbr_máx_nrm, umbr_mín_nrm = umbr_máx / amp - ubic, umbr_mín / amp - ubic

        intr_máx = donde(f_numpy(np.logical_or, umbr_máx_nrm < -1, umbr_máx_nrm > 1), 1, -umbr_máx_nrm).fi(np.arccos)

        i_máx = intr_máx, (2 * π - intr_máx)
        intr_mín = donde(f_numpy(np.logical_or, umbr_mín_nrm < -1, umbr_mín_nrm > 1), 1, -umbr_mín_nrm).fi(np.arccos)
        i_mín = intr_mín, (2 * π - intr_mín)

        dif = 1 - umbr_máx_nrm
        sup_arriba = donde(
            dif > 0,
            -i_máx[1].fi(np.sin) + i_máx[0].fi(np.sin) + máximo(0, -1 - umbr_máx_nrm) * 2 * π,
            0
        ) / (2 * π) * amp
        sup_centro = donde(dif > 0, (i_máx[1] - i_máx[0]) * (umbr_máx_nrm - umbr_mín_nrm), 0) / (2 * π) * amp

        lados = f_numpy(np.logical_or, umbr_máx_nrm < -1, umbr_mín_nrm > 1)
        sup_lados = donde(
            lados,
            donde(
                dif > 0,
                2 * (
                        i_mín[0].fi(np.sin) - i_máx[0].fi(np.sin)
                        + (i_máx[0] - i_mín[0]) * máximo(-1 - umbr_mín_nrm, 0)
                ),
                i_mín[0].fi(np.sin) - i_mín[1].fi(np.sin)
            ),
            0
        ) / (2 * π) * amp

    else:
        raise ValueError(método)

    if corte == 'horizontal':
        días_grd = sup_centro + sup_lados
    elif corte == 'intermediario':
        días_grd = máximo(sup_centro - sup_arriba, 0) + sup_lados
    elif corte == 'vertical':
        días_grd = sup_lados
    elif corte == 'ninguno':
        días_grd = sup_lados + sup_centro + sup_arriba
    else:
        raise ValueError(corte)

    return días_grd.donde(días_grd >= 0, 0)
