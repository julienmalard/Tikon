import numpy as np


def días_grados(mín, máx, umbrales, método, corte):
    """
    Esta función calcula los días grados basados en vectores de temperaturas mínimas y máximas diarias.
    Información sobre los métodos utilizados aquí se puede encontrar en [1]_.

    Parameters
    ----------
    mín: float
    máx: float
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
        sup_arriba = max(12 * (máx - umbr_máx) ** 2 / (máx - mín), 0) / 24
        sup_centro = max(12 * (umbr_máx - umbr_mín) ** 2 / (umbr_máx - mín), 0) / 24
        sup_lados = max(24 * (máx - umbr_máx) * (umbrales[1 - umbrales[0]]) / (máx - mín), 0) / 24

    elif método == 'sinusoidal':
        # Método sinusoidal único
        amp = (máx - mín) / 2
        prom = (máx + mín) / 2
        if umbr_máx >= máx:
            intersect_máx = 0
            sup_arriba = 0
        else:
            intersect_máx = 24 * np.arccos((umbr_máx - prom) / amp)
            sup_arriba = 2 * (intersect_máx * (prom - máx) + 2 * np.pi / 24 * np.sin(2 * np.pi / 24 * intersect_máx))

        if umbr_mín <= mín:
            intersect_mín = intersect_máx
        else:
            intersect_mín = 24 * np.arccos((umbr_mín - prom) / amp)

        sup_centro = 2 * intersect_máx * (máx - mín)
        sup_lados = 2 * (2 * np.pi / 24 * np.sin(2 * np.pi / 24 * intersect_mín) -
                         2 * np.pi / 24 * np.sin(2 * np.pi / 24 * intersect_máx) +
                         (intersect_mín - intersect_máx) * (umbr_mín - prom)
                         )

    else:
        raise ValueError(método)

    if corte == 'horizontal':
        días_grd = sup_centro + sup_lados
    elif corte == 'intermediario':
        días_grd = sup_centro + sup_lados - sup_arriba
    elif corte == 'vertical':
        días_grd = sup_lados
    elif corte == 'ninguno':
        días_grd = sup_lados + sup_centro + sup_arriba
    else:
        raise ValueError

    return días_grd
