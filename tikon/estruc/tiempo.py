import math as mat
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from எண்ணிக்கை import உரைக்கு as உ

class Tiempo(object):
    def __init__(símismo, n_días, f_inic, paso=1):
        símismo._f_inic = _gen_fecha(f_inic)
        símismo._día = 0
        símismo.paso = paso
        símismo._n_días = n_días
        símismo.eje = pd.to_timedelta(símismo.días, unit='D') + pd.to_datetime(símismo.f_inic)

    def n_pasos(símismo):
        return len(símismo.eje)

    def avanzar(símismo):
        símismo._día += símismo.paso
        return símismo._día <= símismo._n_días

    def fecha(símismo):
        if símismo._f_inic is not None:
            return símismo._f_inic + timedelta(days=símismo._día)

    def día(símismo):
        return símismo._día

    def índices(símismo, t):
        return símismo.eje.índices(t)

    def reinic(símismo):
        símismo._día = 0

    def __len__(símismo):
        return len(símismo.eje)


class EjeTiempo(object):
    def __init__(símismo, días, f_inic=None):
        if not isinstance(días, np.ndarray):
            días = np.array(días)
        símismo.días = días
        símismo.f_inic = f_inic

    def índices(símismo, t):
        if símismo.f_inic is t.f_inic is None:
            dif = 0
        else:
            dif = (t.f_inic - símismo.f_inic).days
        return t.días - dif

    def vec(símismo):
        if símismo.f_inic:
            return pd.to_timedelta(símismo.días, unit='D') + pd.to_datetime(símismo.f_inic)
        else:
            return np.array(símismo.días)

    def cortar(símismo, eje):
        índs_eje = símismo.índices(eje)
        máx = índs_eje.max()
        mín = índs_eje.min()

        días = símismo.días
        return EjeTiempo(días=días[np.logical_and(días >= mín, días <= máx)], f_inic=símismo.f_inic)


def _gen_fecha(f):
    if isinstance(f, str):
        return datetime.strptime('-'.join(உ(x, 'latin') for x in str.split('-/.')), '%Y-%m-%d')
    elif isinstance(f, date):
        return f
    elif isinstance(f, datetime):
        return f.date()
    else:
        raise TypeError(type(f))
