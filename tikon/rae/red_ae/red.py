import numpy as np

from tikon.ecs.paráms import Inter
from tikon.estruc.módulo import Módulo, DimsRes
from tikon.rae.red_ae.res import ResultadoRed, ResultadoEdad, ResultadoDepred
from tikon.result.dims import Coord
from tikon.result.res import ResultadosMódulo
from .cohortes import Cohortes
from .. import Organismo
from ..orgs.ecs import EcsOrgs
from ..orgs.organismo import EtapaFantasma


class RedAE(Módulo):
    nombre = 'red'

    def __init__(símismo, orgs=None):
        super().__init__()

        símismo._orgs = {}
        símismo.info_etps = None
        símismo.cohortes = None

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

    def espec_aprioris(símismo, a_prioris):
        for org, l_org in a_prioris.items():
            try:
                obj_org = símismo[org] if isinstance(org, str) else org
            except KeyError:
                continue

            for d_apr in l_org:
                if d_apr['etapa'] in obj_org:
                    obj_org.espec_apriori_etp(**d_apr)

    def iniciar_estruc(símismo, tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés):
        símismo.info_etps = InfoEtapas(símismo._orgs)
        símismo._ecs_simul = EcsOrgs(
            símismo.info_etps, mód=símismo, í_cosos=None, n_rep=n_rep_parám
        )
        símismo.cohortes = Cohortes(símismo.info_etps, n_rep_estoc, n_rep_parám, parc=parc)

        super().iniciar_estruc(tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés)

    def iniciar_vals(símismo):
        super().iniciar_vals()

        símismo.cohortes.reinic()
        símismo.cohortes.agregar(símismo.obt_valor('Pobs'))

    def incrementar(símismo):
        símismo._ecs_simul.eval(símismo.tiempo.paso)

    def cerrar(símismo):
        pass

    def poner_valor(símismo, var, valor, rel=False, índs=None):
        if var == 'Pobs':
            super().poner_valor(var, valor, rel=rel, índs=índs)
        else:
            raise ValueError(var)

    def obt_valor(símismo, var, índs=None):
        if var == 'Dens':
            pobs = super().obt_valor('Pobs', índs=índs)
            superficies = símismo.obt_val_control('superficies')  # para hacer: si índs contienen parcelas
            return pobs / superficies
        else:
            return super().obt_valor(var, índs=índs)

    def agregar_pobs(símismo, pobs, etapas=None):
        índs = {'etapa': etapas} if etapas else None
        símismo.poner_valor('Pobs', pobs, rel=True, índs=índs)
        símismo.cohortes.agregar(pobs, etapas=etapas)

    def quitar_pobs(símismo, pobs, etapas=None):
        índs = {'etapa': etapas} if etapas else None
        símismo.poner_valor('Pobs', -pobs, rel=True, índs=índs)
        símismo.cohortes.quitar(pobs, etapas=etapas)

    def ajustar_pobs(símismo, pobs, etapas=None):
        índs = {'etapa': etapas} if etapas else None
        símismo.poner_valor('Pobs', pobs, rel=True, índs=índs)
        símismo.cohortes.ajustar(pobs, etapas=etapas)

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
    def etps_repr(símismo):
        return [etp.org[0] for etp in símismo.info_etps if etp.categ_activa('Reproducción', símismo)]

    def etps_trans(símismo):
        etps_trans = [etp for etp in símismo.info_etps if etp.categ_activa('Transiciones', símismo)]
        siguientes = [etp.siguiente() for etp in etps_trans]
        return [(etp, sig) for etp, sig in zip(etps_trans, siguientes) if sig]

    def _gen_resultados(símismo, n_rep_estoc, n_rep_parám, vars_interés):

        l_res = ['Edad', 'Crecimiento', 'Reproducción', 'Muertes', 'Transiciones', 'Estoc']
        parc = símismo.obt_val_control('parcelas')

        obs = símismo.mnjdr_móds.exper.obtener_obs(símismo)
        inic_pobs = símismo.mnjdr_móds.exper.obt_inic(símismo, 'Pobs')

        coords = {
            'Pobs': {'etapa': Coord(símismo.info_etps.etapas)},
            'Depredación': {
                'etapa': Coord(símismo._ecs_simul.cosos_en_categ('Depredación')),
                'víctima': Coord(símismo.info_etps.etapas)
            },
            'Movimiento': {
                'etapa': Coord(símismo._ecs_simul.cosos_en_categ('Movimiento')),
                'dest': Coord(parc)
            },
            **{res: {'etapa': Coord(símismo._ecs_simul.cosos_en_categ(res))} for res in l_res}
        }

        cls_res = {
            'Depredación': ResultadoDepred,
            'Edad': ResultadoEdad
        }
        dims_base = DimsRes(n_estoc=n_rep_estoc, n_parám=n_rep_parám, parc=parc)

        # para hacer: generalizar para todos módulos
        if vars_interés is None:
            temporales = [vr for vr in coords if vr in obs]
        elif vars_interés is True:
            temporales = list(coords)
        else:
            temporales = vars_interés

        return ResultadosRed([
            (cls_res[nmb] if nmb in cls_res else ResultadoRed)(
                nmb, dims_base + crd,
                tiempo=símismo.tiempo if nmb in temporales else None,
                obs=obs[nmb] if nmb in obs else None,
                inic=inic_pobs if nmb == 'Pobs' else None,  # para hacer: ¿más elegante?
            ) for nmb, crd in coords.items()
        ])

    def guardar_calib(símismo, directorio=''):
        for org in símismo:
            org.guardar_calib(directorio)

    def __getitem__(símismo, itema):
        return símismo._orgs[str(itema)]

    def __iter__(símismo):
        for org in símismo._orgs.values():
            yield org

    def cargar_calib(símismo, directorio):
        for org in símismo:
            org.cargar_calib(directorio)


class InfoEtapas(object):
    def __init__(símismo, orgs):
        símismo._orgs = list(orgs.values()) if isinstance(orgs, dict) else orgs
        símismo.etapas = [etp for org in símismo._orgs for etp in org.etapas(fantasmas=True)]

    def presas(símismo, etp):
        presas = [pr for pr in etp.presas() if pr in símismo]
        fantasmas = [etp for etp in símismo if isinstance(etp, EtapaFantasma) and etp.etp_hués in presas]
        return presas + fantasmas

    def huéspedes(símismo, etp):
        return [pr for pr in etp.huéspedes() if pr in símismo]

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


class ResultadosRed(ResultadosMódulo):

    def verificar_estado(símismo):
        mnsg = '\tSi acabas de agregar nuevas ecuaciones, es probablemente culpa tuya.\n\tSino, es culpa mía.'
        pobs = símismo['Pobs'].obt_valor()
        if pobs.min() < 0:
            raise ValueError('Población inferior a 0.\n{}'.format(mnsg))
        if np.any(np.isnan(pobs)):
            raise ValueError('Población no numérica (p. ej., división por 0).\n{}'.format(mnsg))
        if np.any(np.not_equal(pobs.astype(int), pobs)):
            raise ValueError('Población fraccional.'.format(mnsg))
        # para hacer: incorporar cohortes como resultados e incluir las pruebas siguientes
        """
        if len(símismo.predics['Cohortes']):
            pobs_coh = símismo.predics['Cohortes']['Pobs']
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
