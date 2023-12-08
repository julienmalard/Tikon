from typing import Iterable

import numpy as np
from frozendict import frozendict

from tikon.central.matriz import Datos
from tikon.central.módulo import Módulo
from tikon.central.simul import SimulMódulo
from tikon.consts import CORREO_AUTOR
from tikon.ecs.paráms import Inter
from tikon.móds.rae.utils import (
    RES_POBS,
    RES_COHORTES,
    EJE_COH,
    EJE_ETAPA,
    EJE_VÍCTIMA,
    contexto,
)
from .res.cohortes import ResCohortes
from ..orgs.ecs import EcsOrgs
from ..orgs.ecs.utils import ECS_TRANS, ECS_REPR
from ..orgs.etapa import Etapa, EtapaFantasma
from ..orgs.insectos import Parasitoide
from ..orgs.insectos.paras import EtapaJuvenilParasitoide
from ..orgs.organismo import Organismo
from ..red.res import res as res_red


class ErrorParasitismoCircular(ValueError):
    pass


class SimulRed(SimulMódulo):
    resultados = [
        res_red.ResPobs,
        res_red.ResEdad,
        res_red.ResCrec,
        res_red.ResDepred,
        res_red.ResRepr,
        res_red.ResMuerte,
        res_red.ResTrans,
        res_red.ResMov,
        res_red.ResEstoc,
        ResCohortes,
    ]

    def __init__(símismo, mód: "RedAE", simul_exper, ecs, vars_interés):

        símismo.etapas = mód.etapas
        símismo.orgs = mód.organismos
        presas = mód.presas()
        símismo.víctimas = presas.union({h for h in mód.huéspedes() if h not in presas})

        modelo = simul_exper.modelo
        exper = simul_exper.exper
        símismo.recip_repr = tuple(
            [
                id(etp.org[0])
                for etp in símismo.etapas
                if etp.categ_activa(ECS_REPR, modelo, mód=mód, exper=exper)
            ]
        )

        símismo.recip_trans = tuple(
            [
                (id(etp), id(etp.siguiente()))
                for etp in símismo.etapas
                if etp.categ_activa(ECS_TRANS, modelo, mód=mód, exper=exper)
                   and etp.siguiente()
            ]
        )

        símismo.parás_hués = []
        for etp in símismo.etapas:
            if isinstance(etp.org, Parasitoide) and etp.nombre == "adulto":
                huéspedes = list(mód.huéspedes(etp))
                fantasmas = sorted(
                    mód.fantasmas(huéspedes, paras=etp),
                    key=lambda x: huéspedes.index(x.etp_hués),
                )
                símismo.parás_hués.append(
                    (
                        id(etp),
                        (
                            tuple(id(h) for h in huéspedes),
                            tuple(id(f) for f in fantasmas),
                        ),
                    )
                )

        # Índices para luego poder encontrar las interacciones entre parasitoides y víctimas en las matrices de
        # depredación
        depredadores = tuple(
            id(etp) for etp in símismo.etapas if mód.presas(etp) or mód.huéspedes(etp)
        )
        símismo.máscara_parás = Datos(
            False,
            dims=[EJE_ETAPA, EJE_VÍCTIMA],
            coords=frozendict(
                {
                    EJE_ETAPA: depredadores,
                    EJE_VÍCTIMA: tuple(id(v) for v in símismo.víctimas),
                }
            ),
        )
        for paras, hués_fants in símismo.parás_hués:
            símismo.máscara_parás.loc[
                frozendict({EJE_ETAPA: paras, EJE_VÍCTIMA: hués_fants[0]})
            ] = True

        super().__init__(
            mód, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés
        )

    def poner_valor(símismo, var, val, rel=False):
        if var == RES_POBS:
            cambio = val if rel else val - símismo[RES_POBS].datos
            símismo[RES_COHORTES].ajustar(cambio)

        super().poner_valor(
            var, val, rel
        )  # **Debe** venir después de ajustar cohortes sino `rel` no funciona

    def verificar_estado(símismo):
        super().verificar_estado()

        mnsg = (
            "\tSi acabas de agregar nuevas ecuaciones, es probablemente culpa tuya."
            f"\n\tSino, es culpa mía, avísame al {CORREO_AUTOR}."
        )
        pobs = símismo[RES_POBS].datos

        if símismo[RES_COHORTES].activa:
            pobs_coh = símismo[RES_COHORTES].datos[{"comp": 0}]
            if ~np.array_equal(pobs_coh.matr, np.round(pobs_coh.matr)):
                raise ValueError(
                    f"Población de cohorte fraccional.\n{mnsg}"
                )
            pobs_corresp_coh = pobs.loc[
                frozendict({EJE_ETAPA: pobs_coh.coords_internas[EJE_ETAPA]})
            ]
            if ~np.array_equal(pobs_coh.suma(dim=EJE_COH).matr, pobs_corresp_coh.matr):
                raise ValueError(
                    f"Población de cohorte no suma a población total.\n{mnsg}"
                )


class RedAE(Módulo):
    nombre = "red"
    cls_simul = SimulRed
    eje_coso = EJE_ETAPA

    def __init__(símismo, orgs: Iterable[Organismo] = None):
        super().__init__(cosos=orgs)
        símismo.relaciones = {"presa": [], "paras": []}

    @property
    def etapas(símismo):
        para_resolver = [etp for org in símismo for etp in símismo[org].etapas]
        etapas = []


        while len(para_resolver):
            resolvables = []  # Para hacer

            if not resolvables:
                raise ErrorParasitismoCircular
            resueltas = []  # Para hacer
            etapas += resueltas

        return etapas

        etps_fant = [
            fnt for r_p in símismo.relaciones["paras"] for fnt in r_p.fantasmas
        ]
        return [etp for org in símismo for etp in símismo[org].etapas] + etps_fant

    @property
    def organismos(símismo):
        return [símismo[org] for org in símismo]

    def agregar_relación(símismo, relación):
        for org in relación.organismos:
            if org not in símismo.organismos:
                raise ValueError(
                    f'Organismo "{org}" no existe en red "{símismo}".'
                )
        símismo.relaciones[relación.tipo].append(relación)

    def inter(símismo, modelo, coso, tipo: str):
        if isinstance(tipo, str):
            tipo = [tipo]

        etps_inter = set()
        coords = set()
        for tp in tipo:
            if tp == "presa":
                etps_inter.update(símismo.presas(coso))
                coords.update(símismo.presas())
            elif tp == "huésped":
                etps_inter.update(símismo.huéspedes(coso))
                coords.update(símismo.huéspedes())
            else:
                raise ValueError(tipo)
        if len(etps_inter):
            return Inter(etps_inter, eje=EJE_VÍCTIMA, coords=coords)

    def presas(símismo, depred=None, presa=None):
        presa = símismo._resolver_etapas(presa)
        depred = símismo._resolver_etapas(depred)
        presas = {
            rel.etp_presa
            for rel in símismo.relaciones["presa"]
            if rel.etp_presa in presa and rel.etp_depred in depred
        }

        # Incluir los fantasmas de las presas
        fants_presas = {
            etp
            for etp in símismo.etapas
            if isinstance(etp, EtapaFantasma) and etp.etp_hués in presas
        }

        return presas.union(fants_presas)

    def huéspedes(símismo, paras=None, hués=None):
        """Huéspedes que pueden ser infectados directamente por parasitoide `paras`."""
        paras = símismo._resolver_etapas(paras)
        hués = símismo._resolver_etapas(hués)
        etps = {
            hsp
            for rel in símismo.relaciones["paras"]
            if rel.etp_depred in paras
            for hsp in rel.etps_entra
            if hsp in hués
        }

        for etp in set(etps):
            if isinstance(etp, EtapaJuvenilParasitoide):
                etps.remove(etp)
                etps.update(símismo.fantasmas(paras=etp.org))

        return etps

    def fantasmas(símismo, hués=None, paras=None):
        hués = símismo._resolver_etapas(hués)
        paras = [
            prs
            for prs in símismo._resolver_etapas(paras)
            if isinstance(prs.org, Parasitoide) and prs.nombre == "adulto"
        ]
        return [
            fnt
            for rel in símismo.relaciones["paras"]
            if rel.etp_depred in paras
            for fnt in rel.fantasmas
            if fnt.etp_hués in hués
        ]

    def gen_ecs(símismo, modelo, mód, exper, n_reps):
        return EcsOrgs(modelo, mód, exper, cosos=símismo.etapas, n_reps=n_reps)

    def _resolver_etapas(símismo, etps):
        if etps is None:
            return símismo.etapas
        elif isinstance(etps, (Etapa, Organismo)):
            etps = [etps]
        etps = [etp for x in etps for etp in ([x] if isinstance(x, Etapa) else x)]
        return [etp for etp in etps if etp in símismo.etapas]

    def __enter__(símismo):
        if símismo not in contexto:
            contexto.append(símismo)
        return símismo

    def __exit__(símismo, tipo_sld, val_sld, trz_sld):
        if símismo in contexto:
            contexto.remove(símismo)
