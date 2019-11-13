import math

import numpy as np
import pandas as pd
import xarray as xr
from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.central.res import Resultado
from tikon.result import Obs
from tikon.utils import EJE_TIEMPO

const = math.pi


class Res(Resultado):
    nombre = 'res'
    unids = None
    inicializable = True

    def __init__(símismo, sim, coords, vars_interés):
        coords = {'mi eje': np.arange(10), **coords}
        super().__init__(sim, coords, vars_interés)


class SimulMóduloInic(SimulMódulo):
    resultados = [Res]


class MóduloResInic(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloInic


f_inic = '2019-01-01'
f_final = '2019-02-01'
tiempo = pd.date_range(f_inic, f_final, freq='D')

obs = Obs(
    mód='módulo', var='res',
    datos=xr.DataArray(const, coords={'mi eje': np.arange(5), EJE_TIEMPO: tiempo}, dims=['mi eje', EJE_TIEMPO])
)

exper = Exper('exper', Parcela('parcela'))
exper.datos.agregar_obs(obs)

exper_sin_obs = Exper('exper', Parcela('parcela'))

modelo = Modelo(MóduloResInic())
