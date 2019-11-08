from tikon.ecs.paráms import Inter
from tikon.estruc.módulo import Módulo
from tikon.estruc.simul import SimulMódulo
from tikon.móds.apli.res import ResConcentración, ResDescomp, ResMortalidad
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.red.utils import EJE_ETAPA


class SimulAplicaciones(SimulMódulo):
    resultados = [ResDescomp, ResConcentración, ResMortalidad]

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


class Aplicaciones(Módulo):
    nombre = 'aplicaciones'
    cls_simul = SimulAplicaciones

    def __init__(símismo, productos):
        super().__init__(productos)

    @property
    def productos(símismo):
        return [símismo[prod] for prod in símismo]
