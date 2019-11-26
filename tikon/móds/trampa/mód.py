from tikon.central.módulo import Módulo
from tikon.central.simul import SimulMódulo
from tikon.ecs.paráms import Inter
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import EJE_ETAPA

from .ecs import EcsTrampa
from .res import ResDensidad, ResDescomp, ResCaptura
from .utils import EJE_TRAMPA


class SimulAplicaciones(SimulMódulo):
    resultados = [ResDescomp, ResDensidad, ResCaptura]

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        super().__init__(mód, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)


class Trampas(Módulo):
    nombre = 'trampas'
    cls_simul = SimulAplicaciones
    cls_ecs = EcsTrampa
    eje_coso = EJE_TRAMPA

    def __init__(símismo, trampas):
        super().__init__(trampas)

    @property
    def trampas(símismo):
        return [símismo[trampa] for trampa in símismo]

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
