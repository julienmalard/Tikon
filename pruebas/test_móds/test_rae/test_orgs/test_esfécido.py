import unittest

from tikon.móds.rae.orgs.insectos import Esfécido


class PruebaEsfécido(unittest.TestCase):
    def test_esfécido(símismo):
        ins = Esfécido('Esfécido')
        símismo.assertEqual(len(ins), 2)
