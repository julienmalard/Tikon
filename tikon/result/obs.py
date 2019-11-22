import numpy as np
import pandas as pd
import xarray as xr

from tikon.utils import EJE_TIEMPO, EJE_PARC


class Obs(object):
    def __init__(símismo, datos):
        símismo.datos = datos

    def fechas(símismo):
        tiempos = símismo.datos[EJE_TIEMPO].values
        return pd.Timestamp(tiempos.min()), pd.Timestamp(tiempos.max())

    def proc_res(símismo, res):
        return res

    @property
    def mód(símismo):
        raise NotImplementedError

    @property
    def var(símismo):
        raise NotImplementedError

    @classmethod
    def de_pandas(cls, datos_pd, corresp, eje_principal, parc=None, tiempo=None, coords=None, factor=1, **argsll):
        corresp = corresp or {}
        coords = {
            EJE_PARC: parc or EJE_PARC,
            EJE_TIEMPO: tiempo or EJE_TIEMPO,
            **(coords or {})
        }

        for dim, crd in coords.items():
            if isinstance(crd, str) and crd in datos_pd.columns:
                coords[dim] = datos_pd[crd]
        coords[eje_principal] = list(corresp.values())
        datos = xr.DataArray(np.nan, coords=coords, dims=list(coords))

        for f in datos_pd.iterrows():
            vals = f[list(corresp)]
            datos.loc[índs] = vals * factor

        return cls(datos)
