import unittest

import numpy as np
import numpy.testing as npt
import scipy.stats as estad
from tikon.ecs.dists import DistAnalítica, DistTraza


class PruebaDistAnalítica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.líms = {'[R,R]': (3, 7), '[R, ∞)': (1, np.inf), '(-∞, R]': (-np.inf, 4), '(-∞, +∞)': (-np.inf, np.inf)}

    def _verif_en_líms(símismo, trz, líms):
        símismo.assertTrue(líms[0] <= trz.min() and trz.max() <= líms[1])

    def test_de_líms(símismo):
        for nmbr, lm in símismo.líms.items():
            with símismo.subTest(nmbr):
                trz = DistAnalítica.de_líms(lm).obt_vals(1000)
                símismo._verif_en_líms(trz, líms=lm)

    def test_de_dens(símismo):
        inf = np.inf
        dens = 0.7
        líms = {
            '[R,R]': {
                'teor': (3, 7),
                'dens': {'ident': (3, 7), 'izq': (3, 6), 'drch': (4, 7), 'dentro': (4, 5), 'fuera': (2, 4)}
            },
            '[R, ∞)': {
                'teor': (1, inf),
                'dens': {'ident': (1, inf), 'izq': (1, 6), 'drch': (4, inf), 'dentro': (4, 5), 'fuera': (0, 4)}
            },
            '(-∞, R]': {
                'teor': (-inf, 4),
                'dens': {'ident': (-inf, 4), 'izq': (-inf, 0), 'drch': (0, 4), 'dentro': (2, 3), 'fuera': (0, 5)}
            },
            '(-∞, +∞)': {
                'teor': (-inf, inf),
                'dens': {'ident': (-inf, inf), 'izq': (-inf, 6), 'drch': (4, inf), 'dentro': (4, 5)}
            }}
        for ll, v in líms.items():
            lm_t = v['teor']
            for ll_d, lm_d in v['dens'].items():
                with símismo.subTest(líms_teor=ll, líms_dens=ll_d):
                    if ll_d in ['ident', 'fuera']:
                        with símismo.assertRaises(ValueError):
                            DistAnalítica.de_dens(dens, líms_dens=lm_d, líms=lm_t)
                    else:
                        dist = DistAnalítica.de_dens(dens, líms_dens=lm_d, líms=lm_t)
                        trz = dist.obt_vals(1000)
                        símismo._verif_en_líms(trz, lm_t)
                        npt.assert_allclose(dens, np.mean(np.logical_and(trz > lm_d[0], trz < lm_d[1])), rtol=0.05)

    def test_de_dens_0(símismo):
        with símismo.assertRaises(ValueError):
            DistAnalítica.de_dens(0, líms_dens=(0, 1), líms=(0, None))

    def test_dens_fuera(símismo):
        with símismo.assertRaises(ValueError):
            DistAnalítica.de_dens(-1, líms_dens=(0, 1), líms=(0, None))

        with símismo.assertRaises(ValueError):
            DistAnalítica.de_dens(2, líms_dens=(0, 1), líms=(0, None))

    def test_de_dens_1(símismo):
        for ll, v in símismo.líms.items():
            with símismo.subTest(líms=ll):
                if ll == '[R,R]':
                    trz = DistAnalítica.de_dens(1, líms_dens=v, líms=(2, 8)).obt_vals(1000)
                    símismo._verif_en_líms(trz, líms=v)
                else:
                    with símismo.assertRaises(ValueError):
                        DistAnalítica.de_dens(1, líms_dens=v, líms=(2, 8))

    def test_de_traza(símismo):
        pass

    def test_obt_vals(símismo):
        pass

    def test_obt_vals_índs(símismo):
        pass

    def test_aprox_líms(símismo):
        pass

    def test_tamaño(símismo):
        pass

    def test_conv_dic(símismo):
        pass


class PruebaDistTraza(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n = n = 10000
        trz = np.random.normal(0, 1, n)
        cls.dist = DistTraza(trz)

    def test_tmñ(símismo):
        símismo.assertEqual(símismo.dist.tmñ(), símismo.n)

    def test_aprox_líms(símismo):
        prc = 0.95
        líms = símismo.dist.aprox_líms(prc)
        npt.assert_allclose(líms, estad.norm.ppf([(1 - prc) / 2, 0.5 + prc / 2]), rtol=.10)

    @unittest.skip('saber')
    def test_pesos(símismo):
        dist = DistTraza(símismo.dist.trz, pesos=símismo.dist.trz.argsort())
        npt.assert_array_less(símismo.dist.aprox_líms(0.99), dist.aprox_líms(0.95))

    def test_obt_vals(símismo):
        vals = símismo.dist.obt_vals(10)
        símismo.assertTrue(np.all(np.isin(vals, símismo.dist.trz)))

    def test_obt_vals_índ(símismo):
        símismo.assertEqual(símismo.dist.obt_vals_índ(12), símismo.dist.trz[12])

    def test_obt_vals_índ_matr(símismo):
        índs = [1, 3, 765]
        npt.assert_equal(símismo.dist.obt_vals_índ(índs), símismo.dist.trz[índs])

    def test_conv_dic(símismo):
        dist = DistTraza.de_dic(símismo.dist.a_dic())
        npt.assert_allclose(dist.trz, símismo.dist.trz)
        npt.assert_allclose(dist.pesos, símismo.dist.pesos)

    def test_error_pesos(símismo):
        with símismo.assertRaises(ValueError):
            DistTraza(trz=np.arange(12), pesos=np.random.random(símismo.n + 1))
