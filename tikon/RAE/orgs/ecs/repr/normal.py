from tikon.ecs.paráms import Parám
from .._ecs_coh import EcuaciónDistConCohorte


class N(Parám):
    nombre = 'n'
    líms = (0, None)


class Mu(Parám):
    nombre = 'mu'
    líms = (0, None)


class Sigma(Parám):
    nombre = 'sigma'
    líms = (0, None)


class Normal(EcuaciónDistConCohorte):
    """

    """
    nombre = 'Normal'
    _cls_ramas = [N, Mu, Sigma]

    def _prms_scipy(símismo):
        return dict(loc=símismo._ramas['mu'], scale=símismo._ramas['sigma'])

    def __call__(símismo, paso):
        símismo.trans_cohortes(
            cambio_edad=símismo.cambio_edad(), etps=símismo._í_cosos,
            dists=símismo.dist,
            matr_egr=repr_etp_recip, quitar=False
        )
        return np.multiply(cf['n'], repr_etp_recip)
