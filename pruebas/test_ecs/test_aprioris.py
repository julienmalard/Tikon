import unittest

import numpy as np
import numpy.testing as npt
import scipy.stats as estad
from tikon.ecs.aprioris import APrioriDens, APrioriDist


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
    def test_apriori_dist():
        apr = APrioriDist(estad.norm())
        trz = apr.dist((None, None)).obt_vals(10000)
        npt.assert_almost_equal(trz.mean(), 0, decimal=2)

    def test_apriori_dist_líms_erróneas(símismo):
        apr = APrioriDist(estad.norm())
        with símismo.assertRaises(ValueError):
            apr.dist((1, None))
