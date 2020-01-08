import unittest

from tikon.móds.rae.orgs.insectos import LotkaVolterra


class PruebaSencillo(unittest.TestCase):
    def test_sencillo(símismo):
        ins = LotkaVolterra('Sencillo')
        símismo.assertEqual(len(ins), 1)
