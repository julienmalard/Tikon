import xarray as xr
from tikon.móds.manejo.acciones import Acción

from .mód import Trampas
from .utils import EJE_TRAMPA, RES_DENS


class PonerTrampa(Acción):
    def __init__(símismo, trampa, dens):
        símismo.trampa = trampa
        símismo.dens = dens

    def __call__(símismo, sim, donde):
        cambio = xr.where(donde, símismo.dens, 0).expand_dims(dim={EJE_TRAMPA: símismo.trampa})
        sim[Trampas.nombre].poner_valor(var=RES_DENS, val=cambio, rel=True)
