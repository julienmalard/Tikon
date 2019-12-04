from tikon.móds.rae.utils import RES_REPR

from .._ecs_coh import EcuaciónConCohorte
from .._plntll import EcuaciónOrg


class EcuaciónRepr(EcuaciónOrg):
    _nombre_res = RES_REPR

    def eval(símismo, paso, sim):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError


class EcuaciónReprCoh(EcuaciónRepr, EcuaciónConCohorte):

    def eval(símismo, paso, sim):
        dens_repr = símismo.dens_dif(sim, símismo.cambio_edad(sim), símismo.dist)
        return símismo.cf['n'] * dens_repr  # Paso y pobs ya se tomaron en cuenta con cambio edad

    def _prms_scipy(símismo):
        raise NotImplementedError

    @property
    def _cls_dist(símismo):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
