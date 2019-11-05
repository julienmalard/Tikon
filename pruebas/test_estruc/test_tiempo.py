import unittest
from datetime import date, datetime

import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
from tikon.estruc import gen_tiempo, Tiempo


class PruebaGenerarTiempo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = pd.date_range('2000-01-01', '2000-01-10', freq='D')

    def _verif_igual(símismo, t):
        pdt.assert_index_equal(t.eje, símismo.ref)

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

    def test_auto_error_tipo(símismo):
        with símismo.assertRaises(TypeError):
            gen_tiempo(123.456)

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

    def test_error_tipo(símismo):
        with símismo.assertRaises(TypeError):
            Tiempo(123, 456)


class PruebaFuncionalidadTiempo(unittest.TestCase):
    def test_avanzar(símismo):
        t = Tiempo('2000/01/01', '2000/01/31')
        fechas, n_días = zip(*[(f, t.n_día) for f in t.avanzar()])
        pdt.assert_index_equal(pd.Index(fechas), t.eje)
        npt.assert_equal(np.array(n_días), np.arange(1, 32))

    def test_paso(símismo):
        t = Tiempo('2000/01/01', '2000/01/31', paso=2)
        pdt.assert_index_equal(t.eje, pd.date_range('2000/01/01', '2000/01/31', freq='2D'))
        fechas, n_días = zip(*[(f, t.n_día) for f in t.avanzar()])
        pdt.assert_index_equal(pd.Index(fechas), t.eje)
        npt.assert_equal(np.array(n_días), np.arange(1, 17) * 2)

    def test_reinic(símismo):
        t = Tiempo('2000/01/01', '2000/01/31')
        fechas_0 = pd.Index([f for f in t.avanzar()])
        t.reinic()
        fechas_1 = pd.Index([f for f in t.avanzar()])
        pdt.assert_index_equal(fechas_0, fechas_1)
