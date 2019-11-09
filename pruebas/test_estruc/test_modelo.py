import unittest

from .rcrs import req_modelo_falta, req_var_falta, var_con_punto, req_cntrl_falta, req_ecuación_falta


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

    def test_req_control_falta(símismo):
        with símismo.assertRaises(ValueError):
            req_cntrl_falta.modelo.simular('simul modelo falta', exper=req_cntrl_falta.exper, t=10)

    def test_obt_valor(símismo):
        pass

    def test_obt_valor_control(símismo):
        pass

    def test_obt_valor_extern(símismo):
        pass

    def test_poner_valor_extern(símismo):
        pass


class PruebaFuncionalidadesEcs(unittest.TestCase):

    def test_req_ecuación_falta(símismo):
        modelo = req_ecuación_falta.modelo
        coso = req_ecuación_falta.coso
        exper = req_ecuación_falta.exper
        coso.activar_ec('categ', 'subcateg', 'req falta')

        with símismo.assertRaises(ValueError):
            modelo.simular('ecuación req falta', exper=exper, t=10)

        coso.activar_ec('categ', 'subcateg', 'req controles falta')
        with símismo.assertRaises(ValueError):
            modelo.simular('ecuación req control falta', exper=exper, t=10)

        coso.desactivar_ec('categ')
        modelo.simular('ecuaciones reqs faltan no activadas', exper=exper, t=10)

    def test_req_ecuación_inter(símismo):
        pass

    def test_obt_valor(símismo):
        pass

    def test_postproc(símismo):
        pass

    def test_obt_valor_control(símismo):
        pass

    def test_obt_valor_extern(símismo):
        pass

    def test_poner_valor_extern(símismo):
        pass

    def test_inter(símismo):
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
