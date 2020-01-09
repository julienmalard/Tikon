from tikon.móds.rae.utils import EJE_ETAPA, EJE_VÍCTIMA, RES_POBS, RES_CREC, RES_DEPR, RES_MOV, RES_MRTE, RES_REPR, \
    RES_TRANS
from tikon.datos import Obs
from tikon.utils import EJE_PARC, EJE_DEST

from .red import RedAE


class ObsRAE(Obs):
    mód = RedAE.nombre

    @classmethod
    def de_cuadro(cls, datos_pd, corresp, coords=None, tiempo=None, parcela=None, factor=1, **argsll):
        return super().de_cuadro(
            datos_pd, corresp=corresp, eje_principal=EJE_ETAPA, parc=parcela, tiempo=tiempo, coords=coords, factor=factor
        )

    @property
    def var(símismo):
        raise NotImplementedError


class ObsPobs(ObsRAE):
    var = RES_POBS


class ObsCrec(ObsRAE):
    var = RES_CREC


class ObsRepr(ObsRAE):
    var = RES_REPR


class ObsTrans(ObsRAE):
    var = RES_TRANS


class ObsMov(ObsRAE):
    var = RES_MOV

    @classmethod
    def de_cuadro(cls, datos_pd, corresp, tiempo=None, parcela=None, dest=None, factor=1, **argsll):
        coords = {
            EJE_DEST: dest or EJE_DEST,
        }
        return super().de_cuadro(
            datos_pd, corresp=corresp, coords=coords, tiempo=tiempo, parcela=parcela, factor=factor
        )


class ObsEmigr(ObsTrans):

    def proc_res(símismo, res):
        res = super().proc_res(res)
        return res.sum(dim=EJE_DEST).squeeze(EJE_DEST, drop=True)


class ObsImigr(ObsTrans):

    def proc_res(símismo, res):
        res = super().proc_res(res)
        return res.sum(dim=EJE_PARC).squeeze(EJE_PARC, drop=True)

    @classmethod
    def de_cuadro(cls, datos_pd, corresp, tiempo=None, parcela=None, factor=1, **argsll):
        coords = {
            EJE_PARC: None,
            EJE_DEST: parcela
        }
        return super().de_cuadro(
            datos_pd, corresp=corresp, coords=coords, tiempo=tiempo, parcela=None, factor=factor
        )


class ObsMuerte(ObsRAE):
    var = RES_MRTE


class ObsDepred(ObsRAE):
    var = RES_DEPR

    @classmethod
    def de_cuadro(cls, datos_pd, corresp, tiempo=None, parcela=None, víctima=None, factor=1, **argsll):
        coords = {
            EJE_VÍCTIMA: víctima,
        }
        return super().de_cuadro(
            datos_pd, corresp=corresp, coords=coords, tiempo=tiempo, parcela=parcela, factor=factor
        )
