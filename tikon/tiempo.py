import math as mat
from datetime import date, datetime, timedelta


class Tiempo(object):
    def __init__(símismo, n_días, día=0, f_inic=None, paso=1):
        símismo._f_inic = _gen_fecha(f_inic)
        símismo._día = día
        símismo._paso = paso
        símismo._n_días = n_días
        símismo.eje = EjeTiempo(días=range(día, día + mat.ceil(n_días / paso), paso), f_inic=f_inic)

    def n_pasos(símismo):
        return len(símismo.eje)

    def avanzar(símismo):
        símismo._día += símismo._paso
        return símismo._día <= símismo._n_días

    def fecha(símismo):
        if símismo._f_inic is not None:
            return símismo._f_inic + timedelta(days=símismo._día)

    def día(símismo):
        return símismo._día

    def índices(símismo, t):
        return símismo.eje.índices(t)


class EjeTiempo(object):
    def __init__(símismo, días, f_inic=None):
        símismo.días = días
        símismo.f_inic = f_inic

    def índices(símismo, t):
        if símismo.f_inic is t.f_inic is None:
            return t.días
        elif isinstance(símismo.f_inic, date) and isinstance(t.f_inic, date):
            dif = (t.f_inic - símismo.f_inic).days
            return t.días - dif

    def __len__(símismo):
        return len(símismo.días)


def _gen_fecha(f):
    if f is None:
        return
    elif isinstance(f, str):
        return datetime.strptime(str, '%Y-%m-%d')
    elif isinstance(f, date):
        return f
    elif isinstance(f, datetime):
        return f.date()
    else:
        raise TypeError(type(f))
