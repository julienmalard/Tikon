from typing import List

from tikon.central.coso import Coso

from .ecs import EcsOrgs
from .ecs.utils import ECS_EDAD, ECS_MRTE, ECS_TRANS


class Organismo(Coso):
    """
    Un organismo es la clase pariente para cualquier especie en una red agroecológica.
    """

    def __init__(símismo, nombre, etapas):
        super().__init__(nombre, ecs=EcsOrgs)

        if ':' in símismo.nombre:
            raise ValueError('Nombre de organismo no puede contener ":".')

        if isinstance(etapas, Etapa):
            etapas = [etapas]
        etapas = [e if isinstance(e, Etapa) else símismo._gen_etapa(e) for e in etapas]

        símismo._etapas = etapas
        símismo._rels_presas = []  # type: List[RelaciónPresa]
        símismo._rels_parás = []  # type: List[RelaciónParas]

    def activar_ec(símismo, categ, subcateg, ec, etapas=None):
        etapas = símismo.resolver_etapas(etapas)

        for etp in etapas:
            etp.activar_ec(categ=categ, subcateg=subcateg, ec=ec)

    def activar_ecs(símismo, dic_ecs):
        for etp, d_etp in dic_ecs.items():
            etps = símismo.resolver_etapas(etp)
            for e in etps:
                e.activar_ecs(d_etp)

    def desactivar_ec(símismo, categ, subcateg=None):
        for etp in símismo:
            etp.desactivar_ec(categ=categ, subcateg=subcateg)

    def secome(símismo, presa, etps_presa=None, etps_símismo=None):
        etps_presa = presa.resolver_etapas(etps_presa)
        etps_símismo = símismo.resolver_etapas(etps_símismo)

        for e_p in etps_presa:
            for e_s in etps_símismo:
                obj_rel = RelaciónPresa(presa=presa, etp_presa=e_p, etp_depred=e_s)
                símismo._rels_presas.append(obj_rel)

    def nosecome(símismo, presa, etps_presa=None, etps_símismo=None):

        etps_presa = presa.resolver_etapas(etps_presa)
        etps_símismo = símismo.resolver_etapas(etps_símismo)

        for rel in list(símismo._rels_presas):
            if rel.presa is presa and rel.etp_presa in etps_presa and rel.etp_depred in etps_símismo:
                símismo._rels_presas.remove(rel)

    def parasita(símismo, huésped, etps_entra, etp_emerg, etp_recip, etp_símismo=None):
        etps_entra = huésped.resolver_etapas(etps_entra)
        etp_emerg = huésped.resolver_etapas(etp_emerg)[0]
        etp_recip = símismo.resolver_etapas(etp_recip)[0]

        if etp_símismo is None:
            etp_símismo = símismo._etapas[-1]
        etp_símismo = símismo.resolver_etapas(etp_símismo)[0]

        obj_rel = RelaciónParas(
            huésped=huésped, etps_entra=etps_entra, etp_depred=etp_símismo, etp_emerg=etp_emerg, etp_recip=etp_recip
        )
        símismo._rels_parás.append(obj_rel)

    def noparasita(símismo, huésped, etps_entra=None, etps_símismo=None):

        etps_entra = símismo.resolver_etapas(etps_entra)
        etps_símismo = símismo.resolver_etapas(etps_símismo)

        for rel in list(símismo._rels_parás):
            if rel.huésped is huésped and rel.etps_entra in etps_entra and rel.etp_depred in etps_símismo:
                símismo._rels_parás.remove(rel)

    def resolver_etapas(símismo, etapas):
        if etapas is None:
            etapas = símismo._etapas
        elif isinstance(etapas, (str, Etapa)):
            etapas = [etapas]
        etapas = [símismo[e] if isinstance(e, str) else e for e in etapas]

        return etapas

    def etapas(símismo, fantasmas_de=None):

        if fantasmas_de:
            etps_fant = [f for r_p in símismo._rels_parás for f in r_p.fantasmas if f.org_hués in fantasmas_de]
        else:
            etps_fant = []

        return símismo._etapas + etps_fant

    def índice(símismo, etp):
        if isinstance(etp, str):
            etp = símismo[etp]
        return símismo._etapas.index(etp)

    def presas(símismo, etp=None):
        return [rel.etp_presa for rel in símismo._rels_presas if (etp is None or rel.etp_depred == etp)]

    def huéspedes(símismo, etp=None):
        """
        Devuelve etapas huéspedes víctimas directas de parasitismo.

        Parameters
        ----------
        etp

        Returns
        -------

        """
        return [e_h for rel in símismo._rels_parás for e_h in rel.etps_entra if (etp is None or rel.etp_depred == etp)]

    def fantasmas(símismo):
        return [rel.fantasmas[í] for rel in símismo._rels_parás for í in range(len(rel.etps_entra))]

    def espec_apriori_etp(símismo, etapa, apriori, categ, subcateg, ec, prm, índs=None):
        símismo[etapa].espec_apriori(apriori, categ, subcateg, ec, prm, índs)

    def _gen_etapa(símismo, etp):
        return Etapa(etp, símismo)

    def _ecs_a_json(símismo):
        return {etp.nombre: etp._ecs_a_json() for etp in símismo}

    def _ecs_de_json(símismo, calibs):
        for etp in símismo:
            if etp.nombre in calibs:
                etp._ecs_de_json(calibs[etp.nombre])

    def __len__(símismo):
        return len(símismo._etapas)

    def __getitem__(símismo, itema):
        if isinstance(itema, int):
            return símismo._etapas[itema]
        try:
            return next(e for e in símismo._etapas if e.nombre == itema)
        except StopIteration:
            raise KeyError('Etapa {etp} no existe en organismo {org}.'.format(etp=itema, org=símismo))

    def __iter__(símismo):
        for etp in símismo._etapas:
            yield etp

    def __contains__(símismo, itema):
        if isinstance(itema, str):
            return any(str(itema) == e.nombre for e in símismo.etapas())
        return any(itema is e for e in símismo.etapas())


class Etapa(Coso):
    def __init__(símismo, nombre, org):
        super().__init__(nombre, EcsOrgs)

        if ':' in símismo.nombre:
            raise ValueError('Nombre de etapa no puede contener ":".')

        símismo.org = org

    @property
    def índices_inter(símismo):
        return [str(símismo.org), str(símismo)]

    def presas(símismo):
        return símismo.org.presas(símismo)

    def huéspedes(símismo):
        return símismo.org.huéspedes(símismo)

    def con_cohortes(símismo, exper):
        return símismo.categ_activa(ECS_EDAD, modelo=None, mód=símismo, exper=exper)

    def siguiente(símismo):
        índice = símismo.org.índice(símismo)
        if índice < (len(símismo.org) - 1):
            return símismo.org[índice + 1]

    def __add__(símismo, otro):
        return SumaEtapas([símismo, otro])

    def __str__(símismo):
        return str(símismo.org) + ' : ' + símismo.nombre


categs_parás = [ECS_TRANS, ECS_EDAD, ECS_MRTE]


class EtapaFantasma(Etapa):
    def __init__(símismo, org, etp, org_hués, etp_hués, sig):
        nombre = f'{etp.nombre} en {etp_hués.org}, {etp_hués.nombre}'
        super().__init__(nombre, org)

        símismo.etp_espejo = etp
        símismo.org_hués = org_hués
        símismo.etp_hués = etp_hués
        símismo.sig = sig

        símismo._vincular_ecs()

    def _vincular_ecs(símismo):

        if isinstance(símismo.sig, EtapaFantasma):
            categs_de_prs = []
        else:
            categs_de_prs = categs_parás
        categs_de_hués = [str(ctg) for ctg in símismo.ecs if str(ctg) not in categs_de_prs]

        for ctg in categs_de_hués:
            símismo.ecs[ctg] = símismo.etp_hués.ecs[ctg]

        for ctg in categs_de_prs:
            símismo.ecs[ctg] = símismo.etp_espejo.ecs[ctg]

    def siguiente(símismo):
        return símismo.sig


class RelaciónPresa(object):
    def __init__(símismo, presa, etp_presa, etp_depred):
        símismo.presa = presa
        símismo.etp_presa = etp_presa
        símismo.etp_depred = etp_depred


class RelaciónParas(object):
    def __init__(símismo, huésped, etps_entra, etp_depred, etp_emerg, etp_recip):
        símismo.huésped = huésped
        símismo.etps_entra = etps_entra
        símismo.etp_depred = etp_depred
        símismo.etp_emerg = etp_emerg
        símismo.etp_recip = etp_recip

        símismo.fantasmas = []
        etps_en_hués = range(min(huésped.índice(etp) for etp in etps_entra), huésped.índice(etp_emerg) + 1)

        for í_etp in reversed(etps_en_hués):
            símismo.fantasmas.append(EtapaFantasma(
                etp_depred.org, etp=etp_depred.org[0], org_hués=huésped, etp_hués=huésped[í_etp],
                sig=símismo.fantasmas[-1] if símismo.fantasmas else etp_recip
            ))


class SumaEtapas(object):
    def __init__(símismo, etapas):
        símismo.etapas = etapas

    def __add__(símismo, otro):
        if isinstance(otro, Etapa):
            return SumaEtapas([otro, *símismo.etapas])
        else:
            return SumaEtapas(*list(otro), *símismo.etapas)

    def __iter__(símismo):
        for etp in símismo.etapas:
            yield etp
