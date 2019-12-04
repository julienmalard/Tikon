import numpy as np
from tikon.ecs.árb_mód import Parám

from ._plntll_ec import ModCrec


class T(Parám):
    nombre = 't'
    líms = (0, None)
    unids = 'C'


class P(Parám):
    nombre = 'p'
    líms = (0, None)
    unids = None


class R(Parám):
    nombre = 'r'
    líms = (0, None)
    unids = None


class LogNormTemp(ModCrec):
    nombre = 'Log Normal Temperatura'
    cls_ramas = [T, P, R]

    def eval(símismo, paso, sim):
        # r responde a la temperatura con una ecuación log normal.
        temp_máx = sim.obt_valor_extern('clima.temp_máx')
        cf = símismo.cf

        return cf['r'] * paso * np.exp(-0.5 * (np.log(temp_máx / cf['t']) / cf['p']) ** 2)

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_máx'}
