import xarray as xr
from tikon.móds.manejo.acciones import Acción
from tikon.móds.manejo.conds import CondVariable

from .orgs.organismo import Etapa, SumaEtapas, Organismo
from .red import RedAE
from tikon.móds.rae.utils import RES_POBS, EJE_ETAPA


class CondPoblación(CondVariable):
    def __init__(símismo, etapas, prueba, func=xr.DataArray.sum, espera=14):
        etapas = [etapas] if isinstance(etapas, (Etapa, SumaEtapas, Organismo)) else etapas
        etapas_final = []
        for etp in etapas:
            if isinstance(etp, Etapa):
                etapas_final.append(etp)
            else:
                etapas_final += [e for e in etp]

        super().__init__(
            mód=RedAE.nombre, var=RES_POBS, prueba=prueba, espera=espera, func=func, coords={EJE_ETAPA: etapas}
        )


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
