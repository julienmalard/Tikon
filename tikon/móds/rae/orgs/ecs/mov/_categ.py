import numpy as np
from tikon.móds.rae.orgs.ecs._plntll import CategEcOrg
from tikon.móds.rae.orgs.ecs.utils import ECS_MOV
from tikon.móds.rae.utils import RES_MOV
from tikon.utils import EJE_DEST, EJE_PARC

from .atr import Atracción
from .dstn import Distancia


class EcsMov(CategEcOrg):
    nombre = ECS_MOV
    cls_ramas = [Distancia, Atracción]
    _nombre_res = RES_MOV

    def postproc(símismo, paso, sim):
        mov = np.floor(símismo.obt_valor_res(sim))
        símismo.poner_valor_res(sim, mov)

        emigr = mov.sum(dim=EJE_DEST)
        imigr = mov.sum(dim=EJE_PARC).rename({EJE_DEST: EJE_PARC})
        migr = imigr - emigr

        símismo.ajust_pobs(sim, migr)

    @classmethod
    def activa(cls, modelo, mód, exper):
        return any(len(exp.parcelas) > 1 for exp in exper)
