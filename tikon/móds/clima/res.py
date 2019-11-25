from tikon.central.res import Resultado
from tikon.utils import EJE_TIEMPO


class ResultadoClima(Resultado):

    def __init__(símismo, sim, coords, vars_interés):
        super().__init__(sim, coords, vars_interés)

    def iniciar(símismo):
        super().iniciar()
        f_inic = símismo.sim.simul_exper.t.fecha
        inic = símismo.sim.datos[símismo.nombre].loc[{EJE_TIEMPO: f_inic}].drop_vars(EJE_TIEMPO)
        símismo.datos = inic

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def unids(símismo):
        raise NotImplementedError
