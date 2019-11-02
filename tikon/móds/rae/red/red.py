import numpy as np
import xarray as xr
from tikon.ecs.paráms import Inter
from tikon.estruc.módulo import Módulo
from tikon.estruc.simul import SimulMódulo
from tikon.móds.rae.orgs.ecs.utils import ECS_TRANS, ECS_REPR
from tikon.móds.rae.orgs.insectos import Parasitoide
from tikon.móds.rae.red.res.cohortes import ResCohortes
from tikon.móds.rae.red.utils import RES_POBS, RES_COHORTES, EJE_COH, EJE_ETAPA, EJE_VÍCTIMA

from ..orgs.ecs import EcsOrgs
from ..orgs.organismo import EtapaFantasma
from ..red.res import res as res_red


class RedAE(Módulo):
    nombre = 'red'

    def __init__(símismo, orgs=None):
        super().__init__(cosos=orgs)

    @property
    def etapas(símismo):
        return [etp for org in símismo for etp in símismo[org].etapas(fants_de=símismo._cosos)]

    def añadir_org(símismo, org):
        símismo._cosos[str(org)] = org

    def quitar_org(símismo, org):
        try:
            símismo._cosos.pop(str(org))
        except KeyError:
            raise KeyError('El organismo "{org}" no existía en esta red.'.format(org=org))

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        return SimulRed(simul_exper=simul_exper, etapas=símismo.etapas, ecs=ecs, vars_interés=vars_interés)

    def gen_ecs(símismo, n_reps):
        return EcsOrgs(cosos=símismo.etapas, n_reps=n_reps)


class SimulRed(SimulMódulo):
    resultados = [
        res_red.ResPobs, res_red.ResEdad, res_red.ResCrec, res_red.ResDepred, res_red.ResRepr,
        res_red.ResMuerte, res_red.ResTrans, res_red.ResMov, res_red.ResEstoc, ResCohortes
    ]

    def __init__(símismo, simul_exper, etapas, ecs, vars_interés):

        símismo.etapas = etapas

        símismo.víctimas = set(pr for etp in símismo.etapas for pr in etp.presas()).union(
            set(h for etp in símismo.etapas for h in símismo.huéspedes(etp))
        )

        símismo.etps_repr = [
            etp.org[0] for etp in símismo.etapas if etp.categ_activa(ECS_REPR, símismo)
        ]
        símismo.recip_trans = [
            (etp, etp.siguiente()) for etp in etapas if etp.categ_activa(ECS_TRANS, símismo) and etp.siguiente()
        ]

        símismo.parás_hués = [
            (etp, símismo.huéspedes(etp), símismo.fantasmas(etp))
            for etp in símismo.etapas if isinstance(etp.org, Parasitoide)
        ]

        # Índices para luego poder encontrar las interacciones entre parasitoides y víctimas en las matrices de
        # depredación
        símismo.máscara_parás = xr.DataArray(
            False, coords={EJE_ETAPA: símismo.etapas, EJE_VÍCTIMA: símismo.víctimas}
        )
        for parás, hués_fants in símismo.parás_hués:
            símismo.máscara_parás.loc[{EJE_ETAPA: parás, EJE_VÍCTIMA: hués_fants[0]}] = True

        super().__init__(nombre=RedAE.nombre, simul_exper=simul_exper, ecs=ecs, vars_interés=vars_interés)

    def requísitos(símismo, controles=False):
        return {req for etp in símismo.etapas for req in etp.requísitos(controles)}

    def inter(símismo, coso, tipo):
        if isinstance(tipo, str):
            tipo = [tipo]

        etps_inter = set()
        for tp in tipo:
            if tp == 'presa':
                etps_inter.update(símismo.presas(coso))
            elif tp == 'huésped':
                etps_inter.update(símismo.huéspedes(coso))
            else:
                raise ValueError(tipo)
        inter = [[str(etp.org), str(etp)] for etp in etps_inter]
        if len(inter):
            return Inter(inter, eje=EJE_VÍCTIMA)

    def presas(símismo, etp):
        presas = [pr for pr in etp.presas() if pr in símismo]

        # Incluir los fantasmas de las presas
        fants_presas = [etp for etp in símismo.etapas if isinstance(etp, EtapaFantasma) and etp.etp_hués in presas]

        return presas + fants_presas

    def huéspedes(símismo, etp):
        """Huéspedes que pueden ser directamente infectados por parasitoide `etp`."""
        return [pr for pr in etp.huéspedes() if pr in símismo.etapas]

    def fantasmas(símismo, etp):
        return [pr for pr in etp.org.fantasmas() if pr in símismo.etapas]

    def iniciar(símismo):
        super().iniciar()

        símismo[RES_COHORTES].agregar(símismo[RES_POBS].valores())

    def cerrar(símismo):
        pass

    def poner_valor(símismo, var, val, rel=False):
        if var == RES_POBS:
            cambio = val if rel else val - símismo[RES_POBS].datos
            símismo[RES_COHORTES].ajustar(cambio)
        else:
            raise ValueError('No se puede cambiar el valor de {} durante una simulación.'.format(var))

        super().poner_valor(var, val, rel)

    def verificar_estado(símismo):
        super().verificar_estado()

        mnsg = '\tSi acabas de agregar nuevas ecuaciones, es probablemente culpa tuya.\n\tSino, es culpa mía.'
        pobs = símismo[RES_POBS].datos

        if np.any(np.not_equal(pobs.astype(int), pobs)):
            raise ValueError('Población fraccional.\n{mnsg}'.format(mnsg=mnsg))

        if símismo[RES_COHORTES].datos.values.size:
            pobs_coh = símismo[RES_COHORTES].datos['pobs']
            if pobs_coh.min() < 0:
                raise ValueError('Población de cohorte inferior a 0.\n{mnsg}'.format(mnsg=mnsg))
            if np.any(np.not_equal(pobs_coh.astype(int), pobs_coh)):
                raise ValueError('Población de cohorte fraccional.\n{mnsg}'.format(mnsg=mnsg))
            if np.any(np.isnan(pobs_coh)):
                raise ValueError('Población de cohorte "nan".\n{mnsg}'.format(mnsg=mnsg))
            if np.any(np.not_equal(pobs_coh.sum(dim=EJE_COH), pobs)):
                raise ValueError('Población de cohorte no suma a población total.\n{mnsg}'.format(mnsg=mnsg))
