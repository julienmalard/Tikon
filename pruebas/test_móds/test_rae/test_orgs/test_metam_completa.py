import unittest

from tikon.móds.rae.orgs.insectos import MetamCompleta


class PruebaMetamCompleta(unittest.TestCase):
    def test_metam_completa(símismo):
        ins = MetamCompleta('Metamórfosis completa')

    def test_juveniles_múltiples(símismo):
        ins = MetamCompleta('Metamórfosis completa', njuvenil=3)

    def test_sin_huevo(símismo):
        ins = MetamCompleta('Metamórfosis completa', huevo=False)

    def test_sin_adulto(símismo):
        ins = MetamCompleta('Metamórfosis completa', adulto=False)
