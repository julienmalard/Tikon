import unittest
from datetime import date, datetime

import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
from tikon.central import gen_tiempo, Tiempo


class PruebaGenerarTiempo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = pd.date_range('2000-01-01', '2000-01-10', freq='D')

    def _verif_igual(símismo, t):
        pdt.assert_index_equal(t.eje, símismo.ref)

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
        t = Tiempo('૨૦૦૦-૦૧-૦૧', '૨૦૦૦-૦૧-૧૦')  # ¡Hablemos gujerati!
        símismo._verif_igual(t)

    def test_error_tipo(símismo):
        with símismo.assertRaises(TypeError):
            Tiempo(123, 456)


class PruebaFuncionalidadTiempo(unittest.TestCase):
    @staticmethod
    def test_avanzar():
        t = Tiempo('2000/01/01', '2000/02/01')
        fechas, n_días = zip(*[(f, t.n_día) for f in t.avanzar()])
        pdt.assert_index_equal(pd.Index(fechas), t.eje[1:])
        npt.assert_equal(np.array(n_días), np.arange(1, 32))
        npt.assert_equal(np.array(n_días), np.arange(1, 32))

    @staticmethod
    def test_paso():
        t = Tiempo('2000/01/01', '2000/02/01', paso=2)
        pdt.assert_index_equal(t.eje, pd.date_range('2000/01/01', '2000/01/31', freq='2D'))
        fechas, n_días = zip(*[(f, t.n_día) for f in t.avanzar()])
        pdt.assert_index_equal(pd.Index(fechas), t.eje[1:])
        npt.assert_equal(np.array(n_días), np.arange(1, 16) * 2)

    @staticmethod
    def test_reinic():
        t = Tiempo('2000/01/01', '2000/01/31')
        fechas_0 = pd.Index([f for f in t.avanzar()])
        t.reinic()
        fechas_1 = pd.Index([f for f in t.avanzar()])
        pdt.assert_index_equal(fechas_0, fechas_1)
