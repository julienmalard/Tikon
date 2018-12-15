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
        símismo.info_etps = None  # type: InfoEtapas
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
        símismo.info_etps = InfoEtapas(símismo._orgs)
        símismo._ecs_simul = EcsOrgs(
            símismo.info_etps, mód=símismo, í_cosos=None, n_rep=n_rep_parám
        )
        símismo.cohortes = Cohortes(símismo.info_etps, n_rep_estoc, n_rep_parám, parc=parc)

        super().iniciar_estruc(tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc)

    def iniciar_vals(símismo):
        pass

    def incrementar(símismo):
        símismo._ecs_simul.eval(símismo.tiempo.paso)

    def cerrar(símismo):
        pass

    def poner_valor(símismo, var, valor, rel=False, índs=None):
        if var == 'Pobs':
            super().poner_valor(var, valor, rel=False, índs=índs)
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

    def inter(símismo, coso, tipo):
        if isinstance(tipo, str):
            tipo = [tipo]

        etps = símismo.info_etps
        tmñ_total = len(etps)

        etps_inter = set()
        for tp in tipo:
            if tp == 'presa':
                etps_inter.update(símismo.info_etps.presas(coso))
            elif tp == 'huésped':
                etps_inter.update(símismo.info_etps.huéspedes(coso))
            else:
                raise ValueError(tipo)
        índs = {etps.índice(etp): [etp.org, etp] for etp in etps_inter}
        if len(índs):
            return Inter(tmñ=tmñ_total, índices=índs)

    # para hacer: limpiar y reorganizar estos
    def í_repr(símismo):
        return [
            símismo.info_etps.índice(etp.org[0]) for etp in símismo.info_etps
            if etp.categ_activa('Reproducción', símismo)
        ]

    def _coords_resultados(símismo):

        l_res = ['Edad', 'Crecimiento', 'Reproducción', 'Muertes', 'Transiciones', 'Estoc']
        parc = símismo.obt_val_control('parcelas')

        return {
            'Pobs': {'etapa': símismo.info_etps.etapas},
            'Depredación': {
                'etapa': símismo._ecs_simul.cosos_en_categ('Depredación'),
                'víctima': símismo.info_etps.etapas
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

    def presas(símismo, etp):
        return [pr for pr in etp.presas() if pr in símismo]

    def huéspedes(símismo, etp):
        return [pr for pr in etp.huéspedes() if pr in símismo]

    def índice(símismo, etp):
        return símismo.etapas.index(etp)

    def __iter__(símismo):
        for etp in símismo.etapas:
            yield etp

    def __contains__(símismo, itema):
        return itema in símismo.etapas

    def __len__(símismo):
        return len(símismo.etapas)
