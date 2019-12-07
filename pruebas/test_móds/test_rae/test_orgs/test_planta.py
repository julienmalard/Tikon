import unittest

import numpy.testing as npt
from scipy.stats import uniform
from tikon.central import Modelo, Parcela, Exper
from tikon.ecs.aprioris import APrioriDist
from tikon.móds.rae.orgs.plantas import Hojas, HojasRaices, Completa
from tikon.móds.rae.red import RedAE
from tikon.utils import EJE_TIEMPO


class PruebaPlanta(unittest.TestCase):
    def test_hojas(símismo):
        plt = Hojas('Hojas')
        símismo.assertEqual(len(plt), 1)

    def test_hojas_raices(símismo):
        plt = HojasRaices('Hojas Raices')
        símismo.assertEqual(len(plt), 2)

    def test_completa(símismo):
        plt = Completa('Completa')
        símismo.assertEqual(len(plt), 7)


class PruebaEnRed(unittest.TestCase):
    @staticmethod
    def test_fijar_dens():
        plt = HojasRaices('Hojas Raices')
        apr = APrioriDist(uniform(3, 1))
        plt.fijar_dens(apr)
        exper = Exper('exper', Parcela('parc'))
        res = Modelo(RedAE(plt)).simular(
            'dens fija', exper=exper, t=5, vars_interés='red.Pobs'
        )['exper']['red']['Pobs'].res[{EJE_TIEMPO: slice(1, None)}]
        npt.assert_array_less(res.values, 3 + 1)
        npt.assert_array_less(3, res.values)
