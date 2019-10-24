import pandas as pd
from tikon.result.utils import EJE_TIEMPO


class Obs(object):
    def __init__(símismo, mód, var, datos):
        símismo.mód = mód
        símismo.var = var
        símismo.datos = datos

    def fechas(símismo):
        tiempos = símismo.datos[EJE_TIEMPO].values
        return pd.Timestamp(tiempos.min()), pd.Timestamp(tiempos.max())

    def proc_res(símismo, res):
        return res
