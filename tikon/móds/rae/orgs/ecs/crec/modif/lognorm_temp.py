import xarray as xr
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg


class T(Parám):
    nombre = 't'
    líms = (0, None)
    unids = 'C'


class P(Parám):
    nombre = 'p'
    líms = (0, None)
    unids = None


class LogNormTemp(EcuaciónOrg):
    nombre = 'Log Normal Temperatura'
    cls_ramas = [T, P]

    def eval(símismo, paso, sim):
        # r responde a la temperatura con una ecuación log normal.
        temp_máx = sim.obt_val_extern('clima.temp_máx')
        cf = símismo.cf

        return cf['r'] * paso * xr.ufuncs.exp(-0.5 * (xr.ufuncs.log(temp_máx / cf['t']) / cf['p']) ** 2)

    def requísitos(símismo, controles=False):
        if not controles:
            return ['clima.temp_máx']
