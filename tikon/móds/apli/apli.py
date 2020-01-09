from tikon.central.módulo import Módulo
from tikon.central.simul import SimulMódulo
from tikon.ecs.paráms import Inter
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import EJE_ETAPA

from .ecs import EcsProducto
from .res import ResConcentración, ResDescomp, ResMortalidad
from .utils import EJE_PRODUCTO


class SimulAplicaciones(SimulMódulo):
    resultados = [ResDescomp, ResConcentración, ResMortalidad]

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        super().__init__(mód, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)


class Aplicaciones(Módulo):
    nombre = 'aplicaciones'
    cls_simul = SimulAplicaciones
    cls_ecs = EcsProducto
    eje_coso = EJE_PRODUCTO

    def __init__(símismo, productos):
        super().__init__(productos)

    @property
    def productos(símismo):
        return [símismo[prod] for prod in símismo]

    def inter(símismo, modelo, coso, tipo):
        if isinstance(tipo, str):
            tipo = [tipo]

        etps_inter = set()
        for tp in tipo:
            if tp == 'etapa':
                etps_inter.update(modelo[RedAE.nombre].etapas)
            else:
                raise ValueError(tipo)
        if len(etps_inter):
            return Inter(etps_inter, eje=EJE_ETAPA, coords=etps_inter)
