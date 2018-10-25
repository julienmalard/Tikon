from typing import List

from tikon.RAE.ecs import ecs_etps_orgs
from tikon.coso import Coso


class Organismo(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, ecs=None)

        símismo.etapas = []  # type: List[Etapa]
        símismo._rels_presas = []  # type: List[RelaciónPresa]
        símismo._rels_paras = []  # type: List[RelaciónParas]

    def añadir_etapa(símismo, nombre, pos):

        etapa = Etapa(nombre, símismo)
        símismo.etapas.insert(pos, etapa)

    def activar_ec(símismo, categ, subcateg, ec, etapas=None):
        etapas = símismo.resolver_etapas(etapas)

        for etp in etapas:
            etp.activar_ec(categ=categ, subcateg=subcateg, ec=ec)

    def activar_ecs(símismo, dic_ecs):
        for etp, d_etp in dic_ecs.items():
            símismo[etp].activar_ecs(d_etp)

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

    def parasita(símismo, huésped, etps_huésp, etp_emerg, etps_símismo=None):
        etps_huésp = huésped.resolver_etapas(etps_huésp)

        if etps_símismo is None:
            etps_símismo = símismo.etapas[-1]
        etps_símismo = símismo.resolver_etapas(etps_símismo)

        etp_emerg = huésped.resolver_etapas(etp_emerg)

        for e_h in etps_huésp:
            for e_s in etps_símismo:
                obj_rel = RelaciónParas(huésped=huésped, etp_huésp=e_h, etp_depred=e_s, etp_emerg=etp_emerg)
                símismo._rels_paras.append(obj_rel)

    def noparasita(símismo, huésped, etps_huésp=None, etps_símismo=None):

        etps_huésp = símismo.resolver_etapas(etps_huésp)
        etps_símismo = símismo.resolver_etapas(etps_símismo)

        for rel in list(símismo._rels_paras):
            if rel.huésped is huésped and rel.etp_huésp in etps_huésp and rel.etp_depred in etps_símismo:
                símismo._rels_paras.remove(rel)

    def resolver_etapas(símismo, etapas):
        if etapas is None:
            etapas = símismo.etapas
        elif isinstance(etapas, (str, Etapa)):
            etapas = [etapas]
        etapas = [símismo[e] if isinstance(e, str) else e for e in etapas]

        return etapas

    def __getitem__(símismo, itema):
        if isinstance(itema, int):
            return símismo.etapas[itema]
        else:
            try:
                return next(e for e in símismo.etapas if str(e) == itema)
            except StopIteration:
                raise KeyError('Etapa {etp} no existe en organismo {org}.'.format(etp=itema, org=str(símismo)))


class Etapa(Coso):
    def __init__(símismo, nombre, org):
        super().__init__(nombre, ecs_etps_orgs)
        símismo.org = org


class RelaciónPresa(object):
    def __init__(símismo, presa, etp_presa, etp_depred):
        símismo.presa = presa
        símismo.etp_presa = etp_presa
        símismo.etp_depred = etp_depred


class RelaciónParas(object):
    def __init__(símismo, huésped, etp_huésp, etp_depred, etp_emerg):
        símismo.huésped = huésped
        símismo.etp_huésp = etp_huésp
        símismo.etp_depred = etp_depred
        símismo.etp_emerg = etp_emerg
