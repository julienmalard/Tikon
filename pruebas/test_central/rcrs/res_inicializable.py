import math

import numpy as np
import xarray as xr
from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela
from tikon.central.res import Resultado
from tikon.datos import Obs

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


class MiObs(Obs):
    mód = 'módulo'
    var = 'res'


obs = MiObs(datos=xr.DataArray(const, coords={'mi eje': np.arange(5)}, dims=['mi eje']))

exper = Exper('exper', Parcela('parcela'))
exper.datos.espec_inic(const, mód='módulo', var='res')
modelo = Modelo(MóduloResInic())
