import unittest

import numpy as np
import xarray
from tikon.central import Resultado


class PruebaResultado(unittest.TestCase):
    def test_iter_índs(símismo):
        coords = {'eje1': np.arange(3), 'eje2': np.arange(4), 'eje3': ['a', 'b']}
        datos = xarray.DataArray(
            0., coords=coords, dims=['eje1', 'eje2', 'eje3']
        )

        with símismo.subTest('todos'):
            índs = list(Resultado.iter_índs(datos))
            símismo.assertEqual(len(índs), np.prod([len(v) for v in coords.values()]))
            símismo.assertTrue(all(eje in índ for índ in índs for eje in coords))

        with símismo.subTest('excluir'):
            excluir = 'eje2'
            índs = list(Resultado.iter_índs(datos, excluir=excluir))
            símismo.assertEqual(len(índs), np.prod([len(v) for ll, v in coords.items() if ll != excluir]))
            símismo.assertTrue(all(eje in índ for índ in índs for eje in coords if eje != excluir))
