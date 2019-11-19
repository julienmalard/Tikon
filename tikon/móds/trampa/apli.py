from tikon.central.módulo import Módulo
from tikon.central.simul import SimulMódulo
from tikon.ecs.paráms import Inter
from tikon.móds.apli.res import ResConcentración, ResDecomp, ResMortalidad
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.red.utils import EJE_ETAPA


class Aplicaciones(Módulo):
    nombre = 'aplicaciones'

    def __init__(símismo, productos):
        super().__init__(productos)

    @property
    def productos(símismo):
        return [símismo[prod] for prod in símismo]


class SimulAplicaciones(SimulMódulo):
    resultados = [ResDecomp, ResConcentración, ResMortalidad]

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        super().__init__(mód, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)

    def inter(símismo, coso, tipo):
        if isinstance(tipo, str):
            tipo = [tipo]

        etps_inter = set()
        for tp in tipo:
            if tp == 'etapa':
                etps_inter.update(símismo.simul_exper[RedAE.nombre].etapas)
            else:
                raise ValueError(tipo)
        inter = [[str(etp.org), str(etp)] for etp in etps_inter]
        if len(inter):
            return Inter(inter, eje=EJE_ETAPA)
