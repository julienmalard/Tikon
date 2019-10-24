import pandas as pd
import xarray as xr
from tikon.móds.rae.red.utils import EJE_ETAPA, RES_POBS, RES_CREC, RES_DEPR, RES_MOV, RES_MRTE, RES_REPR, RES_TRANS, \
    EJE_VÍCTIMA, EJE_DEST
from tikon.result.obs import Obs
from tikon.result.utils import EJE_PARC, EJE_TIEMPO

from .red import RedAE


class ObsRAE(Obs):
    var = None

    def __init__(símismo, datos):
        super().__init__(mód=RedAE.nombre, var=símismo.var, datos=datos)

    @classmethod
    def de_csv(cls, archivo, col_tiempo, corresp, parc, factor=1):
        csv_pd = pd.read_csv(archivo, encoding='utf8')

        coords = {
            EJE_PARC: [parc],
            EJE_ETAPA: list(corresp.values()),
            EJE_TIEMPO: csv_pd[col_tiempo]
        }
        datos = xr.DataArray(csv_pd[list(corresp)] * factor, coords=coords, dims=list(coords))
        return cls(datos=datos)


class ObsPobs(ObsRAE):
    var = RES_POBS


class ObsCrec(ObsRAE):
    var = RES_CREC


class ObsRepr(ObsRAE):
    var = RES_REPR


class ObsMov(ObsRAE):
    var = RES_MOV


class ObsTrans(ObsRAE):
    var = RES_TRANS


class ObsEmigr(ObsTrans):

    def proc_res(símismo, res):
        return res.sum(dim=EJE_DEST).squeeze(EJE_DEST)


class ObsImigr(ObsTrans):

    def proc_res(símismo, res):
        return res.sum(dim=EJE_PARC).squeeze(EJE_PARC)


class ObsMuerte(ObsRAE):
    var = RES_MRTE


class ObsDepred(ObsRAE):
    var = RES_DEPR

    @classmethod
    def de_csv(cls, archivo, col_tiempo, corresp, parc, factor=1):
        csv_pd = pd.read_csv(archivo, encoding='utf8')

        coords = {
            EJE_PARC: [parc],
            EJE_ETAPA: list(corresp.values()),
            EJE_TIEMPO: csv_pd[col_tiempo],
            EJE_VÍCTIMA: NotImplemented,
        }
        datos = xr.DataArray(csv_pd[list(corresp)] * factor, coords=coords, dims=list(coords))
        return cls(datos=datos)
