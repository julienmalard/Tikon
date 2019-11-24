import numpy as np

from .ec import EcuaciónCrec
from .modif import ModifCrec
from .._plntll import CategEcOrg
from ..utils import ECS_CREC
from tikon.móds.rae.utils import RES_CREC


class EcsCrec(CategEcOrg):
    nombre = ECS_CREC
    cls_ramas = [ModifCrec, EcuaciónCrec]
    _nombre_res = RES_CREC

    def postproc(símismo, paso, sim):
        crec = símismo.obt_valor_res(sim)
        pobs = símismo.pobs(sim)

        # Evitar pérdidas de poblaciones superiores a la población.
        crec = np.maximum(crec, -pobs)

        símismo.poner_valor_res(sim, val=crec)
        símismo.ajust_pobs(sim, pobs=crec)
