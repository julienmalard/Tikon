import unittest

import numpy as np
import pandas as pd
import xarray.testing as xrt
from tikon.central import Modelo, Exper, Parcela, Tiempo
from tikon.móds.clima import Clima
from تقدیر.ذرائع import جےسن as fnt_json


class PruebaClima(unittest.TestCase):
    @staticmethod
    def test_clima():
        parc = Parcela('parc')
        lat, lon = parc.geom.centroide
        f_inic, f_final = '2000-01-01', '2000-02-01'
        eje_fechas = pd.date_range(f_inic, f_final, freq='D')
        datos = {'precip': np.random.random(eje_fechas.size), 'tiempo': eje_fechas}
        fuentes = fnt_json(datos, lat, lon, بلندی=411, تبديل_عمودی_ستون={'precip': 'بارش', 'tiempo': 'تاریخ'})
        clima = Clima(fuentes=(fuentes,), variables=['precip'])
        res = Modelo(clima).simular('clima', exper=Exper('exper', parc), t=Tiempo(f_inic, f_final), vars_interés=True)
        res_precip = res['exper']['clima']['precip']
        xrt.assert_equal(
            res_precip.datos_t,
            pd.DataFrame(datos).set_index('tiempo').to_xarray()['precip'].broadcast_like(res_precip.datos_t)
        )

    def test_fecha_falta(símismo):
        parc = Parcela('parc')
        lat, lon = parc.geom.centroide
        f_inic, f_final = '2000-01-01', '2000-02-01'
        eje_fechas = pd.date_range(f_inic, f_final, freq='D')
        datos = {'precip': np.random.random(eje_fechas.size), 'tiempo': eje_fechas}
        fuentes = fnt_json(datos, lat, lon, بلندی=0, تبديل_عمودی_ستون={'precip': 'بارش', 'tiempo': 'تاریخ'})
        clima = Clima(fuentes=(fuentes,), variables=['precip'])
        with símismo.assertRaises(ValueError):
            Modelo(clima).simular(
                'clima', exper=Exper('exper', parc), t=Tiempo(f_inic, '2000-02-02'), vars_interés=True
            )
