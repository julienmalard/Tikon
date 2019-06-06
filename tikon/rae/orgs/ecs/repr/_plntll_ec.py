import numpy as np

from .._ecs_coh import EcuaciónConCohorte


class EcuaciónRepr(EcuaciónConCohorte):

    def _prms_scipy(símismo):
        raise NotImplementedError

    def eval(símismo, paso):
        # para hacer: ¿algo raro aquí?
        repr_de_etapa = símismo.trans_cohortes(símismo.cambio_edad(), símismo.dist, quitar=False)

        return np.multiply(símismo.cf['n'], repr_de_etapa)
