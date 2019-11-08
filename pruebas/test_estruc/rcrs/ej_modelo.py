
from tikon.estruc import Módulo, SimulMódulo, Modelo


class Módulo1(Módulo):
    nombre = 'Módulo 1'

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        return SimulMódulo1(símismo, simul_exper, vars_interés=vars_interés, ecs=ecs)


class SimulMódulo1(SimulMódulo):
    def requísitos(símismo, controles=False):
        if controles:
            return ['superficies']
        return ['Módulo 2.var 2']


class Módulo2(Módulo):
    nombre = 'Módulo 2'

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        return SimulMódulo2(símismo, simul_exper, vars_interés=vars_interés, ecs=ecs)


class SimulMódulo2(SimulMódulo):
    def requísitos(símismo, controles=False):
        if controles:
            return ['superficies']
