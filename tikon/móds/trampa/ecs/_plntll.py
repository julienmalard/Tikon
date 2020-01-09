from tikon.ecs import Ecuación

from ..utils import EJE_TRAMPA


class EcuaciónTrampa(Ecuación):
    eje_cosos = EJE_TRAMPA

    @property
    def nombre(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError
