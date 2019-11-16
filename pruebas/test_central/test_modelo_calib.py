import unittest

from .rcrs.modelo_calib import modelo, exper, coso


class PruebaCalib(unittest.TestCase):
    def test_calib(símismo):
        modelo.calibrar('calib', exper, n_iter=30)
        valid = modelo.simular('valid', exper, calibs=['calib']).validar()
        símismo.assertGreater(valid['ens'], 0.99)

    @unittest.skip('implementar')
    def test_calib_paráms_mód(símismo):
        pass
