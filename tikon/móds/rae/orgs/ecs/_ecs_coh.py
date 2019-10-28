from tikon.móds.rae.red.utils import RES_EDAD

from ._plntll import EcuaciónOrg


class EcuaciónConCohorte(EcuaciónOrg):

    def __init__(símismo, cosos, n_reps, ecs):
        super().__init__(cosos, n_reps, ecs)

        símismo.dist = None

    def act_vals(símismo):
        super().act_vals()
        símismo.dist = símismo._cls_dist(**símismo._prms_scipy())

    def cambio_edad(símismo, sim):
        return símismo.obt_val_mód(sim, RES_EDAD)

    @staticmethod
    def trans_cohortes(sim, cambio_edad, dist):
        return sim.cohortes.trans(cambio_edad, dist)

    @staticmethod
    def dens_dif(sim, cambio_edad, dist):
        return sim.cohortes.dens_dif(cambio_edad, dist=dist)

    @property
    def _cls_dist(símismo):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError

    def _prms_scipy(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError
