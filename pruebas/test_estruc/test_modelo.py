import unittest

from tikon.estruc import Modelo, Módulo, SimulMódulo


class Módulo1(Módulo):
    nombre = 'Módulo 1'

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        pass


class SimulMódulo1(SimulMódulo):
    def requísitos(símismo, controles=False):
        pass

