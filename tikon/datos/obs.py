import numpy as np
import pandas as pd
import xarray as xr

from tikon.utils import EJE_TIEMPO, EJE_PARC


class Obs(object):
    def __init__(símismo, datos):
        símismo.datos = datos

    def fechas(símismo):
        tiempos = símismo.datos[EJE_TIEMPO].values
        if np.issubdtype(tiempos.dtype, np.datetime64):
            return (pd.Timestamp(tiempos.min()), pd.Timestamp(tiempos.max())), 0
        else:
            return (None, None), tiempos.max()

    def proc_res(símismo, res):
        if not np.issubdtype(símismo.datos[EJE_TIEMPO].values.dtype, np.datetime64):
            res = res.copy()
            res[EJE_TIEMPO] = np.array(
                [x.days for x in pd.to_datetime(res[EJE_TIEMPO].values) - pd.to_datetime(res[EJE_TIEMPO].values[0])]
            )
        return res

    @property
    def mód(símismo):
        raise NotImplementedError

    @property
    def var(símismo):
        raise NotImplementedError

    @classmethod
    def de_cuadro(cls, datos_pd, corresp, eje_principal, parc=None, tiempo=None, coords=None, factor=1, **argsll):
        if isinstance(datos_pd, str):
            datos_pd = pd.read_csv(datos_pd, encoding='utf8')
        corresp = corresp or {}
        coords = {
            EJE_PARC: parc or EJE_PARC,
            EJE_TIEMPO: tiempo or EJE_TIEMPO,
            **(coords or {})
        }

        coords_xr = coords.copy()
        for dim, crd in coords.items():
            if isinstance(dim, str) and crd in datos_pd.columns:
                coords_xr[dim] = datos_pd[crd]
            else:
                coords_xr[dim] = [crd]
        coords_xr[eje_principal] = list(corresp.values())
        datos = xr.DataArray(np.nan, coords=coords_xr, dims=list(coords_xr))

        for f in datos_pd.iterrows():
            d = f[1]
            índs = {
                **{dim: d[vl] if isinstance(vl, str) and vl in d else vl for dim, vl in coords.items()},
                **{eje_principal: [corresp[x] for x in list(d.axes[0]) if x in corresp]}
            }
            vals = d[[x for x in list(d.axes[0]) if x in corresp]]
            datos.loc[índs] = vals * factor

        return cls(datos)
