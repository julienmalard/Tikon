import unittest

from pruebas.rcrs.ej_coso import EjemploCoso


class PruebaCoso(unittest.TestCase):
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
        pass

    def test_categ_activa(símismo):
        cs = EjemploCoso()
        # cs.categ_activa()

    def test_verificar(símismo):
        pass

    def test_requísitos(símismo):
        pass
