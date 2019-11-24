from tikon.móds.rae.utils import EJE_ETAPA, EJE_VÍCTIMA, RES_POBS, RES_CREC, RES_DEPR, RES_MOV, RES_MRTE, RES_REPR, \
    RES_TRANS
from tikon.result import Obs
from tikon.utils import EJE_PARC, EJE_DEST
from .red import RedAE


class ObsRAE(Obs):
    mód = RedAE.nombre

    @classmethod
    def de_pandas(cls, datos_pd, corresp, coords=None, tiempo=None, parc=None, factor=1, **argsll):
        return super().de_pandas(
            datos_pd, corresp=corresp, eje_principal=EJE_ETAPA, parc=parc, tiempo=tiempo, coords=coords, factor=factor
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
    def de_pandas(cls, datos_pd, corresp, tiempo=None, parc=None, dest=None, factor=1, **argsll):
        coords = {
            EJE_DEST: dest or EJE_DEST,
        }
        return super().de_pandas(
            datos_pd, corresp=corresp, coords=coords, tiempo=tiempo, parc=parc, factor=factor
        )


class ObsEmigr(ObsTrans):

    def proc_res(símismo, res):
        return res.sum(dim=EJE_DEST).squeeze(EJE_DEST)


class ObsImigr(ObsTrans):

    def proc_res(símismo, res):
        return res.sum(dim=EJE_PARC).squeeze(EJE_PARC)

    @classmethod
    def de_pandas(cls, datos_pd, corresp, tiempo=None, parc=None, factor=1, **argsll):
        coords = {
            EJE_PARC: None,
            EJE_DEST: parc
        }
        return super().de_pandas(
            datos_pd, corresp=corresp, coords=coords, tiempo=tiempo, parc=None, factor=factor
        )


class ObsMuerte(ObsRAE):
    var = RES_MRTE


class ObsDepred(ObsRAE):
    var = RES_DEPR

    @classmethod
    def de_pandas(cls, datos_pd, corresp, tiempo=None, parc=None, víctima=None, factor=1, **argsll):
        coords = {
            EJE_VÍCTIMA: víctima,
        }
        return super().de_pandas(
            datos_pd, corresp=corresp, coords=coords, tiempo=tiempo, parc=parc, factor=factor
        )
