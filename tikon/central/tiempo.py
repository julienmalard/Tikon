import re
from datetime import date, datetime, timedelta

import pandas as pd
from எண்ணிக்கை import உரைக்கு as உ


class Tiempo(object):
    def __init__(símismo, f_inic, f_final, paso=1):
        f_inic = _gen_fecha(f_inic)
        f_final = _gen_fecha(f_final)

        if f_inic >= f_final:
            raise ValueError('Fecha inicial {inic} superior a fecha final {fin}'.format(inic=f_inic, fin=f_final))

        símismo.paso = paso
        símismo._n_pasos = (f_final - f_inic).days // paso

        símismo.eje = pd.date_range(f_inic, end=f_final, freq=str(símismo.paso) + 'D')
        símismo.i = 0

    def avanzar(símismo):
        for f in símismo.eje[1:]:
            símismo.i += 1
            yield f

    @property
    def fecha(símismo):
        return símismo.eje[símismo.i]

    @property
    def n_día(símismo):
        return símismo.i * símismo.paso

    def reinic(símismo):
        símismo.i = 0

    def __len__(símismo):
        return len(símismo.eje)


def gen_tiempo(t, datos):
    # Tiempos completamente especificados por el usuario tienen precedencia sobre datos
    if isinstance(t, Tiempo):
        return t

    # Inferir tiempos de datos de observaciones
    (f_inic, f_final), d_final = datos.fechas()
    f_inic = f_inic or date.today()
    if f_final:
        f_final = max(f_final, f_inic + timedelta(days=d_final))

    if isinstance(t, int):
        return Tiempo(f_inic=f_inic, f_final=f_inic + timedelta(days=t))

    d_final = d_final or 30
    if t is not None:
        f_inic = _gen_fecha(t)

    if f_final:
        f_final = max(f_final, f_inic + timedelta(days=d_final))
    else:
        f_final = f_inic + timedelta(days=d_final)

    return Tiempo(f_inic=f_inic, f_final=f_final)


def _gen_fecha(f):
    if isinstance(f, pd.Timestamp):
        return f
    if isinstance(f, str):
        return pd.Timestamp(
            datetime.strptime('-'.join(உ(x, 'latin') for x in re.split(r'[-/.]', f)), '%Y-%m-%d').date()
        )
    if isinstance(f, date):
        return pd.Timestamp(f)

    if isinstance(f, datetime):
        return pd.Timestamp(f.date())

    raise TypeError(type(f))
