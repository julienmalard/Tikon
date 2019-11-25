import unittest

from tikon.móds.rae.orgs.insectos import MetamIncompleta


class PruebaMetamCompleta(unittest.TestCase):
    def test_metam_incompleta(símismo):
        ins = MetamIncompleta('Metamórfosis incompleta')

    def test_juveniles_múltiples(símismo):
        ins = MetamIncompleta('Metamórfosis incompleta', njuvenil=3)

    def test_sin_huevo(símismo):
        ins = MetamIncompleta('Metamórfosis incompleta', huevo=False)

    def test_sin_adulto(símismo):
        ins = MetamIncompleta('Metamórfosis incompleta', adulto=False)
