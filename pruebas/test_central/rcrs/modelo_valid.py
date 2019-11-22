import numpy as np
import pandas as pd
import xarray as xr
from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.central.res import Resultado
from tikon.result import Obs
from tikon.utils import EJE_TIEMPO, EJE_PARC

f_inic = '2000-01-01'

crds = {'eje 1': ['a', 'b'], 'eje 2': ['x', 'y', 'z']}


class Res(Resultado):

    def __init__(símismo, sim, coords, vars_interés):
        coords = {**crds, **coords}
        super().__init__(sim, coords, vars_interés)

    nombre = 'res'
    unids = None


class SimulMóduloValid(SimulMódulo):
    resultados = [Res]

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        símismo.poner_valor('res', 1, rel=True)


class MóduloValid(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloValid


class MiObs(Obs):
    mód = 'módulo'
    var = 'res'


obs = MiObs(
    datos=xr.DataArray(
        np.arange(10),
        coords={EJE_TIEMPO: pd.date_range(f_inic, periods=10, freq='D')}, dims=[EJE_TIEMPO]
    ).expand_dims({EJE_PARC: ['parcela'], **crds})
)

exper = Exper('exper', Parcela('parcela'), obs=obs)
modelo = Modelo(MóduloValid)
