from tikon.ecs import Ecuación

from ..utils import EJE_PRODUCTO


class EcuaciónProd(Ecuación):
    eje_cosos = EJE_PRODUCTO

    @property
    def nombre(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError
