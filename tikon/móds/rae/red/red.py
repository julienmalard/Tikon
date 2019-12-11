import numpy as np

from tikon.central.módulo import Módulo
from tikon.central.simul import SimulMódulo
from tikon.datos.datos import Datos
from tikon.ecs.paráms import Inter
from tikon.móds.rae.utils import RES_POBS, RES_COHORTES, EJE_COH, EJE_ETAPA, EJE_VÍCTIMA
from .res.cohortes import ResCohortes
from ..orgs.ecs import EcsOrgs
from ..orgs.ecs.utils import ECS_TRANS, ECS_REPR
from ..orgs.insectos import Parasitoide
from ..orgs.organismo import EtapaFantasma, Etapa
from ..red.res import res as res_red


class SimulRed(SimulMódulo):
    resultados = [
        res_red.ResPobs, res_red.ResEdad, res_red.ResCrec, res_red.ResDepred, res_red.ResRepr,
        res_red.ResMuerte, res_red.ResTrans, res_red.ResMov, res_red.ResEstoc, ResCohortes
    ]

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):

        símismo.etapas = mód.etapas
        símismo.orgs = mód.orgs
        presas = mód.presas()
        símismo.víctimas = presas + [h for h in mód.huéspedes() if h not in presas]

        modelo = simul_exper.modelo
        exper = simul_exper.exper
        símismo.recip_repr = [
            etp.org[0] for etp in símismo.etapas if etp.categ_activa(ECS_REPR, modelo, mód=mód, exper=exper)
        ]

        símismo.recip_trans = [
            (etp, etp.siguiente()) for etp in símismo.etapas
            if etp.categ_activa(ECS_TRANS, modelo, mód=mód, exper=exper) and etp.siguiente()
        ]

        símismo.parás_hués = [
            (etp, ([etp.etp_hués for etp in mód.fantasmas(etp)], mód.fantasmas(etp))) for etp in símismo.etapas
            if isinstance(etp.org, Parasitoide) and etp.nombre == 'adulto' and mód.huéspedes(etp)
        ]

        # Índices para luego poder encontrar las interacciones entre parasitoides y víctimas en las matrices de
        # depredación
        depredadores = [
            etp for etp in símismo.etapas if any(pr in símismo.etapas for pr in etp.presas() + etp.huéspedes())
        ]
        símismo.máscara_parás = Datos(
            False, coords={
                EJE_ETAPA: depredadores, EJE_VÍCTIMA: símismo.víctimas
            }, dims=[EJE_ETAPA, EJE_VÍCTIMA]
        )
        for parás, hués_fants in símismo.parás_hués:
            símismo.máscara_parás.loc[{EJE_ETAPA: parás, EJE_VÍCTIMA: hués_fants[0]}] = True

        super().__init__(mód, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)

    def poner_valor(símismo, var, val, rel=False):
        if var == RES_POBS:
            cambio = val if rel else val - símismo[RES_POBS].datos
            símismo[RES_COHORTES].ajustar(cambio)

        super().poner_valor(var, val, rel)  # **Debe** venir después de ajustar cohortes sino `rel` no funciona

    def verificar_estado(símismo):
        super().verificar_estado()

        mnsg = '\tSi acabas de agregar nuevas ecuaciones, es probablemente culpa tuya.\n\tSino, es culpa mía.'
        pobs = símismo[RES_POBS].datos

        if símismo[RES_COHORTES].activa:
            pobs_coh = símismo[RES_COHORTES].datos[{'comp': 0}]
            if np.any(~np.equal(pobs_coh.matr, np.round(pobs_coh.matr))):
                raise ValueError('Población de cohorte fraccional.\n{mnsg}'.format(mnsg=mnsg))
            pobs_corresp_coh = pobs.loc[{EJE_ETAPA: pobs_coh.coords[EJE_ETAPA]}]
            if np.any(np.not_equal(pobs_coh.suma(dim=EJE_COH).matr, pobs_corresp_coh.matr)):
                raise ValueError('Población de cohorte no suma a población total.\n{mnsg}'.format(mnsg=mnsg))


class RedAE(Módulo):
    nombre = 'red'
    cls_simul = SimulRed
    eje_coso = EJE_ETAPA

    def __init__(símismo, orgs=None):
        super().__init__(cosos=orgs)

    @property
    def etapas(símismo):
        return [etp for org in símismo for etp in símismo[org].etapas(fantasmas_de=símismo._cosos.values())]

    @property
    def orgs(símismo):
        return [símismo[org] for org in símismo]

    def añadir_org(símismo, org):
        símismo._cosos[str(org)] = org

    def quitar_org(símismo, org):
        try:
            símismo._cosos.pop(str(org))
        except KeyError:
            raise KeyError('El organismo "{org}" no existía en esta red.'.format(org=org))

    def inter(símismo, modelo, coso, tipo):
        if isinstance(tipo, str):
            tipo = [tipo]

        etps_inter = set()
        coords = set()
        for tp in tipo:
            if tp == 'presa':
                etps_inter.update(símismo.presas(coso))
                coords.update(símismo.presas())
            elif tp == 'huésped':
                etps_inter.update(símismo.huéspedes(coso))
                coords.update(símismo.huéspedes())
            else:
                raise ValueError(tipo)
        if len(etps_inter):
            return Inter(etps_inter, eje=EJE_VÍCTIMA, coords=coords)

    def presas(símismo, etps=None):
        if isinstance(etps, Etapa):
            etps = [etps]
        elif etps is None:
            etps = símismo.etapas
        presas = [pr for etp in etps for pr in etp.presas() if pr in símismo.etapas]

        # Incluir los fantasmas de las presas
        fants_presas = [etp for etp in símismo.etapas if isinstance(etp, EtapaFantasma) and etp.etp_hués in presas]

        return presas + fants_presas

    def huéspedes(símismo, etps=None):
        """Huéspedes que pueden ser directamente infectados por parasitoide `etp`."""
        if isinstance(etps, Etapa):
            etps = [etps]
        elif etps is None:
            etps = símismo.etapas
        return [pr for etp in etps for pr in etp.huéspedes() if pr in símismo.etapas]

    def fantasmas(símismo, etp):
        return [pr for pr in etp.org.fantasmas() if pr.etp_espejo in símismo.etapas]

    def gen_ecs(símismo, modelo, mód, exper, n_reps):
        return EcsOrgs(modelo, mód, exper, cosos=símismo.etapas, n_reps=n_reps)
