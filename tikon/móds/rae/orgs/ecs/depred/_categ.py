import numpy as np
from frozendict import frozendict

from tikon.datos.datos import mínimo
from tikon.ecs.árb_mód import EcuaciónVacía
from tikon.móds.rae.orgs.ecs._plntll import CategEcOrg, SubcategEcOrg
from tikon.móds.rae.orgs.ecs.utils import ECS_DEPR, probs_conj
from tikon.móds.rae.utils import RES_DEPR, EJE_ETAPA, RES_COHORTES, EJE_VÍCTIMA, RES_POBS

from .bed_deang import BedDeAng
from .dep_presa import TipoIDP, TipoIIDP, TipoIIIDP
from .dep_ratio import TipoIDR, TipoIIDR, TipoIIIDR
from .hassel_varley import TipoIHasselVarley, TipoIIHasselVarley, TipoIIIHasselVarley
from .kovai import Kovai


class EcDepred(SubcategEcOrg):
    nombre = 'Ecuación'
    cls_ramas = [
        Kovai, EcuaciónVacía,
        TipoIDP, TipoIIDP, TipoIIIDP,
        TipoIDR, TipoIIDR, TipoIIIDR,
        TipoIHasselVarley, TipoIIHasselVarley, TipoIIIHasselVarley,
        BedDeAng
    ]
    _nombre_res = RES_DEPR


class EcsDepred(CategEcOrg):
    nombre = ECS_DEPR
    cls_ramas = [EcDepred]
    _nombre_res = RES_DEPR

    def postproc(símismo, paso, sim):
        cohortes = sim[RES_COHORTES]

        depred = símismo.obt_valor_res(sim)

        # Reemplazar valores NaN con 0.
        depred.llenar_nan(0)

        # Arreglar errores de redondeo (negativos) en la computación
        depred.donde(depred < 0, 0)

        # Convertir depredación potencial por depredador a depredación potencial total (multiplicar por la población
        # de cada depredador). También multiplicamos por el paso de la simulación. 'depred' ahora está en unidades
        # del número total de presas comidas por cada tipo de depredador por unidad de tiempo.
        depred = depred * símismo.pobs(sim) * paso

        # Ajustar por la presencia de varios depredadores (eje = depredadores)
        máx = símismo.pobs(sim, filtrar=depred.coords[EJE_VÍCTIMA]).renombrar({EJE_ETAPA: EJE_VÍCTIMA})
        depred = mínimo(depred, máx)
        depred = probs_conj(depred, pesos=1, máx=máx, dim=EJE_ETAPA)

        depred.fi(np.floor).llenar_nan(0)

        # Guardar la depredación final
        símismo.poner_valor_res(sim, depred)

        # Depredación únicamente por presa (todos los depredadores juntos)
        depred_por_presa = depred.suma(dim=EJE_ETAPA).renombrar({EJE_VÍCTIMA: EJE_ETAPA})

        # Actualizar la matriz de poblaciones
        sim[RES_POBS].poner_valor(-depred_por_presa, rel=True)

        # Dividir las depredaciones entre las de depredación normal y las de parasitismo
        depr_parás = depred.donde(sim.máscara_parás, 0)
        depr_sin_parás = depred.donde(~sim.máscara_parás, 0)

        # Para las depredaciones normales, es fácil quitarlas de los cohortes
        cohortes.quitar(depr_sin_parás.suma(dim=EJE_ETAPA).renombrar({EJE_VÍCTIMA: EJE_ETAPA}))

        # Para cada parasitoide...
        for parás, (l_hués, l_fants) in sim.parás_hués:
            pob_parasitada = depr_parás.loc[
                frozendict({EJE_ETAPA: parás, EJE_VÍCTIMA: l_hués})
            ].dejar(EJE_ETAPA).renombrar({EJE_VÍCTIMA: EJE_ETAPA})

            cohortes.quitar(pob_parasitada, recips=l_fants)
            pob_parasitada.asiñar_coords(EJE_ETAPA, l_fants)
            sim[RES_POBS].poner_valor(pob_parasitada, rel=True)
