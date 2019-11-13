import unittest

import numpy as np
import numpy.testing as npt
import scipy.stats as estad
from tikon.ecs.aprioris import APrioriDens, APrioriDist
from tikon.ecs.dists import DistAnalítica


class PruebaAprioris(unittest.TestCase):
    @staticmethod
    def test_apriori_dens():
        apr = APrioriDens((0, 1), 0.9)
        trz = apr.dist((0, None)).obt_vals(10000)
        npt.assert_allclose(np.mean(np.logical_and(trz < 1, trz > 0)), 0.9, atol=0.01)

    def test_apriori_dens_líms_erróneas(símismo):
        apr = APrioriDens((0, 1), 0.9)
        with símismo.assertRaises(ValueError):
            apr.dist((1, None))

    @staticmethod
    def test_apriori_dist_scipy():
        apr = APrioriDist(estad.norm())
        trz = apr.dist((None, None)).obt_vals(10000)
        npt.assert_allclose(trz.mean(), 0, atol=0.05)
        npt.assert_allclose(trz.std(), 1, atol=0.05)

    @staticmethod
    def test_apriori_dist_analítica():
        dist = DistAnalítica(estad.norm())
        apr = APrioriDist(dist)
        trz = apr.dist((None, None)).obt_vals(10000)
        npt.assert_allclose(trz.mean(), 0, atol=0.05)
        npt.assert_allclose(trz.std(), 1, atol=0.05)

    def test_apriori_dist_líms_erróneas(símismo):
        apr = APrioriDist(estad.norm())
        with símismo.assertRaises(ValueError):
            apr.dist((1, None))
