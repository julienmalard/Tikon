from tikon.ecs.árb_mód import Ecuación


class EcuaciónConCohorte(Ecuación):

    def cambio_edad(símismo):
        return símismo.obt_val_mód('Edad')

    def __call__(símismo, paso):
        raise NotImplementedError


class EcuaciónDistConCohorte(EcuaciónConCohorte):

    _cls_dist = NotImplemented

    def __init__(símismo, cosos, í_cosos, mnjdr_móds):
        super().__init__(cosos, í_cosos, mnjdr_móds)

        símismo.dist = símismo._cls_dist(símismo._prms_scipy())

    def reinic(símismo):
        símismo.dist = símismo._cls_dist(símismo._prms_scipy())  # para hacer

    def _prms_scipy(símismo):
        raise NotImplementedError

    def __call__(símismo, paso):
        raise NotImplementedError
