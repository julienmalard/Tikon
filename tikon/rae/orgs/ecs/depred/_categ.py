import numpy as np

from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.rae.red_ae.utils import probs_conj
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
        np.multiply(depred, np.multiply(pobs, paso)[..., np.newaxis], out=depred)  # para hacer: rebanar mejor

        # Ajustar por la presencia de varios depredadores (eje = depredadores)
        eje_depredador = símismo.í_eje_res('etapa')
        probs_conj(depred, pesos=1, máx=símismo.obt_val_mód('Pobs', filtrar=False), eje=eje_depredador)

        depred[np.isnan(depred)] = 0

        # Guardar la depredación final
        símismo.poner_val_res(depred)

        # Depredación únicamente por presa (todos los depredadores juntos)
        depred_por_presa = np.sum(depred, axis=eje_depredador)

        # Actualizar la matriz de poblaciones
        símismo.poner_val_mód('Pobs', -depred_por_presa, rel=True, filtrar=False)

        # para hacer
        # Dividir las depredaciones entre las de depredación normal y las de parasitismo
        depred_parás = np.zeros_like(depred)
        return
        índs_parás, índs_víc = símismo.parasitoides['índices']
        depred_parás[..., índs_parás, índs_víc] = depred[..., índs_parás, índs_víc]
        depred_por_presa_sin_parás = np.subtract(depred_por_presa, np.sum(depred_parás, axis=eje_depredador))

        # Para las depredaciones normales, es fácil quitarlas de los cohortes
        símismo.mód.cohortes.quitar(depred_por_presa_sin_parás, etapas=símismo.cosos)

        # Para cada parasitoide...
        for n_parás, d_parás in símismo.parasitoides['adultos'].items():
            índ_entra = d_parás['n_entra']
            índ_recip = d_parás['n_fants'][:len(índ_entra)]
            símismo.mód.cohortes.quitar(etapas=índ_entra, recips=índ_recip)
            símismo._quitar_de_cohortes(
                muertes=depred_parás[..., n_parás, símismo.índices_cohortes], í_don=índ_entra, í_recip=índ_recip)

            # Agregar las adiciones a las etapas fantasmas a la matriz de poblaciones general
            símismo.mód.agregar_pobs()
            pobs[..., índ_recip] += depred_parás[..., n_parás, índ_entra]
