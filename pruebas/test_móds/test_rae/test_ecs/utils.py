import numpy as np
import pandas as pd
from tikon.central import Modelo
from tikon.móds.clima import Clima

from تقدیر.ذرائع import جےسن as fnt_json


def gen_modelo_reqs_clima(ec, exper, módulos, t):
    reqs_móds = ec.requísitos() or set()
    reqs_clima = set()
    for req in reqs_móds:
        mód, var = req.split('.')
        if mód == 'clima':
            reqs_clima.add(var)
    if reqs_clima:
        lat, lon = exper.controles['centroides'][0].values
        elev = exper.controles['elevaciones'][0].values

        fuente = fnt_json(
            {'tiempo': t.eje,
             **{vr: np.random.random(len(t)) for vr in reqs_clima}}, lat, lon, elev,
            تبديل_عمودی_ستون={'tiempo': 'تاریخ'}
        )
        modelo = Modelo([módulos, Clima(fuentes=(fuente,))])
    else:
        modelo = Modelo(módulos)

    return modelo
