from tikon.estruc.módulo import Módulo
from tikon.estruc.simul import SimulMódulo
from tikon.móds.apli.res import ResConcentración, ResDecomp


class Aplicaciones(Módulo):
    nombre = 'aplicaciones'

    def __init__(símismo, productos):
        super().__init__(productos)

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        return SimulAplicaciones(simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)

    def requísitos(símismo, controles=False):
        pass


class SimulAplicaciones(SimulMódulo):
    resultados = [ResDecomp, ResConcentración]

    def __init__(símismo, simul_exper, ecs, vars_interés):
        super().__init__(Aplicaciones.nombre, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)
