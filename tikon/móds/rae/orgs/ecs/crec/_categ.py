import xarray as xr
from tikon.móds.rae.orgs.ecs._plntll import CategEcOrg
from tikon.móds.rae.orgs.ecs.utils import ECS_CREC
from tikon.móds.rae.red.utils import RES_CREC

from .ec import EcuaciónCrec
from .modif import ModifCrec


class EcsCrec(CategEcOrg):
    nombre = ECS_CREC
    cls_ramas = [ModifCrec, EcuaciónCrec]
    _nombre_res = RES_CREC
    req_todas_ramas = True

    def postproc(símismo, paso, sim):
        crec = símismo.obt_val_res(sim)
        pobs = símismo.pobs(sim)

        # Evitar pérdidas de poblaciones superiores a la población.
        crec = xr.ufuncs.maximum(crec, -pobs)

        símismo.poner_val_res(sim, val=crec)
        símismo.ajust_pobs(sim, pobs=crec)
