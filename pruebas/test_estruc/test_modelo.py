import unittest

import numpy.testing as npt
import xarray.testing as xrt
from tikon.estruc import Modelo

from .rcrs import req_modelo_falta, req_var_falta, módulo_con_punto, req_cntrl_falta, req_ecuación_falta, \
    req_ecuación_inter, obt_valor_control, obt_valor_extern, var_con_punto, inic_modelo, obt_valor, poner_valor_extern


class PruebaModelo(unittest.TestCase):

    @staticmethod
    def test_inic_con_1_módulo():
        Modelo(inic_modelo.Módulo1())

    @staticmethod
    def test_inic_con_lista_módulos():
        Modelo([inic_modelo.Módulo1(), inic_modelo.Módulo2()])

    @staticmethod
    def test_inic_con_clase_módulo():
        Modelo(inic_modelo.Módulo1)

    @staticmethod
    def test_inic_con_lista_mixta():
        Modelo([inic_modelo.Módulo1, inic_modelo.Módulo2()])

    def test_módulo_con_punto(símismo):
        with símismo.assertRaises(ValueError):
            módulo_con_punto.modelo.simular('módulo con punto', exper=módulo_con_punto.exper, t=10)

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

    @staticmethod
    def test_obt_valor():
        modelo = obt_valor.modelo
        exper = obt_valor.exper
        exper.controles['var'] = 2
        res_mód = modelo.simular('valor control', exper=exper, t=10)['exper']['módulo']
        xrt.assert_equal(res_mód['res 1'].datos, res_mód['res 2'].datos)

    @staticmethod
    def test_obt_valor_control():
        modelo = obt_valor_control.modelo
        exper = obt_valor_control.exper
        exper.controles['var'] = 2
        res = modelo.simular('valor control', exper=exper, t=10)
        npt.assert_equal(res['exper']['módulo']['res'].datos.values, 2)

    @staticmethod
    def test_obt_valor_extern():
        modelo = obt_valor_extern.modelo
        exper = obt_valor_extern.exper
        res = modelo.simular('valor extern', exper=exper, t=10)
        xrt.assert_equal(res['exper']['módulo 1']['res 1'].datos, res['exper']['módulo 2']['res 2'].datos)

    @staticmethod
    def test_poner_valor_extern():
        modelo = poner_valor_extern.modelo
        exper = poner_valor_extern.exper
        const = poner_valor_extern.const
        res = modelo.simular('valor extern', exper=exper, t=10)
        npt.assert_equal(res['exper']['módulo 1']['res 1'].datos.values, const)


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
        modelo = req_ecuación_inter.modelo
        coso1 = req_ecuación_inter.coso1
        coso2 = req_ecuación_inter.coso2
        exper = req_ecuación_inter.exper

        modelo.simular('sin interacciones', exper=exper, t=10)

        coso1.interactua_con(coso2)
        with símismo.assertRaises(ValueError):
            modelo.simular('con interacciones', exper=exper, t=10)

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
