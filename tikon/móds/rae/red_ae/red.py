import os

import numpy as np
from tikon.ecs.paráms import Inter
from tikon.estruc.módulo import Módulo
from tikon.estruc.simul import SimulMódulo
from tikon.móds.rae.orgs.utils import POBS, COHORT
from tikon.result.coords import Coord, coords_base

from .. import Organismo
from ..orgs.ecs import EcsOrgs
from ..orgs.organismo import EtapaFantasma
from ..red_ae import res as res_red


class RedAE(Módulo):
    nombre = 'red'

    def __init__(símismo, orgs=None):
        super().__init__()

        orgs = orgs or []
        if isinstance(orgs, Organismo):
            orgs = [orgs]

        símismo._orgs = {str(o_): o_ for o_ in orgs}

    def añadir_org(símismo, org):
        símismo._orgs[str(org)] = org

    def quitar_org(símismo, org):
        try:
            símismo._orgs.pop(str(org))
        except KeyError:
            raise KeyError('El organismo "{org}" no existía en esta red.'.format(org=org))

    def espec_aprioris(símismo, a_prioris):
        for org, l_org in a_prioris.items():
            try:
                obj_org = símismo[org] if isinstance(org, str) else org
            except KeyError:
                continue

            for d_apr in l_org:
                if d_apr[ETAPA] in obj_org:
                    obj_org.espec_apriori_etp(**d_apr)

    def gen_simul(símismo, simul_exper):
        return SimulRed(
            simul_exper=simul_exper,
            etapas=[etp for org in símismo for etp in símismo[org].etapas()],
        )

    def gen_resultados(símismo, n_rep_estoc, n_rep_parám, vars_interés):


        obs = símismo.mnjdr_móds.exper.obtener_obs(símismo)
        inic_pobs = símismo.mnjdr_móds.exper.obt_inic(símismo, POBS)

        # para hacer: generalizar para todos módulos
        if vars_interés is None:
            temporales = [vr for vr in coords if vr in obs]
        elif vars_interés is True:
            temporales = list(coords)
        else:
            temporales = vars_interés

        return CorridaRed([
            (cls_res[nmb] if nmb in cls_res else ResultadoRed)(
                nmb, dims_base + crd,
                tiempo=símismo.tiempo if nmb in temporales else None,
                obs=obs[nmb] if nmb in obs else None,
                inic=inic_pobs if nmb == POBS else None,  # para hacer: ¿más elegante?
            ) for nmb, crd in coords.items()
        ])

    def guardar_calib(símismo, directorio=''):
        for org in símismo:
            org.guardar_calib(directorio)

    def __getitem__(símismo, itema):
        return símismo._orgs[str(itema)]

    def __iter__(símismo):
        for org in símismo._orgs:
            yield org

    def cargar_calib(símismo, directorio=''):
        # para hacer: genérico
        if os.path.split(directorio)[1] != 'red':
            directorio = os.path.join(directorio, 'red')

        for org in símismo:
            org.cargar_calib(directorio)


class InfoEtapas(object):
    def __init__(símismo, orgs):
        símismo._orgs = list(orgs.values()) if isinstance(orgs, dict) else orgs
        símismo.etapas = [etp for org in símismo._orgs for etp in org.etapas(fantasmas=True)]

    def índice(símismo, etp):
        return símismo.etapas.index(etp)

    def etp_fant(símismo, huésped, parasitoide):
        return next(
            etp for etp in símismo.etapas if
            isinstance(etp, EtapaFantasma) and etp.etp_hués == huésped and etp.org == parasitoide
        )

    def __iter__(símismo):
        for etp in símismo.etapas:
            yield etp

    def __contains__(símismo, itema):
        return itema in símismo.etapas

    def __len__(símismo):
        return len(símismo.etapas)


class SimulRed(SimulMódulo):
    def __init__(símismo, simul_exper, etapas, vars_interés):

        símismo.etapas = etapas
        símismo.ecs = EcsOrgs(cosos=etapas, sim=símismo, n_rep=simul_exper.reps['paráms'])
        símismo.etps_repr = [
            etp.org[0] for etp in símismo.etapas if etp.categ_activa(REPR, símismo)
        ]
        parcelas = simul_exper.exper.controles['parcelas']

        base = coords_base(parcelas=parcelas)
        cosos = símismo.ecs.cosos_en_categ
        l_res = [
            res_red.ResPobs(coords={ETAPA: etapas, **base}),
            res_red.ResEdad(coords={ETAPA: cosos(res_red.ResEdad), **base}),
            res_red.ResCrec(coords={ETAPA: cosos(res_red.ResCrec), **base}),
            res_red.ResDepred(coords={ETAPA: cosos(res_red.ResDepred), 'víctima': víctimas, **base}),
            res_red.ResRepr(coords={ETAPA: cosos(res_red.ResRepr), **base}),
            res_red.ResMuerte(coords={ETAPA: cosos(res_red.ResMuerte), **base}),
            res_red.ResTrans(coords={ETAPA: cosos(res_red.ResTrans), **base}),
            res_red.ResMov(coords={'dest': parcelas, ETAPA: cosos(res_red.ResMov), **base}),
            res_red.ResEstoc(coords={ETAPA: cosos(res_red.ResEstoc), **base}),
            res_red.ResCohortes(coords={ETAPA: cosos(res_red.ResCohortes), **base})
        ]
        super().__init__(resultados=l_res, simul_exper=simul_exper)

    def inter(símismo, coso, tipo):
        if isinstance(tipo, str):
            tipo = [tipo]

        etps = símismo.etapas

        etps_inter = set()
        for tp in tipo:
            if tp == 'presa':
                etps_inter.update(símismo.presas(coso))
            elif tp == 'huésped':
                etps_inter.update(símismo.huéspedes(coso))
            else:
                raise ValueError(tipo)
        índs = {etps.índice(etp): [etp.org, etp] for etp in etps_inter}
        if len(índs):
            return Inter(tmñ=len(etps), índices=índs)

    def presas(símismo, etp):
        presas = [pr for pr in etp.presas() if pr in símismo]
        fantasmas = [etp for etp in símismo.etapas if isinstance(etp, EtapaFantasma) and etp.etp_hués in presas]
        return presas + fantasmas

    def huéspedes(símismo, etp):
        return [pr for pr in etp.huéspedes() if pr in símismo.etapas]

    # para hacer: limpiar y reorganizar estos

    def etps_trans(símismo):
        etps_trans = [etp for etp in símismo.info_etps if etp.categ_activa(TRANS, símismo)]
        siguientes = [etp.siguiente() for etp in etps_trans]
        return [(etp, sig) for etp, sig in zip(etps_trans, siguientes) if sig]

    def iniciar_vals(símismo):
        super().iniciar_vals()

        símismo[COHORT].agregar(símismo[POBS].valores())

    def incrementar(símismo, paso):
        símismo.ecs.eval(paso=paso)
        super().incrementar(paso)

    def cerrar(símismo):
        pass

    def poner_valor(símismo, var, val, rel=False):
        if var == POBS:
            cambio = val if rel else val - símismo[POBS].datos
            símismo[COHORT].ajustar(cambio)
        else:
            raise ValueError('No se puede cambiar el valor de "{}" durante una simulación.'.format(var))

        super().poner_valor(var, val, rel)

    def obt_valor(símismo, var):
        if var == 'Dens':
            pobs = super().obt_valor(POBS)
            superficies = símismo.simul_exper.exper.controles('superficies')
            return pobs / superficies

        return super().obt_valor(var)

    def verificar_estado(símismo):
        mnsg = '\tSi acabas de agregar nuevas ecuaciones, es probablemente culpa tuya.\n\tSino, es culpa mía.'
        pobs = símismo[POBS].valores()
        if pobs.min() < 0:
            raise ValueError('Población inferior a 0.\n{}'.format(mnsg))
        if np.any(np.isnan(pobs)):
            raise ValueError('Población no numérica (p. ej., división por 0).\n{}'.format(mnsg))
        if np.any(np.not_equal(pobs.astype(int), pobs)):
            raise ValueError('Población fraccional.'.format(mnsg))

        super().verificar_estado()

        # para hacer: incorporar cohortes como resultados e incluir las pruebas siguientes
        """
        if len(símismo.predics[COHORT]):
            pobs_coh = símismo.predics[COHORT][POBS]
            if pobs_coh.min() < 0:
                raise ValueError('Población de cohorte inferior a 0 justo después de calcular {}.\n{}'
                                 .format(punto, mnsg))
            if np.any(np.not_equal(pobs_coh.astype(int), pobs_coh)):
                raise ValueError('Población de cohorte fraccional justo después de calcular {}.\n{}'
                                 .format(punto, mnsg))
            if np.any(np.isnan(pobs_coh)):
                raise ValueError('Población de cohorte "nan" justo después de calcular {}.\n{}'.format(punto, mnsg))
            if np.any(np.not_equal(pobs_coh.sum(axis=0), pobs[..., símismo.índices_cohortes])):
                raise ValueError('Población de cohorte no suma a población total justo después de calcular {}.'
                                 .format(punto))
        """
