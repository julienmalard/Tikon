import unittest

import numpy.testing as npt
from pruebas.rcrs.ej_coso import EjemploCoso
from tikon.ecs.aprioris import APrioriDens


class PruebaEcsCoso(unittest.TestCase):
    def test_activar_ec(símismo):
        cs = EjemploCoso()
        cs.activar_ec('1', '1a', 'Sencilla')
        símismo.assertEqual(str(cs.ecs['1']['1a'].ec_activa()), 'Sencilla')

    def test_activar_ec_no_existe(símismo):
        cs = EjemploCoso()
        with símismo.assertRaises(ValueError):
            cs.activar_ec('1', '1a', '¡Hola! Yo no soy una ecuación válida.')

    def test_desactivar_ec(símismo):
        cs = EjemploCoso()
        cs.activar_ec('1', '1a', 'Sencilla')
        cs.desactivar_ec('1', '1a')
        símismo.assertEqual(str(cs.ecs['1']['1a'].ec_activa()), 'Nada')

    def test_desactivar_ec_por_categ(símismo):
        cs = EjemploCoso()
        cs.activar_ec('1', '1a', 'Sencilla')
        cs.desactivar_ec('1')
        símismo.assertEqual(str(cs.ecs['1']['1a'].ec_activa()), 'Nada')

    def test_activar_ecs(símismo):
        cs = EjemploCoso()
        cs.activar_ecs({'2': {'2a': 'Sencilla'}, '1': {'1a': 'Sencilla'}})
        símismo.assertEqual(str(cs.ecs['1']['1a'].ec_activa()), 'Sencilla')
        símismo.assertEqual(str(cs.ecs['2']['2a'].ec_activa()), 'Sencilla')


class PruebaApriorisCoso(unittest.TestCase):
    @staticmethod
    def test_espec_apriori():
        cs = EjemploCoso()
        apr = APrioriDens((0, 1), 0.95)
        cs.espec_apriori(apr, categ='2', sub_categ='2a', ec='Sencilla', prm='a')
        prm = cs.ecs['2']['2a']['Sencilla']['a'].cls_pariente

        dist_apriori = cs.ecs['2']['2a']['Sencilla']['a'].apriori()
        ref = apr.dist(prm.líms)
        npt.assert_equal(dist_apriori.aprox_líms(0.95), ref.aprox_líms(0.95))

    @unittest.skip('implementar')
    def test_espec_apriori_índs(símismo):
        cs = EjemploCoso()
        apr = APrioriDens((0, 1), 0.95)
        cs.espec_apriori(apr, categ='2', sub_categ='2a', ec='Sencilla', prm='a', índs=['soy', 'un'])
        prm = cs.ecs['2']['2a']['Sencilla']['a'].cls_pariente

        dist_apriori = cs.ecs['2']['2a']['Sencilla']['a'].apriori(inter=['soy', 'un', 'índice'])
        ref = apr.dist(prm.líms)
        npt.assert_equal(dist_apriori.aprox_líms(0.95), ref.aprox_líms(0.95))
        raise NotImplementedError

    @unittest.skip('implementar')
    def test_espec_apriori_líms_incompat(símismo):
        cs = EjemploCoso()
        apr = APrioriDens((0, 1), 0.95)
        cs.espec_apriori(apr, categ='2', sub_categ='2a', ec='Sencilla', prm='a')

    @unittest.skip('implementar')
    def test_verificar(símismo):
        cs = EjemploCoso()
        cs.verificar()
        raise NotImplementedError
