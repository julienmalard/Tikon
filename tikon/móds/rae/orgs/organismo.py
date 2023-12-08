from itertools import product
from typing import Union, Iterable

from tikon.central.coso import Coso
from .ecs import EcsOrgs
from .ecs.utils import ECS_EDAD, ECS_MRTE, ECS_TRANS, ECS_ESTOC
from .etapa import Etapa, EtapaFantasma
from ..utils import contexto


class Organismo(Coso):
    """
    Un organismo es la clase pariente para cualquier especie en una red agroecológica.
    """

    def __init__(símismo, nombre: str, etapas: Union["Etapa", Iterable["Etapa"]]):
        super().__init__(nombre, ecs=EcsOrgs)

        if ':' in símismo.nombre:
            raise ValueError('Nombre de organismo no puede contener ":".')

        if isinstance(etapas, Etapa):
            etapas = [etapas]
        etapas = [e if isinstance(e, Etapa) else símismo._gen_etapa(e) for e in etapas]

        símismo.etapas = etapas

    def activar_ec(símismo, categ: str, subcateg: str, ec: str, etapas: "Tipo_Resolvable_A_Etapas" = None):
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

    def espec_apriori(símismo, apriori, categ, sub_categ, ec, prm, índs=None, etapas=None):
        etapas = símismo.resolver_etapas(etapas)
        for etp in etapas:
            etp.espec_apriori(apriori, categ, sub_categ, ec, prm, índs=índs)

    def borrar_aprioris(
            símismo, categ: str = None, sub_categ: str = None, ec: str = None, prm: str = None, índs=None,
            etapas=None
    ):
        etapas = símismo.resolver_etapas(etapas)
        for etp in etapas:
            etp.borrar_aprioris(categ, sub_categ, ec, prm, índs=índs)

    def verificar(símismo):
        for etp in símismo.etapas:
            etp.ecs.verificar()

    def borrar_calib(símismo, nombre):
        for etp in símismo.etapas:
            etp.borrar_calib(nombre)

    def renombrar_calib(símismo, nombre, nuevo):
        for etp in símismo.etapas:
            etp.renombrar_calib(nombre, nuevo)

    def secome(símismo, presa, etps_presa=None, etps_símismo=None):
        etps_presa = presa.resolver_etapas(etps_presa)
        etps_símismo = símismo.resolver_etapas(etps_símismo)
        if not contexto:
            raise ValueError('Debes especificar relaciones tróficas adentro de un bloque `with` con la red de interés.')

        for red, e_p, e_s in product(contexto, etps_presa, etps_símismo):
            red.agregar_relación(RelaciónPresa(presa=presa, etp_presa=e_p, etp_depred=e_s))

    def parasita(símismo, huésped, etps_entra, etp_emerg, etp_recip, etp_símismo=None):
        if not contexto:
            raise ValueError('Debes especificar relaciones tróficas adentro de un bloque `with` con la red de interés.')

        etps_entra = huésped.resolver_etapas(etps_entra)
        etp_emerg = huésped.resolver_etapas(etp_emerg)[0]
        etp_recip = símismo.resolver_etapas(etp_recip)[0]

        if etp_símismo is None:
            etp_símismo = símismo.etapas[-1]
        etp_símismo = símismo.resolver_etapas(etp_símismo)[0]

        obj_rel = RelaciónParas(
            huésped=huésped, etps_entra=etps_entra, etp_depred=etp_símismo, etp_emerg=etp_emerg, etp_recip=etp_recip
        )
        for red in contexto:
            red.agregar_relación(obj_rel)

    def resolver_etapas(símismo, etapas):
        if etapas is None:
            etapas = símismo.etapas
        elif isinstance(etapas, (str, Etapa)):
            etapas = [etapas]
        etapas = [símismo[e] if isinstance(e, str) else e for e in etapas]

        return etapas

    def índice(símismo, etp):
        if isinstance(etp, str):
            etp = símismo[etp]
        return símismo.etapas.index(etp)

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
        return len(símismo.etapas)

    def __getitem__(símismo, itema):
        if isinstance(itema, int):
            return símismo.etapas[itema]
        try:
            return next(e for e in símismo.etapas if e.nombre == itema)
        except StopIteration:
            raise KeyError('Etapa {etp} no existe en organismo {org}.'.format(etp=itema, org=símismo))

    def __iter__(símismo):
        for etp in símismo.etapas:
            yield etp

    def __contains__(símismo, itema):
        if isinstance(itema, str):
            return any(str(itema) == e.nombre for e in símismo.etapas)
        return any(itema is e for e in símismo.etapas)


categs_parás = [ECS_TRANS, ECS_EDAD, ECS_MRTE, ECS_ESTOC]


class RelaciónOrgs(object):
    def __init__(símismo, orgs):
        símismo.orgs = orgs

    @property
    def tipo(símismo):
        raise NotImplementedError


class RelaciónPresa(RelaciónOrgs):
    tipo = 'presa'

    def __init__(símismo, presa, etp_presa, etp_depred):
        símismo.presa = presa
        símismo.etp_presa = etp_presa
        símismo.etp_depred = etp_depred
        super().__init__([presa, etp_depred.org])


class RelaciónParas(RelaciónOrgs):
    tipo = 'paras'

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
        símismo.fantasmas.reverse()

        super().__init__([huésped, etp_depred.org])
