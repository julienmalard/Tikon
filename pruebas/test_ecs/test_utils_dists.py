import unittest

import numpy as np
import tikon.ecs.dists.utils as utl


class PruebaUtils(unittest.TestCase):
    def test_dists(símismo):
        for nmbr in utl.dists:
            with símismo.subTest(nmbr):
                prms = utl.prms_dist(nmbr)
                líms = utl.líms_dist(nmbr)
                d_prms = {pr: np.random.random() for pr in prms}
                dist_sp = utl.obt_scipy(nmbr, d_prms)
                trz = dist_sp.rvs(10000)
                símismo.assertTrue(
                    trz.min() >= líms[0] * d_prms['scale'] + d_prms['loc']
                    and trz.max() <= líms[1] * d_prms['scale'] + d_prms['loc']
                )

    def test_nombre_equivocado(símismo):
        with símismo.assertRaises(ValueError):
            utl.obt_scipy('no existo', {})
