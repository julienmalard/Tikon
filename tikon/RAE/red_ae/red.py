from tikon.ecs.paráms import Inter
from tikon.módulo import Módulo
from .cohortes import Cohortes
from .. import Organismo
from ..orgs.ecs import EcsOrgs


class RedAE(Módulo):
    nombre = 'red'

    def __init__(símismo, orgs=None):
        super().__init__()

        símismo._orgs = {}
        símismo._info_etps = None  # type: InfoEtapas
        símismo._ecs_simul = None  # type: EcsOrgs
        símismo.cohortes = None  # type: Cohortes

        if orgs is not None:
            if isinstance(orgs, Organismo):
                orgs = [orgs]
            for org in orgs:
                símismo.añadir_org(org)

    def añadir_org(símismo, org):
        símismo._orgs[str(org)] = org

    def quitar_org(símismo, org):
        if isinstance(org, Organismo):
            org = str(org)
        try:
            símismo._orgs.pop(org)
        except KeyError:
            raise KeyError('El organismo {org} no existía en esta red.'.format(org=org))

    def paráms(símismo):
        return símismo._ecs_simul.vals_paráms()

    def iniciar_estruc(símismo, tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc):
        símismo._info_etps = InfoEtapas(símismo._orgs)
        símismo._ecs_simul = EcsOrgs(
            símismo._info_etps, mód=símismo, í_cosos=None, n_rep=n_rep_parám
        )
        símismo.cohortes = Cohortes(símismo._info_etps, n_rep_estoc, n_rep_parám, len(parc))

        super().iniciar_estruc(tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc)

    def iniciar_vals(símismo):
        pass

    def incrementar(símismo):
        símismo._ecs_simul.eval(símismo.tiempo.paso)

    def cerrar(símismo):
        pass

    def poner_valor(símismo, var, valor, rel=False):
        if var == 'Poblaciones':
            super().poner_valor(var, valor, rel=False)
        else:
            raise ValueError(var)

    def obt_valor(símismo, var):
        if var == 'Dens':
            pobs = super().obt_valor('Pobs')
            superficies = símismo.obt_val_control('superficies')
            return pobs / superficies
        else:
            return super().obt_valor(var)

    def agregar_pobs(símismo, pobs):
        símismo.poner_valor('Pobs', pobs, rel=True)
        símismo.cohortes.agregar(pobs)

    def quitar_pobs(símismo, pobs):
        símismo.poner_valor('Pobs', -pobs, rel=True)
        símismo.cohortes.quitar(pobs)

    def ajustar_pobs(símismo, pobs):
        símismo.poner_valor('Pobs', pobs, rel=True)
        símismo.cohortes.ajustar(pobs)

    def presas(símismo, etp):
        return [pr for pr in etp.presas() if pr in símismo._info_etps]

    def huéspedes(símismo, etp):
        return [pr for pr in etp.huéspedes() if pr in símismo._info_etps]

    def inter(símismo, coso, tipo):
        if isinstance(tipo, str):
            tipo = [tipo]

        etps = símismo._info_etps
        tmñ_total = len(etps)

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
            return Inter(tmñ=tmñ_total, índices=índs)

    def _coords_resultados(símismo):

        l_res = ['Crecimiento', 'Reproducción', 'Muertes', 'Transiciones', 'Estoc']
        parc = símismo.obt_val_control('parcelas')

        return {
            'Pobs': {'etapa': símismo._info_etps.etapas},
            'Depredación': {
                'etapa': símismo._ecs_simul.cosos_en_categ('Depredación'),
                'víctima': símismo._info_etps.etapas
            },
            'Movimiento': {
                'etapa': símismo._ecs_simul.cosos_en_categ('Movimiento'),
                'dest': parc
            },
            **{res: {'etapa': símismo._ecs_simul.cosos_en_categ(res)} for res in l_res}
        }

    def __getitem__(símismo, itema):
        return símismo._orgs[str(itema)]

    def __iter__(símismo):
        for org in símismo._orgs.values():
            yield org


class InfoEtapas(object):
    def __init__(símismo, orgs):
        símismo._orgs = list(orgs.values()) if isinstance(orgs, dict) else orgs
        símismo.etapas = [etp for org in símismo._orgs for etp in org.etapas(fantasmas=True)]

    def índice(símismo, etp):
        return símismo.etapas.index(etp)

    def __iter__(símismo):
        for etp in símismo.etapas:
            yield etp

    def __len__(símismo):
        return len(símismo.etapas)
