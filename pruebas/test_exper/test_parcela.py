import unittest

from tikon.estruc import GeomParcela


class PruebaGeomParcela(unittest.TestCase):
    def test_de_coords(símismo):
        geom = GeomParcela(coords=[(0, 0), (0, 1), (1, 1), (1, 0)])
        símismo.assertEqual(geom.centroide, (0.5, 0.5))
        símismo.assertGreater(geom.superficie, 0)
