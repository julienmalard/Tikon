from tikon.central.matriz import Datos
from ._plntll import EcuaciónOrg
from ...utils import RES_EDAD, RES_COHORTES


class EcuaciónConCohorte(EcuaciónOrg):

    def __init__(símismo, modelo, mód, exper, cosos, n_reps, ecs):
        super().__init__(modelo, mód, exper, cosos=cosos, n_reps=n_reps, ecs=ecs)

        símismo.dist = None

    def act_vals(símismo):
        super().act_vals()
        símismo.dist = símismo._cls_dist(**{
            ll: v.matr if isinstance(v, Datos) else v for ll, v in símismo._prms_scipy().items()
        })

    def cambio_edad(símismo, sim):
        return símismo.obt_valor_mód(sim, RES_EDAD)

    @staticmethod
    def trans_cohortes(sim, cambio_edad, dist):
        return sim[RES_COHORTES].trans(cambio_edad, dist)

    @staticmethod
    def dens_dif(sim, cambio_edad, dist):
        return sim[RES_COHORTES].dens_dif(cambio_edad, dist=dist)

    @property
    def _nombre_res(símismo):
        raise NotImplementedError

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
