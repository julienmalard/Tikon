import unittest

import numpy as np
import numpy.testing as npt
import xarray.testing as xrt
from pruebas.test_central.rcrs import req_ecuación_falta, req_ecuación_inter, ec_obt_poner_valor, ec_postproc, \
    ec_valor_control, ec_obt_valor_extern, ec_poner_valor_extern, ec_parám, ec_apriori_auto
from scipy.stats import uniform
from tikon.central import Modelo
from tikon.central.calibs import EspecCalibsCorrida
from tikon.central.errores import ErrorRequísitos
from tikon.ecs.aprioris import APrioriDist


class PruebaFuncionalidadesEcs(unittest.TestCase):

    def test_req_ecuación_falta(símismo):
        modelo = req_ecuación_falta.modelo
        coso = req_ecuación_falta.coso
        exper = req_ecuación_falta.exper
        coso.activar_ec('categ', 'subcateg', 'req falta')

        with símismo.assertRaises(ErrorRequísitos):
            modelo.simular('ecuación req falta', exper=exper, t=10)

        coso.activar_ec('categ', 'subcateg', 'req controles falta')
        with símismo.assertRaises(ErrorRequísitos):
            modelo.simular('ecuación req control falta', exper=exper, t=10)

        coso.desactivar_ec('categ')
        modelo.simular('ecuaciones reqs faltan no activadas', exper=exper, t=10)

    def test_req_ecuación_inter(símismo):
        modelo = req_ecuación_inter.mi_modelo
        coso1 = req_ecuación_inter.coso1
        coso2 = req_ecuación_inter.coso2
        exper = req_ecuación_inter.exper

        modelo.simular('sin interacciones', exper=exper, t=10)

        coso1.interactua_con(coso2)
        with símismo.assertRaises(ErrorRequísitos):
            modelo.simular('con interacciones', exper=exper, t=10)

    @staticmethod
    def test_postproc():
        modelo = ec_postproc.modelo
        exper = ec_postproc.exper

        coso_pp = ec_postproc.coso_pp
        coso_pp_categ = ec_postproc.coso_pp_categ
        coso_no_pp = ec_postproc.coso_no_pp

        res = modelo.simular('postproc', exper, t=2)['exper']['módulo']['res']
        res_pp = res.datos.loc[{'coso': coso_pp}].values
        res_pp_categ = res.datos.loc[{'coso': coso_pp_categ}].values
        res_no_pp = res.datos.loc[{'coso': coso_no_pp}].values

        npt.assert_equal(res_no_pp, 0)
        npt.assert_equal(res_pp_categ, 1 + ec_postproc.agreg_postproc_categ)
        npt.assert_equal(res_pp, 1 + ec_postproc.agreg_postproc_categ + ec_postproc.agreg_postproc_subcateg)

    @staticmethod
    def test_obt_y_poner_valor():
        modelo = ec_obt_poner_valor.mi_modelo
        exper = ec_obt_poner_valor.exper
        res = modelo.simular('ec obt valor', exper, t=10, vars_interés=True)['exper']['módulo']
        xrt.assert_equal(res['res 1'].datos_t[1:], res['res 2'].datos_t[1:] + 1)

    @staticmethod
    def test_obt_valor_control():
        modelo = ec_valor_control.mi_modelo
        exper = ec_valor_control.exper
        valor = 34
        exper.controles['var control'] = valor
        res = modelo.simular('ec obt valor control', exper, t=2)['exper']['módulo']['res']
        npt.assert_equal(res.datos.values, valor)

    @staticmethod
    def test_obt_valor_extern():
        modelo = ec_obt_valor_extern.mi_modelo
        exper = ec_obt_valor_extern.exper
        valor = ec_obt_valor_extern.valor
        exper.controles['var control'] = valor
        res = modelo.simular('ec obt valor extern', exper, t=2)['exper']['módulo']['res']
        npt.assert_equal(res.datos.values, valor)

    @staticmethod
    def test_poner_valor_extern():
        modelo, exper, valor = ec_poner_valor_extern.mi_modelo, ec_poner_valor_extern.exper, ec_poner_valor_extern.valor
        exper.controles['var control'] = valor
        res = modelo.simular('ec obt valor extern', exper, t=2)['exper']['otro módulo']['res 2']
        npt.assert_equal(res.datos.values, valor)

    def test_parám(símismo):
        modelo, exper, rango = ec_parám.mi_modelo, ec_parám.exper, ec_parám.rango
        res = modelo.simular('ec obt valor extern', exper, t=2)['exper']['módulo']['res']
        símismo.assertTrue(np.all(np.logical_and(rango[0] <= res.datos.values, res.datos.values <= rango[1])))

    def test_apriori_auto(símismo):
        calibs = EspecCalibsCorrida(aprioris=True)
        modelo, exper, rango = ec_apriori_auto.mi_modelo, ec_apriori_auto.exper, ec_apriori_auto.rango
        with símismo.subTest('apriori auto'):
            res = modelo.simular('apriori auto', exper, t=2, calibs=calibs)['exper']['módulo']['res']
            símismo.assertTrue(np.all(np.logical_and(rango[0] <= res.datos.values, res.datos.values <= rango[1])))
        with símismo.subTest('apriori manual'):
            coso = ec_apriori_auto.coso
            coso.espec_apriori(APrioriDist(uniform(3, 3)), 'categ', sub_categ='subcateg', ec='ec', prm='a')
            res = modelo.simular('apriori auto', exper, t=2, calibs=calibs)['exper']['módulo']['res']
            símismo.assertTrue(np.all(np.logical_and(3 <= res.datos.values, res.datos.values <= 6)))

    def test_apriori_coso(símismo):
        exper = ec_parám.exper
        coso = ec_parám.CosoParám('hola')
        modelo = Modelo(ec_parám.MóduloParám([coso]))
        coso.espec_apriori(apriori=APrioriDist(uniform(3, 1)), categ='categ', sub_categ='subcateg', ec='ec', prm='a')

        calibs = EspecCalibsCorrida(aprioris=True)
        res = modelo.simular('apriori', exper, t=2, calibs=calibs)['exper']['módulo']['res']
        símismo.assertTrue(np.all(np.logical_and(3 <= res.datos.values, res.datos.values <= (3 + 1))))

    @unittest.skip('implementar')
    def test_inter(símismo):
        pass
