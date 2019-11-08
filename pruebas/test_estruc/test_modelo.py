import unittest

from tikon.estruc import Modelo

from .rcrs.ej_modelo import Módulo1, Módulo2


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
