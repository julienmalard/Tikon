import numpy as np

from .._ecs_coh import EcuaciónConCohorte


class EcuaciónRepr(EcuaciónConCohorte):

    def eval(símismo, paso):
        cf = símismo.cf

        símismo.trans_cohortes(
            cambio_edad=símismo.cambio_edad(), etps=símismo.í_cosos,
            dist=símismo.dist,
            matr_egr=repr_etp_recip, quitar=False
        )

        return np.multiply(cf['n'], repr_etp_recip)
