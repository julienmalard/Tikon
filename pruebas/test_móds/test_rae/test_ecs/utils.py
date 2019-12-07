import numpy as np
from tikon.central import Modelo
from tikon.móds.clima import Clima

from تقدیر.ذرائع import جےسن as fnt_json

from tikon.utils import EJE_PARC


def gen_modelo_reqs_clima(ec, exper, módulos, t):
    reqs_móds = ec.requísitos() or set()
    reqs_clima = set()
    for req in reqs_móds:
        mód, var = req.split('.')
        if mód == 'clima':
            reqs_clima.add(var)
    if reqs_clima:
        lat, lon = exper.controles['centroides'][{EJE_PARC: 0}].matr
        elev = exper.controles['elevaciones'][{EJE_PARC: 0}].matr

        datos = {'tiempo': t.eje, **{vr: np.random.random(len(t)) for vr in reqs_clima}}
        if 'temp_máx' in datos and 'temp_mín' in datos:
            datos['temp_máx'] = datos['temp_máx'] + datos['temp_mín']

        fuente = fnt_json(
            datos, lat, lon, elev,
            تبديل_عمودی_ستون={'tiempo': 'تاریخ'}
        )
        modelo = Modelo([módulos, Clima(fuentes=(fuente,))])
    else:
        modelo = Modelo(módulos)

    return modelo
