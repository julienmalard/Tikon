import numpy as np

from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import SubcategEcOrg, CategEcOrg
from tikon.móds.rae.orgs.ecs.utils import ECS_MRTE
from tikon.móds.rae.utils import RES_MRTE
from .constante import Constante
from .lognorm_temp import LogNormTemp
from .sig_temp import SigmoidalTemperatura
from .lluvia_linear import LluviaLinear


class EcMuerte(SubcategEcOrg):
    nombre = 'Ecuación'
    cls_ramas = [Constante, EcuaciónVacía, LogNormTemp, SigmoidalTemperatura, LluviaLinear]
    _nombre_res = ECS_MRTE


class EcsMuerte(CategEcOrg):
    nombre = ECS_MRTE
    cls_ramas = [EcMuerte]
    _nombre_res = RES_MRTE

    def postproc(símismo, paso, sim):
        """
        Convertimos mortalidad a muertes absolutas, según el número de pasos y la población inicial.

        .. math::
           f(x) = x * (1-(1-q)^p)

        Donde:
        - `f(x)` es la mortalidad absoluta
        - `p` es el paso
        - `q` es la taza de mortalidad para 1 paso

        Parameters
        ----------
        paso
        sim
        """

        pobs = símismo.pobs(sim)
        q = símismo.obt_valor_res(sim)
        muertes = (pobs * (1 - (1 - q) ** paso)).fi(np.round)

        símismo.poner_valor_res(sim, val=muertes)
        símismo.ajust_pobs(sim, -muertes)
