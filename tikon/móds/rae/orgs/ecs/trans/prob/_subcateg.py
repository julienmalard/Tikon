import numpy as np
from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg
from tikon.móds.rae.utils import RES_TRANS, RES_POBS

from .cauchy import Cauchy
from .gamma import Gamma
from .logística import Logística
from .normal import Normal
from .t import T
from .triang import Triang


class TransProb(SubcategEcOrg):
    nombre = 'Prob'
    cls_ramas = [Normal, EcuaciónVacía, Cauchy, Gamma, Logística, T, Triang]
    _nombre_res = RES_TRANS

    def postproc(símismo, paso, sim):
        trans = símismo.obt_valor_res(sim)

        # Quitar los organismos que transicionaron directamente de las poblaciones (cohortes ya se actualizaron)
        símismo.poner_valor_mód(sim, RES_POBS, -trans, rel=True)
