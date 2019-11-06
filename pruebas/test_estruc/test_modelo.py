import unittest

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


class PruebaModelo(unittest.TestCase):
    def test_var_con_punto(símismo):
        pass

    def test_req_modelo_falta(símismo):
        Modelo(Módulo1())

    def test_req_var_falta(símismo):
        pass

    def test_req_control_falta(símismo):
        pass


class PruebaVarsInterés(unittest.TestCase):
    def test_todos(símismo):
        pass

    def test_ninguno(símismo):
        pass

    def test_obs(símismo):
        pass

    def test_nombres(símismo):
        pass

    def test_módulos(símismo):
        pass
