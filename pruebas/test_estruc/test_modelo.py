import unittest

from .rcrs import req_modelo_falta, req_var_falta, var_con_punto, req_cntrl_falta


class PruebaModelo(unittest.TestCase):
    def test_var_con_punto(símismo):
        with símismo.assertRaises(ValueError):
            var_con_punto.modelo.simular('var con punto', exper=var_con_punto.exper, t=10)

    def test_req_modelo_falta(símismo):
        with símismo.assertRaises(ValueError):
            req_modelo_falta.modelo.simular('simul modelo falta', exper=req_modelo_falta.exper, t=10)

    def test_req_var_falta(símismo):
        with símismo.assertRaises(ValueError):
            req_var_falta.modelo.simular('var modelo falta', exper=req_var_falta.exper, t=10)

    def test_req_ecuación_falta(símismo):
        pass

    def test_req_control_falta(símismo):
        with símismo.assertRaises(ValueError):
            req_cntrl_falta.modelo.simular('simul modelo falta', exper=req_cntrl_falta.exper, t=10)


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
