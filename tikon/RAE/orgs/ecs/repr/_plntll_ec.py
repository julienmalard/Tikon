from .._ecs_coh import EcuaciónConCohorte
import numpy as np


class EcuaciónRepr(EcuaciónConCohorte):

    def __call__(símismo, paso):
        cf = símismo.cf

        símismo.trans_cohortes(
            cambio_edad=símismo.cambio_edad(), etps=símismo._í_cosos,
            dist=símismo.dist,
            matr_egr=repr_etp_recip, quitar=False
        )

        return np.multiply(cf['n'], repr_etp_recip)