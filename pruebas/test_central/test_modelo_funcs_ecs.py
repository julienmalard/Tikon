import unittest

import numpy as np
import numpy.testing as npt
import xarray.testing as xrt
from scipy.stats import uniform
from tikon.central import Modelo, Resultado
from tikon.central.errores import ErrorRequísitos
from tikon.ecs.aprioris import APrioriDist


class PruebaFuncionalidadesEcs(unittest.TestCase):

    def _verif_en(símismo, res, rango):
        if isinstance(res, Resultado):
            res = res.datos
        símismo.assertTrue(np.all(np.logical_and(rango[0] <= res.values, res.values <= rango[1])))

    def _verif_fuera_de(símismo, res, rango):
        if isinstance(res, Resultado):
            res = res.datos
        símismo.assertTrue(np.any(np.logical_or(rango[0] > res.values, res.values > rango[1])))

    def test_req_ecuación_falta(símismo):
        from .rcrs import req_ecuación_falta
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
        from .rcrs import req_ecuación_inter
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
        from .rcrs import ec_postproc
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
        from .rcrs import ec_obt_poner_valor
        modelo = ec_obt_poner_valor.mi_modelo
        exper = ec_obt_poner_valor.mi_exper
        res = modelo.simular('ec obt valor', exper, t=10, vars_interés=True)['exper']['módulo']
        xrt.assert_equal(res['res 1'].datos_t[1:], res['res 2'].datos_t[1:] + 1)

    @staticmethod
    def test_obt_valor_control():
        from .rcrs import ec_valor_control
        modelo = ec_valor_control.mi_modelo
        exper = ec_valor_control.mi_exper
        valor = 34
        exper.controles['var control'] = valor
        res = modelo.simular('ec obt valor control', exper, t=2)['exper']['módulo']['res']
        npt.assert_equal(res.datos.values, valor)

    @staticmethod
    def test_obt_valor_extern():
        from .rcrs import ec_obt_valor_extern
        modelo = ec_obt_valor_extern.mi_modelo
        exper = ec_obt_valor_extern.mi_exper
        valor = ec_obt_valor_extern.valor
        exper.controles['var control'] = valor
        res = modelo.simular('ec obt valor extern', exper, t=2)['exper']['módulo']['res']
        npt.assert_equal(res.datos.values, valor)

    @staticmethod
    def test_poner_valor_extern():
        from .rcrs import ec_poner_valor_extern
        modelo, exper, valor = ec_poner_valor_extern.mi_modelo, ec_poner_valor_extern.mi_exper, ec_poner_valor_extern.valor
        exper.controles['var control'] = valor
        res = modelo.simular('ec obt valor extern', exper, t=2)['exper']['otro módulo']['res 2']
        npt.assert_equal(res.datos.values, valor)

    def test_parám(símismo):
        from .rcrs import ec_parám
        modelo, exper, rango = ec_parám.mi_modelo, ec_parám.mi_exper, ec_parám.rango
        res = modelo.simular('ec obt valor extern', exper, t=2)['exper']['módulo']['res']
        símismo._verif_en(res, rango)

    def test_apriori_auto(símismo):
        from .rcrs import ec_apriori_auto
        modelo, exper, rango = ec_apriori_auto.mi_modelo, ec_apriori_auto.mi_exper, ec_apriori_auto.rango

        with símismo.subTest('apriori auto'):
            res = modelo.simular('apriori auto', exper, t=2)['exper']['módulo']['res']
            símismo._verif_en(res, rango)

        with símismo.subTest('apriori manual'):
            coso = ec_apriori_auto.coso
            coso.espec_apriori(APrioriDist(uniform(3, 3)), 'categ', sub_categ='subcateg', ec='ec', prm='a')
            res = modelo.simular('apriori auto', exper, t=2)['exper']['módulo']['res']
            símismo._verif_en(res, (3, 6))

    def test_apriori_coso(símismo):
        from .rcrs import ec_parám
        exper = ec_parám.mi_exper
        coso = ec_parám.CosoParám('hola')
        modelo = Modelo(ec_parám.MóduloParám([coso]))
        coso.espec_apriori(apriori=APrioriDist(uniform(3, 1)), categ='categ', sub_categ='subcateg', ec='ec', prm='a')

        res = modelo.simular('apriori', exper, t=2)['exper']['módulo']['res']
        símismo._verif_en(res, (3, 3 + 1))

    def test_borrar_apriori(símismo):
        from .rcrs import ec_parám
        exper = ec_parám.mi_exper
        coso = ec_parám.CosoParám('hola')
        módulo = ec_parám.MóduloParám([coso])
        modelo = Modelo(módulo)
        with símismo.subTest('todos'):
            coso.espec_apriori(
                apriori=APrioriDist(uniform(3, 1)), categ='categ', sub_categ='subcateg', ec='ec', prm='a'
            )
            coso.borrar_aprioris()
            res = modelo.simular('apriori', exper, t=2)['exper']['módulo']['res']
            símismo._verif_fuera_de(res, (3, 3 + 1))

        with símismo.subTest('parámetro específico'):
            coso.espec_apriori(
                apriori=APrioriDist(uniform(3, 1)), categ='categ', sub_categ='subcateg', ec='ec', prm='a'
            )
            coso.borrar_aprioris('categ', 'subcateg', 'ec', prm='a')
            res = modelo.simular('apriori', exper, t=2)['exper']['módulo']['res']
            símismo._verif_fuera_de(res, (3, 3 + 1))

        with símismo.subTest('otra rama'):
            coso.espec_apriori(
                apriori=APrioriDist(uniform(3, 1)), categ='categ', sub_categ='subcateg', ec='ec', prm='a'
            )
            coso.borrar_aprioris('categ', 'subcateg', 'ec', prm='b')
            res = modelo.simular('apriori', exper, t=2)['exper']['módulo']['res']
            símismo._verif_en(res, (3, 3 + 1))

        with símismo.subTest('de modelo'):
            coso.espec_apriori(
                apriori=APrioriDist(uniform(3, 1)), categ='categ', sub_categ='subcateg', ec='ec', prm='a'
            )
            módulo.borrar_aprioris()
            res = modelo.simular('apriori', exper, t=2)['exper']['módulo']['res']
            símismo._verif_fuera_de(res, (3, 3 + 1))

    def test_inter(símismo):
        from .rcrs import ec_inter
        modelo = ec_inter.mi_modelo
        rango = ec_inter.rango
        coso1 = ec_inter.coso1
        coso2 = ec_inter.coso2
        coso3 = ec_inter.coso3
        exper = ec_inter.exper

        with símismo.subTest('sin interacciones'):
            res = modelo.simular('sin interacciones', exper=exper, t=2, vars_interés=True)['exper']['módulo']['res']
            npt.assert_equal(res.datos.values, 0)

        with símismo.subTest('con interacciones'):
            coso1.interactua_con([coso2, coso3])
            res = modelo.simular('con interacciones', exper=exper, t=2, vars_interés=True)['exper']['módulo']['res']
            símismo._verif_en(res.datos.loc[{'coso': coso1, 'otro': [coso2, coso3]}], rango)

    def test_inter_aprioris(símismo):
        from .rcrs import ec_inter
        modelo = ec_inter.mi_modelo
        coso1 = ec_inter.coso1
        coso2 = ec_inter.coso2
        coso3 = ec_inter.coso3
        exper = ec_inter.exper

        coso1.interactua_con([coso2, coso3])
        with símismo.subTest('sin índs'):
            apriori = APrioriDist(uniform(1.5, 1))
            coso1.espec_apriori(apriori, 'categ', 'subcateg', 'ec', 'a')
            res = modelo.simular('con interacciones', exper=exper, t=2, vars_interés=True)['exper']['módulo']['res']
            símismo._verif_en(res.datos.loc[{'coso': coso1, 'otro': [coso2, coso3]}], (1.5, 1.5 + 1))

        with símismo.subTest('con índs'):
            apriori = APrioriDist(uniform(1.5, 1))
            coso1.borrar_aprioris()
            coso1.espec_apriori(apriori, 'categ', 'subcateg', 'ec', 'a', índs=[coso3])
            res = modelo.simular('con interacciones', exper=exper, t=2, vars_interés=True)['exper']['módulo']['res']
            símismo._verif_en(res.datos.loc[{'coso': coso1, 'otro': coso3}], (1.5, 1.5 + 1))
            símismo._verif_fuera_de(res.datos.loc[{'coso': coso1, 'otro': coso2}], (1.5, 1.5 + 1))
