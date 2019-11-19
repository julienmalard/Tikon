import xarray as xr
from tikon.móds.manejo.acciones import Acción

from .trampa import Trampas


class Aplicar(Acción):
    def __init__(símismo, producto, conc):
        símismo.producto = producto
        símismo.conc = conc

    def __call__(símismo, sim, donde):
        cambio = xr.where(donde, símismo.conc, 0).expand_dims(dim={EJE_PRODUCTO: símismo.producto})
        sim[Trampas.nombre].poner_valor(var=RES_CONC, val=cambio, rel=True)
