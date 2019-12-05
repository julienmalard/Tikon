from datetime import date

import pandas as pd
import xarray as xr
from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.central.res import Resultado
from tikon.datos import Obs
from tikon.utils import EJE_TIEMPO


class Res1_1(Resultado):
    nombre = 'res 1_1'
    unids = None


class Res1_2(Resultado):
    nombre = 'res 1_2'
    unids = None


class Res2_1(Resultado):
    nombre = 'res 2_1'
    unids = None


class Res2_2(Resultado):
    nombre = 'res 2_2'
    unids = None


class SimulMódulo1(SimulMódulo):
    resultados = [Res1_1, Res1_2]


class Módulo1(Módulo):
    nombre = 'módulo 1'
    cls_simul = SimulMódulo1


class SimulMódulo2(SimulMódulo):
    resultados = [Res2_1, Res2_2]


class Módulo2(Módulo):
    nombre = 'módulo 2'
    cls_simul = SimulMódulo2


class MiObs(Obs):
    mód = 'módulo 1'
    var = 'res 1_1'


obs_1_1 = MiObs(
    datos=xr.DataArray(
        1.5, coords={EJE_TIEMPO: pd.date_range(date.today(), periods=10, freq='D')}, dims=[EJE_TIEMPO]
    )
)

exper = Exper('exper', Parcela('parcela'))
exper_obs_1_1 = Exper('exper', Parcela('parcela'), obs=obs_1_1)
modelo = Modelo([Módulo1, Módulo2])
