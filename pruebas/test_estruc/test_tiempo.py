import unittest
from datetime import date, datetime

import pandas as pd
import pandas.testing as pdt
from tikon.estruc import gen_tiempo, Tiempo


class PruebaGenerarTiempo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Tiempo('2000-01-01', '2000-01-10')

    def _verif_igual(símismo, t):
        pdt.assert_index_equal(t.eje, símismo.ref.eje)

    def test_auto_int(símismo):
        t = gen_tiempo(10)
        símismo.assertEqual(t.fecha, pd.Timestamp(date.today()))
        símismo.assertEqual(len(t), 10 + 1)

    def test_auto_ya_tiempo(símismo):
        t = Tiempo('2000-01-01', '2000-02-01')
        símismo.assertIs(t, gen_tiempo(t))

    def test_auto_texto(símismo):
        t = gen_tiempo('2000-01-01')
        símismo.assertEqual(len(t), 30 + 1)
        símismo.assertEqual(t.fecha, pd.Timestamp(date(2000, 1, 1)))

    def test_de_fecha(símismo):
        t = Tiempo(date(2000, 1, 1), date(2000, 1, 10))
        símismo._verif_igual(t)

    def test_de_fechatiempo(símismo):
        t = Tiempo(datetime(2000, 1, 1), datetime(2000, 1, 10))
        símismo._verif_igual(t)

    def test_de_pandas(símismo):
        t = Tiempo(pd.Timestamp(2000, 1, 1), pd.Timestamp(2000, 1, 10))
        símismo._verif_igual(t)

    def test_otro_idioma(símismo):
        t = Tiempo('૨૦૦૦-૦૧-૦૧', '૨૦૦૦-૦૧-૧૦')
        símismo._verif_igual(t)


class PruebaFuncionalidadTiempo(unittest.TestCase):
    pass
