import scipy.stats as estad

from ._plntll_ec import EcuaciónOrg


class EcuaciónConCohorte(EcuaciónOrg):
    _cls_dist = NotImplemented

    def __init__(símismo, cosos, sim, n_reps, í_cosos, ecs):
        super().__init__(cosos, sim, n_reps, í_cosos, ecs)

        símismo.dist = None  # type: estad.rv_continuous

    def act_vals(símismo):
        super().act_vals()
        símismo.dist = símismo._cls_dist(**símismo._prms_scipy())

    def cambio_edad(símismo):
        return símismo.obt_val_mód(EDAD)

    def trans_cohortes(símismo, cambio_edad, dist, quitar=True):
        return símismo.sim.cohortes.trans(cambio_edad, dist, etapas=símismo.cosos, quitar=quitar)

    def _prms_scipy(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError
