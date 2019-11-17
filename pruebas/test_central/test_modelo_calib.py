import tempfile
import unittest

from .rcrs.modelo_calib import generar


class PruebaCalib(unittest.TestCase):
    def test_calib(símismo):
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        modelo.calibrar('calib', exper, n_iter=30)
        valid = modelo.simular('valid', exper, calibs=['calib']).validar()
        símismo.assertGreater(valid['ens'], 0.99)

    @unittest.skip('implementar')
    def test_calib_paráms_mód(símismo):
        pass

    @unittest.skip('implementar')
    def test_calib_con_inic(símismo):
        pass

    @unittest.skip('implementar')
    def test_calib_exluir_inic(símismo):
        pass

    @unittest.skip('implementar')
    def test_calib_solamente_inic(símismo):
        pass

    @unittest.skip('implementar')
    def test_renombrar_calib(símismo):
        pass

    @unittest.skip('implementar')
    def test_borrar_calib(símismo):
        pass

    def test_guardar_cargar_calib(símismo):
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        modelo.calibrar('calib', exper, n_iter=30)

        with tempfile.TemporaryDirectory() as d:
            modelo.guardar_calibs(d)

            otro = generar()
            otro_modelo = otro['modelo']
            otro_exper = otro['exper']
            otro_modelo.cargar_calibs(d)
            valid = otro_modelo.simular('valid', otro_exper, calibs=['calib']).validar()
            símismo.assertGreater(valid['ens'], 0.99)
