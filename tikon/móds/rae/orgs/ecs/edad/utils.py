from math import pi as π

import numpy as np
import xarray as xr


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
        sup_arriba = xr.where(dif > 0, dif ** 2 / (máx - mín) + np.maximum(mín - umbr_máx, 0), 0)
        sup_centro = xr.where(dif > 0, (1 - np.maximum((umbr_máx - mín) / (máx - mín), 0)) * (umbr_máx - umbr_mín), 0)

        altura = np.minimum(umbr_máx, máx) - np.maximum(umbr_mín, mín)
        sup_lados = xr.where(
            altura > 0,
            0.5 * altura * xr.where(
                dif > 0,
                (umbr_máx - umbr_mín) / (máx - mín),
                1 - np.maximum((umbr_mín - mín) / (máx - mín), 0)
            ) + np.maximum(mín - umbr_mín, 0) * xr.where(
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

        intr_máx = np.arccos(
            xr.where(np.logical_or(umbr_máx_nrm < -1, umbr_máx_nrm > 1), 1, -umbr_máx_nrm)
        )
        i_máx = intr_máx, (2 * π - intr_máx)
        intr_mín = np.arccos(
                xr.where(np.logical_or(umbr_mín_nrm < -1, umbr_mín_nrm > 1), 1, -umbr_mín_nrm)
            )
        i_mín = intr_mín, (2 * π - intr_mín)

        dif = 1 - umbr_máx_nrm
        sup_arriba = xr.where(
            dif > 0,
            -np.sin(i_máx[1]) + np.sin(i_máx[0]) + np.maximum(0, -1 - umbr_máx_nrm) * 2 * π,
            0
        ) / (2 * π) * amp
        sup_centro = xr.where(dif > 0, (i_máx[1] - i_máx[0]) * (umbr_máx_nrm - umbr_mín_nrm), 0) / (2 * π) * amp

        lados = np.logical_or(umbr_máx_nrm < -1, umbr_mín_nrm > 1)
        sup_lados = xr.where(
            lados,
            xr.where(
                dif > 0,
                2 * (
                        np.sin(i_mín[0]) - np.sin(i_máx[0])
                        + (i_máx[0] - i_mín[0]) * np.maximum(-1 - umbr_mín_nrm, 0)
                ),
                np.sin(i_mín[0]) - np.sin(i_mín[1])
            ),
            0
        ) / (2 * π) * amp

    else:
        raise ValueError(método)

    if corte == 'horizontal':
        días_grd = sup_centro + sup_lados
    elif corte == 'intermediario':
        días_grd = np.max(sup_centro - sup_arriba, 0) + sup_lados
    elif corte == 'vertical':
        días_grd = sup_lados
    elif corte == 'ninguno':
        días_grd = sup_lados + sup_centro + sup_arriba
    else:
        raise ValueError(corte)

    return días_grd.where(días_grd >= 0, 0)
