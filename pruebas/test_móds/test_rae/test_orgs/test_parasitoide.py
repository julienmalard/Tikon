import unittest

from tikon.móds.rae.orgs.insectos import Parasitoide


class PruebaParasitoide(unittest.TestCase):
    def test_parasitoide(símismo):
        ins = Parasitoide('Parasitoide')
        símismo.assertEqual(len(ins), 2)

    def test_con_pupa(símismo):
        ins = Parasitoide('Parasitoide', pupa=True)
        símismo.assertEqual(len(ins), 3)
