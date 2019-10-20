import numpy as np

from tikon.ecs.árb_mód import CategEc, SubcategEc, EcuaciónVacía
from tikon.móds.rae import probs_conj
from tikon.móds.rae.orgs.utils import DEPR

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
    _nombre_res = DEPR
    _eje_cosos = ETAPA


class EcsDepred(CategEc):
    nombre = DEPR
    cls_ramas = [EcDepred]
    _nombre_res = DEPR
    _eje_cosos = ETAPA

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
        pobs = símismo.obt_val_mód(POBS, filtrar=True)
        np.multiply(depred, np.multiply(pobs, paso)[..., np.newaxis], out=depred)  # para hacer: rebanar mejor

        # Ajustar por la presencia de varios depredadores (eje = depredadores)
        eje_depredador = símismo.í_eje_res(ETAPA)
        probs_conj(depred, pesos=1, máx=símismo.obt_val_mód(POBS, filtrar=False), eje=eje_depredador)

        depred[np.isnan(depred)] = 0
        depred = np.floor(depred)

        # Guardar la depredación final
        símismo.poner_val_res(depred)

        # Depredación únicamente por presa (todos los depredadores juntos)
        depred_por_presa = np.sum(depred, axis=eje_depredador)

        # Actualizar la matriz de poblaciones
        símismo.poner_val_mód(POBS, -depred_por_presa, rel=True, filtrar=False)

        # Dividir las depredaciones entre las de depredación normal y las de parasitismo
        depr_parás = np.where(símismo._máscara_parás(), depred, 0)
        depr_sin_parás = np.where(~símismo._máscara_parás(), depred, 0)

        # Para las depredaciones normales, es fácil quitarlas de los cohortes
        símismo.sim.cohortes.quitar(np.sum(depr_sin_parás, axis=eje_depredador))

        pobs = símismo.sim.obt_res(POBS)
        # Para cada parasitoide...
        for prs, l_hués in símismo._prs_hués():
            í_prs = símismo.cosos.index(prs)
            for hués in l_hués:
                í_hués = símismo.sim.info_etps.índice(hués)
                etp_fant = símismo.sim.info_etps.etp_fant(hués, prs.org)
                pob_parasitada = depr_parás[..., í_prs, [í_hués]]  # para hacer: rebanar mejor

                símismo.sim.cohortes.quitar(pob_parasitada, etapas=[hués], recips=([etp_fant], [hués]))

                # Agregar las adiciones a las etapas fantasmas a la matriz de poblaciones general
                pobs.poner_valor(pob_parasitada, rel=True, índs={símismo._eje_cosos: [etp_fant]})

    def _máscara_parás(símismo):
        # Índices para luego poder encontrar las interacciones entre parasitoides y víctimas en las matrices de
        # depredación

        máscara = np.zeros((len(símismo.cosos), len(símismo.sim.info_etps)))  # para hacer: más elegante
        prs_hués = símismo._prs_hués()
        l_índs = [
            (símismo.cosos.index(prs), símismo.sim.info_etps.índice(hués))
            for prs, l_hués in prs_hués for hués in l_hués
        ]
        máscara[list(zip(*l_índs))] = 1
        return máscara.astype(bool)

    def _prs_hués(símismo):
        return [
            (etp, símismo.sim.info_etps.huéspedes(etp)) for etp in símismo.cosos if símismo.sim.info_etps.huéspedes(etp)
        ]  # para hacer: más elegante
