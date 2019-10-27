from .._ecs_coh import EcuaciónConCohorte


class EcuaciónReprCoh(EcuaciónConCohorte):

    def eval(símismo, paso, sim):
        dens_repr = símismo.dens_dif(sim, símismo.cambio_edad(sim), símismo.dist)
        pobs = símismo.pobs(sim)  # Paso ya se tomó en cuenta con cambio edad
        return símismo.cf['n'] * dens_repr * pobs

    def _prms_scipy(símismo):
        raise NotImplementedError

    @property
    def _cls_dist(símismo):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
