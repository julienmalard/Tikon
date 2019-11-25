import unittest

from tikon.móds.rae.orgs.insectos import Sencillo


class PruebaSencillo(unittest.TestCase):
    def test_sencillo(símismo):
        ins = Sencillo('Sencillo')
        símismo.assertEqual(len(ins), 1)
