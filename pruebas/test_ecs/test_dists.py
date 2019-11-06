import unittest
import warnings

import numpy as np
import numpy.testing as npt
import scipy.stats as estad
from tikon.ecs.dists import DistTraza


class PruebaDistAnalítica(unittest.TestCase):
    pass


class PruebaDistTraza(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n = n = 10000
        trz = np.random.normal(0, 1, n)
        pesos = np.ones(n)
        cls.dist = DistTraza(trz, pesos=pesos)

    def test_tmñ(símismo):
        símismo.assertEqual(símismo.dist.tmñ(), símismo.n)

    def test_aprox_líms(símismo):
        prc = 0.95
        líms = símismo.dist.aprox_líms(prc)
        npt.assert_allclose(líms, estad.norm.ppf([(1 - prc) / 2, 0.5 + prc / 2]), rtol=.10)
    @unittest.skip('saber')
    def test_pesos(símismo):
        dist = DistTraza(símismo.dist.trz, pesos=símismo.dist.trz.argsort())
        líms1, líms2 = dist.aprox_líms(0.75), símismo.dist.aprox_líms(0.75)
        símismo.assertLess(líms2[0], líms1[0])
        símismo.assertLess(líms1[1], líms2[1])

    def test_obt_vals(símismo):
        vals = símismo.dist.obt_vals(10)
        símismo.assertTrue(np.all(np.isin(vals, símismo.dist.trz)))

    def test_obt_vals_más_tamaño(símismo):
        with warnings.catch_warnings(record=True) as w:
            vals = símismo.dist.obt_vals(símismo.n + 1)
            símismo.assertTrue(len(w) > 0)
        símismo.assertTrue(vals.size == símismo.n + 1)

    def test_obt_vals_índ(símismo):
        símismo.assertEqual(símismo.dist.obt_vals_índ(12), símismo.dist.trz[12])

    def test_obt_vals_índ_matr(símismo):
        índs = [1, 3, 765]
        npt.assert_equal(símismo.dist.obt_vals_índ(índs), símismo.dist.trz[índs])

    def test_conv_dict(símismo):
        dist = DistTraza.de_dic(símismo.dist.a_dic())
        npt.assert_allclose(dist.trz, símismo.dist.trz)
        npt.assert_allclose(dist.pesos, símismo.dist.pesos)

    def test_error_pesos(símismo):
        with símismo.assertRaises(ValueError):
            DistTraza(trz=np.arange(12), pesos=np.random.random(símismo.n + 1))
