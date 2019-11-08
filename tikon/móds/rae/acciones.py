import xarray as xr
from tikon.móds.manejo.acciones import Acción

from .red import RedAE
from .red.utils import RES_POBS, EJE_ETAPA


class AgregarPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def __call__(símismo, sim, donde):
        cambio = xr.where(donde, símismo.valor, 0).expand_dims(dim={EJE_ETAPA: símismo.etapa})
        sim[RedAE.nombre].poner_valor(var=RES_POBS, val=cambio, rel=True)


class PonerPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def __call__(símismo, sim, donde):
        nuevas = xr.where(donde, símismo.valor, 0).expand_dims(dim={EJE_ETAPA: símismo.etapa})
        sim[RedAE.nombre].poner_valor(var=RES_POBS, val=nuevas)


class MultPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def __call__(símismo, sim, donde):
        pobs = sim[RedAE.nombre].obt_valor(var=RES_POBS).loc[{EJE_ETAPA: símismo.etapa}]
        nuevas = xr.where(donde, símismo.valor * pobs, 0)
        sim[RedAE.nombre].poner_valor(var=RES_POBS, val=nuevas)
