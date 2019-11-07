import unittest

import numpy as np
import tikon.ecs.dists.utils as utl


class PruebaUtils(unittest.TestCase):
    def test_dists(símismo):
        for nmbr in utl.dists:
            with símismo.subTest(nmbr):
                prms = utl.prms_dist(nmbr)
                líms = utl.líms_dist(nmbr)
                dist_sp = utl.obt_scipy(nmbr, {pr: np.random.random() for pr in prms})
                trz = dist_sp.rvs(10000)
                símismo.assertTrue(trz.min() >= líms[0] and trz.max() <= líms[1])
