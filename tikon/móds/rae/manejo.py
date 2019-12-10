from tikon.datos.datos import donde as donde_, Datos
from tikon.móds.manejo.acciones import Acción
from tikon.móds.manejo.conds import CondVariable
from tikon.móds.rae.utils import RES_POBS, EJE_ETAPA
from .orgs.organismo import Etapa, SumaEtapas, Organismo
from .red import RedAE


class CondPoblación(CondVariable):
    def __init__(símismo, etapas, prueba, func=Datos.suma, espera=14):
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
        cambio = donde_(donde, símismo.valor, 0)
        if isinstance(cambio, Datos):
            cambio = cambio.expandir_dims(coords={EJE_ETAPA: símismo.etapa})
        else:
            cambio = Datos(cambio.item(), coords={EJE_ETAPA: [símismo.etapa]}, dims=[EJE_ETAPA])
        sim[RedAE.nombre].poner_valor(var=RES_POBS, val=cambio, rel=True)


class PonerPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def __call__(símismo, sim, donde):
        nuevas = donde_(donde, símismo.valor, 0).expandir_dims(dim={EJE_ETAPA: símismo.etapa})
        sim[RedAE.nombre].poner_valor(var=RES_POBS, val=nuevas)


class MultPob(Acción):
    def __init__(símismo, etapa, valor):
        símismo.etapa = etapa
        símismo.valor = valor

    def __call__(símismo, sim, donde):
        pobs = sim[RedAE.nombre].obt_valor(var=RES_POBS).loc[{EJE_ETAPA: símismo.etapa}]
        nuevas = donde_(donde, símismo.valor * pobs, 0)
        sim[RedAE.nombre].poner_valor(var=RES_POBS, val=nuevas)
