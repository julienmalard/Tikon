import unittest

import numpy as np
import tikon.ecs.dists.utils as utl
from scipy.stats import beta


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


class PruebaLímsDist(unittest.TestCase):
    def test_líms_de_nombre(símismo):
        símismo.assertTupleEqual(utl.líms_dist('Uniforme'), (0, 1))

    def test_líms_de_dist(símismo):
        dists = {
            'sin args': [beta(1, 2), (0, 1)],
            '2 args llave': [beta(1, 2, loc=2, scale=3), (2, 3)],
            'arg escala llave ubic pos': [beta(1, 2, 2, scale=3), (2, 3)],
            'arg escal llave': [beta(1, 2, scale=3), (0, 3)],
            'arg ubic pos': [beta(1, 2, 2), (2, 1)],
            '2 args pos': [beta(1, 2, 2, 3), (2, 3)]
        }
        for nmbr, (dist, ref) in dists.items():
            with símismo.subTest(nmbr):
                símismo.assertTupleEqual(utl.obt_ubic_escl(dist), ref)
