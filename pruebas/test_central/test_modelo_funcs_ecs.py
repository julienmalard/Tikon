import unittest

import numpy.testing as npt
import xarray.testing as xrt
from pruebas.test_central.rcrs import req_ecuación_falta, req_ecuación_inter, ec_obt_poner_valor, ec_postproc
from tikon.central.errores import ErrorRequísitos


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

    @unittest.skip('implementar')
    def test_obt_valor_control(símismo):
        pass

    @unittest.skip('implementar')
    def test_obt_valor_extern(símismo):
        pass

    @unittest.skip('implementar')
    def test_poner_valor_extern(símismo):
        pass

    @unittest.skip('implementar')
    def test_inter(símismo):
        pass
