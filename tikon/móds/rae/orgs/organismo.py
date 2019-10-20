from typing import List

from tikon.estruc.coso import Coso
from .ecs import EcsOrgs


class Organismo(Coso):
    """
    Un organismo es la clase pariente para cualquier especie en una red agroecológica.
    """

    def __init__(símismo, nombre):
        super().__init__(nombre, ecs=EcsOrgs)

        símismo._etapas = []  # type: List[Etapa]
        símismo._rels_presas = []  # type: List[RelaciónPresa]
        símismo._rels_paras = []  # type: List[RelaciónParas]

    def añadir_etapa(símismo, nombre, pos=None):

        etapa = Etapa(nombre, símismo)
        if pos is None:
            símismo._etapas.append(etapa)
        else:
            símismo._etapas.insert(pos, etapa)

    def activar_ec(símismo, categ, subcateg, ec, etapas=None):
        etapas = símismo.resolver_etapas(etapas)

        for etp in etapas:
            etp.activar_ec(categ=categ, subcateg=subcateg, ec=ec)

    def activar_ecs(símismo, dic_ecs):
        for etp, d_etp in dic_ecs.items():
            etps = símismo.resolver_etapas(etp)
            for e in etps:
                e.activar_ecs(d_etp)

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
        símismo._rels_paras.append(obj_rel)

    def noparasita(símismo, huésped, etps_entra=None, etps_símismo=None):

        etps_entra = símismo.resolver_etapas(etps_entra)
        etps_símismo = símismo.resolver_etapas(etps_símismo)

        for rel in list(símismo._rels_paras):
            if rel.huésped is huésped and rel.etps_entra in etps_entra and rel.etp_depred in etps_símismo:
                símismo._rels_paras.remove(rel)

    def resolver_etapas(símismo, etapas):
        if etapas is None:
            etapas = símismo._etapas
        elif isinstance(etapas, (str, Etapa)):
            etapas = [etapas]
        etapas = [símismo[e] if isinstance(e, str) else e for e in etapas]

        return etapas

    def etapas(símismo):
        etapas = símismo._etapas

        fants = []
        for r_p in símismo._rels_paras:
            huésped = r_p.huésped
            etps_en_hués = range(min(huésped.índice(r_p.etps_entra)), huésped.índice(r_p.etp_emerg) + 1)

            fant = None
            for í_etp in reversed(etps_en_hués):
                fant = EtapaFantasma(
                    símismo, etp=símismo._etapas[0], org_hués=r_p.huésped, etp_hués=huésped[í_etp],
                    sig=fant or r_p.etp_recip
                )
                fants.append(fant)

        return etapas + fants

    def índice(símismo, etp):
        if isinstance(etp, list):
            return [símismo.índice(e) for e in etp]
        if isinstance(etp, str):
            etp = símismo[etp]
        return símismo._etapas.index(etp)

    def presas(símismo, etp=None):
        if etp is None:
            return [rel.etp_presa for rel in símismo._rels_presas]
        return [rel.etp_presa for rel in símismo._rels_presas if rel.etp_depred == etp]

    def huéspedes(símismo, etp=None):
        if etp is None:
            return [e_h for rel in símismo._rels_paras for e_h in rel.etps_entra]
        return [e_h for rel in símismo._rels_paras for e_h in rel.etps_entra if rel.etp_depred == etp]

    def espec_apriori_etp(símismo, etapa, apriori, categ, subcateg, ec, prm, índs=None):
        símismo[etapa].espec_apriori(apriori, categ, subcateg, ec, prm, índs)

    def _ecs_a_json(símismo):
        return {etp.nombre: etp._ecs_a_json() for etp in símismo}

    def _ecs_de_json(símismo, calibs):
        for etp in símismo:
            if etp.nombre in calibs:
                etp._ecs_de_json(calibs[etp.nombre])

    def __getitem__(símismo, itema):
        if isinstance(itema, int):
            return símismo._etapas[itema]
        if isinstance(itema, Etapa):
            itema = itema.nombre
        else:
            itema = str(itema)
        try:
            return next(e for e in símismo._etapas if e.nombre == itema)
        except StopIteration:
            raise KeyError('Etapa {etp} no existe en organismo {org}.'.format(etp=itema, org=str(símismo)))

    def __iter__(símismo):
        for etp in símismo._etapas:
            yield etp

    def __contains__(símismo, itema):
        # para hacer: más elegante, y coordinar con __getitem__()
        return any(str(itema) == e.nombre for e in símismo._etapas)

    def __len__(símismo):
        return len(símismo._etapas)


class Etapa(Coso):
    def __init__(símismo, nombre, org):
        super().__init__(nombre, EcsOrgs)
        símismo.org = org

    def presas(símismo):
        return símismo.org.presas(símismo)

    def huéspedes(símismo):
        return símismo.org.huéspedes(símismo)

    def con_cohortes(símismo):
        return símismo.categ_activa(EDAD, mód=símismo)

    def siguiente(símismo):
        índice = símismo.org.índice(símismo)
        if índice < (len(símismo.org) - 1):
            return símismo.org[índice + 1]

    def __str__(símismo):
        return str(símismo.org) + ' ' + símismo.nombre


class EtapaFantasma(Etapa):
    def __init__(símismo, org, etp, org_hués, etp_hués, sig):
        nombre = f'{etp.nombre} en {etp_hués}'
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
            categs_de_prs = [TRANS, EDAD, MRTE]
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
