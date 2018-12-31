import numpy as np


def probs_conj(matr, eje, pesos=1, máx=1):
    """
    Esta función utiliza las reglas de probabilidades conjuntas para ajustar depredación con presas o depredadores
    múltiples cuya suma podría sumar más que el total de presas o la capacidad del depredador.

    Parameters
    ----------
    matr: np.ndarray
        Una matriz con los valores para ajustar.
    eje: int
        El eje según cual hay que hacer los ajustes
    pesos: float | int | np.ndarray
        Un peso inverso opcional para aplicar a la matriz ántes de hacer los cálculos.
    máx: float | int | np.ndarray
        Una matriz o número con los valores máximos para la matriz para ajustar. Si es matriz, debe ser de
        tamaño compatible con matr.

    """

    if not isinstance(máx, np.ndarray):
        tamaño = list(matr.shape)
        tamaño.pop(eje)
        máx = np.full(tuple(tamaño), máx)

    ajustados = np.divide(matr, pesos)

    ratio = np.divide(ajustados, np.expand_dims(máx, eje))

    np.multiply(
        np.expand_dims(
            np.divide(
                np.subtract(
                    1,
                    np.product(
                        np.subtract(1,
                                    np.where(np.isnan(ratio), [0], ratio)
                                    ), axis=eje
                    )
                ),
                np.nansum(ratio, axis=eje)
            ),
            axis=eje),
        ajustados,
        out=ajustados)

    ajustados[np.isnan(ajustados)] = 0

    suma = np.sum(ajustados, axis=eje)
    extra = np.where(suma > máx, suma - máx, [0])

    np.multiply(ajustados, np.expand_dims(np.subtract(1, np.divide(extra, suma)), axis=eje), out=ajustados)

    np.multiply(ajustados, pesos, out=matr)


def días_grados(mín, máx, umbrales, método='Triangular', corte='Horizontal'):
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

    Returns
    -------
    int
        Número de días grados.

    References
    ----------
    ..[1] UC IPM: How to Manage Pests: Degree-Days. http://www.ipm.ucdavis.edu/WEATHER/ddconcepts.html
    """

    if método == 'Triangular':
        # Método triangular único
        sup_arriba = max(12 * (máx - umbrales[1]) ** 2 / (máx - mín), 0) / 24
        sup_centro = max(12 * (umbrales[1] - umbrales[0]) ** 2 / (umbrales[1] - mín), 0) / 24
        sup_lados = max(24 * (máx - umbrales[1]) * (umbrales[1 - umbrales[0]]) / (máx - mín), 0) / 24

    elif método == 'Sinusoidal':
        # Método sinusoidal único
        # NOTA: Probablemente lleno de bogues
        amp = (máx - mín) / 2
        prom = (máx + mín) / 2
        if umbrales[1] >= máx:
            intersect_máx = 0
            sup_arriba = 0
        else:
            intersect_máx = 24 * np.arccos((umbrales[1] - prom) / amp)
            sup_arriba = 2 * (intersect_máx * (prom - máx) + 2 * np.pi / 24 * np.sin(2 * np.pi / 24 * intersect_máx))

        if umbrales[0] <= mín:
            intersect_mín = intersect_máx
        else:
            intersect_mín = 24 * np.arccos((umbrales[0] - prom) / amp)

        sup_centro = 2 * intersect_máx * (máx - mín)
        sup_lados = 2 * (2 * np.pi / 24 * np.sin(2 * np.pi / 24 * intersect_mín) -
                         2 * np.pi / 24 * np.sin(2 * np.pi / 24 * intersect_máx) +
                         (intersect_mín - intersect_máx) * (umbrales[0] - prom)
                         )

    else:
        raise ValueError

    if corte == 'Horizontal':
        días_grd = sup_centro + sup_lados
    elif corte == 'Intermediario':
        días_grd = sup_centro + sup_lados - sup_arriba
    elif corte == 'Vertical':
        días_grd = sup_lados
    elif corte == 'Ninguno':
        días_grd = sup_lados + sup_centro + sup_arriba
    else:
        raise ValueError

    return días_grd
