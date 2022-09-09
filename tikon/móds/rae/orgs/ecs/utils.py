import xarray as xr

from tikon.central.matriz import donde

ECS_EDAD = 'Edad'
ECS_CREC = 'Crecimiento'
ECS_DEPR = 'Depredación'
ECS_REPR = 'Reproducción'
ECS_MRTE = 'Muerte'
ECS_TRANS = 'Transición'
ECS_MOV = 'Movimiento'
ECS_ESTOC = 'Estoc'


def probs_conj(datos, dim, pesos=1, máx=1):
    """
    Esta función utiliza las reglas de probabilidades conjuntas para ajustar depredación con presas o depredadores
    múltiples cuya suma podría sumar más que el total de presas o la capacidad del depredador.

    Parameters
    ----------
    datos: xr.DataArray
        Una matriz xr con los valores para ajustar.
    dim: int
        La dimensión común según la cual hay que hacer los ajustes
    pesos: float | int | xr.DataArray
        Un peso inverso opcional para aplicar a la matriz ántes de hacer los cálculos.
    máx: float | int | xr.DataArray
        Una matriz o número con los valores máximos para la matriz para ajustar. Si es matriz, debe ser de
        tamaño compatible con matr.

    """

    ajustados = datos / pesos
    ratio = (ajustados / máx).llenar_nan(0)

    ajustados = ajustados * (1 - (1 - ratio).prod(dim=dim)) / ratio.suma(dim=dim)

    ajustados.llenar_nan(0)

    suma = ajustados.suma(dim=dim)
    extra = donde(suma > máx, suma - máx, 0)

    ajustados *= 1 - (extra / suma)

    return ajustados * pesos

