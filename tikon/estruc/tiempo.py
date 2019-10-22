from datetime import date, datetime, timedelta

import pandas as pd

from எண்ணிக்கை import உரைக்கு as உ


class Tiempo(object):
    def __init__(símismo, f_inic, f_final, paso=1):
        f_inic = _gen_fecha(f_inic)
        f_final = _gen_fecha(f_final)

        símismo.paso = paso
        símismo._n_pasos = (f_final - f_inic).days // paso

        símismo.eje = pd.date_range(f_inic, end=f_final, freq=str(símismo.paso) + 'D')
        símismo._i = 0

    def avanzar(símismo):
        for día in símismo.eje:
            símismo._i += 1
            yield día

    def fecha(símismo):
        return símismo.eje[símismo._i]

    def n_día(símismo):
        return símismo._i * símismo.paso

    def reinic(símismo):
        símismo._i = 0

    def __len__(símismo):
        return len(símismo.eje)


def gen_tiempo(t):
    if isinstance(t, Tiempo):
        return t
    elif isinstance(t, int):
        f_inic = date.today()
        return Tiempo(f_inic=f_inic, f_final=f_inic + timedelta(days=t))
    elif isinstance(t, str):
        return Tiempo(f_inic=t, f_final=_gen_fecha(t) + timedelta(days=30))
    else:
        raise TypeError()


def _gen_fecha(f):
    if isinstance(f, pd.Timestamp):
        return f
    if isinstance(f, str):
        return pd.Timestamp(datetime.strptime('-'.join(உ(x, 'latin') for x in str.split('-/.')), '%Y-%m-%d').date())
    if isinstance(f, date):
        return pd.Timestamp(f)
    if isinstance(f, datetime):
        return pd.Timestamp(f.date())

    raise TypeError(type(f))
