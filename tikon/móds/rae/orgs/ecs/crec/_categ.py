import numpy as np

from tikon.datos.datos import máximo
from .ec import EcCrec
from .tasa import TasaCrec
from .._plntll import CategEcOrg
from ..utils import ECS_CREC
from tikon.móds.rae.utils import RES_CREC


class EcsCrec(CategEcOrg):
    nombre = ECS_CREC
    cls_ramas = [TasaCrec, EcCrec]
    _nombre_res = RES_CREC

    def postproc(símismo, paso, sim):
        crec = símismo.obt_valor_res(sim)
        pobs = símismo.pobs(sim)

        # Evitar pérdidas de poblaciones superiores a la población.
        crec = máximo(crec, -pobs)

        símismo.poner_valor_res(sim, val=crec)
        símismo.ajust_pobs(sim, pobs=crec)
