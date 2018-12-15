from tikon.ecs.árb_mód import Ecuación


class EcuaciónConCohorte(Ecuación):
    _cls_dist = NotImplemented

    def __init__(símismo, cosos, í_cosos, mód, n_rep, ecs=None):
        super().__init__(cosos, í_cosos, mód, n_rep, ecs)

        símismo.dist = símismo._cls_dist(símismo._prms_scipy())

    def reinic(símismo):
        símismo.dist = símismo._cls_dist(símismo._prms_scipy())  # para hacer

    def cambio_edad(símismo):
        return símismo.obt_val_mód('Edad')

    def trans_cohortes(símismo, dist):
        símismo.mód.cohortes.trans()

    def _prms_scipy(símismo):
        raise NotImplementedError

    def eval(símismo, paso):
        raise NotImplementedError
