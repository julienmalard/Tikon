import unittest
from datetime import date

import pandas as pd
from tikon.estruc import gen_tiempo


class PruebaGenerarTiempo(unittest.TestCase):
    def test_int(símismo):
        t = gen_tiempo(10)
        símismo.assertEqual(t.fecha, pd.Timestamp(date.today()))
        símismo.assertEqual(len(t), 10 + 1)
