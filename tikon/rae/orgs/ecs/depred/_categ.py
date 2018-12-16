import numpy as np

from tikon.rae.red_ae.utils import probs_conj
from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from .bed_deang import BedDeAng
from .dep_presa import TipoIDP, TipoIIDP, TipoIIIDP
from .dep_ratio import TipoIDR, TipoIIDR, TipoIIIDR
from .hassel_varley import TipoIHasselVarley, TipoIIHasselVarley, TipoIIIHasselVarley
from .kovai import Kovai


class EcDepred(SubcategEc):
    nombre = 'Ecuación'
    cls_ramas = [
        EcuaciónVacía,
        TipoIDP, TipoIIDP, TipoIIIDP,
        TipoIDR, TipoIIDR, TipoIIIDR,
        TipoIHasselVarley, TipoIIHasselVarley, TipoIIIHasselVarley,
        BedDeAng, Kovai
    ]
    auto = Kovai
    _nombre_res = 'Depredación'
    _eje_cosos = 'etapa'


class EcsDepred(CategEc):
    nombre = 'Depredación'
    cls_ramas = [EcDepred]
    _nombre_res = 'Depredación'
    _eje_cosos = 'etapa'

    def postproc(símismo, paso):
        depred = símismo.obt_res(filtrar=False)

        # Reemplazar valores NaN con 0.
        depred[np.isnan(depred)] = 0

        # Arreglar errores de redondeo en la computación
        depred[depred < 0] = 0

        # Ajustar por superficies
        superficies = símismo.obt_val_control('superficies')
        np.multiply(depred, superficies.reshape((*superficies.shape, *[1] * (len(depred.shape) - 1))), out=depred)

        # Convertir depredación potencial por depredador a depredación potencial total (multiplicar por la población
        # de cada depredador). También multiplicamos por el paso de la simulación. 'depred' ahora está en unidades
        # del número total de presas comidas por cada tipo de depredador por unidad de tiempo.
        pobs = símismo.obt_val_mód('Pobs', filtrar=True)
        np.multiply(depred, np.multiply(pobs, paso)[..., np.newaxis], out=depred)  # para hacer: rabanar mejor

        # Ajustar por la presencia de varios depredadores (eje = depredadores)
        eje_depredador = símismo.í_eje_res('etapa')
        probs_conj(depred, pesos=1, máx=pobs, eje=eje_depredador)

        depred[np.isnan(depred)] = 0

        # Guardar la depredación final
        símismo.poner_val_res(depred)

        # Depredación únicamente por presa (todos los depredadores juntos)
        depred_por_presa = np.sum(depred, axis=eje_depredador)

        # Actualizar la matriz de poblaciones
        símismo.poner_val_mód('Pobs', -depred_por_presa, rel=True, filtrar=False)
