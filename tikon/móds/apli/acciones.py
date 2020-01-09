import xarray as xr
from tikon.móds.manejo.acciones import Acción

from .apli import Aplicaciones
from .utils import EJE_PRODUCTO, RES_CONC


class Aplicar(Acción):
    def __init__(símismo, producto, conc):
        símismo.producto = producto
        símismo.conc = conc

    def __call__(símismo, sim, donde):
        cambio = xr.where(donde, símismo.conc, 0).expand_dims(dim={EJE_PRODUCTO: símismo.producto})
        sim[Aplicaciones.nombre].poner_valor(var=RES_CONC, val=cambio, rel=True)
