from tikon.estruc.módulo import Módulo
from tikon.estruc.simul import SimulMódulo
from tikon.móds.apli.res import ResConcentración, ResDecomp
from tikon.result.utils import gen_coords_base


class Aplicaciones(Módulo):
    nombre = 'aplicaciones'

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        return SimulAplicaciones(simul_exper=simul_exper, ecs=ecs)


class SimulAplicaciones(SimulMódulo):
    def __init__(símismo, simul_exper, ecs):
        coords = gen_coords_base()
        l_res = [
            ResDecomp(),
            ResConcentración()
        ]
        super().__init__(Aplicaciones.nombre, resultados=l_res, simul_exper=simul_exper, ecs=ecs)
