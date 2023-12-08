from typing import Iterable

from tikon.central import Coso
from tikon.central.coso import SumaCosos
from tikon.móds.rae.orgs.ecs import EcsOrgs
from tikon.móds.rae.orgs.ecs.utils import ECS_EDAD
from tikon.móds.rae.orgs.organismo import categs_parás, Organismo


class Etapa(Coso):
    def __init__(símismo, nombre, org):
        super().__init__(nombre, EcsOrgs)

        if ":" in símismo.nombre:
            raise ValueError('Un nombre de etapa no puede contener el carácter ":".')

        símismo.org = org

    @property
    def índices_inter(símismo):
        return [str(símismo.org), str(símismo)]

    def con_cohortes(símismo, exper):
        return símismo.categ_activa(ECS_EDAD, modelo=None, mód=None, exper=exper)

    def siguiente(símismo):
        índice = símismo.org.índice(símismo)
        if índice < (len(símismo.org) - 1):
            return símismo.org[índice + 1]

    def __add__(símismo, otro):
        return SumaEtapas([símismo, otro])

    def __str__(símismo):
        return str(símismo.org) + " : " + símismo.nombre

    def __eq__(símismo, otro):
        return (
                isinstance(otro, símismo.__class__)
                and símismo.nombre == otro.nombre
                and símismo.org == otro.org
        )

    def __hash__(símismo):
        return hash(str(símismo))


class EtapaFantasma(Etapa):
    def __init__(símismo, org, etp, org_hués, etp_hués, sig):
        nombre = f"{etp.nombre} en {etp_hués.org}, {etp_hués.nombre}"
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
        categs_de_hués = [
            str(ctg) for ctg in símismo.ecs if str(ctg) not in categs_de_prs
        ]

        for ctg in categs_de_hués:
            símismo.ecs[ctg] = símismo.etp_hués.ecs[ctg]

        for ctg in categs_de_prs:
            símismo.ecs[ctg] = símismo.etp_espejo.ecs[ctg]

    def siguiente(símismo):
        return símismo.sig


class EspecificaciónEtapas(object):
    def resolver(símismo, etapas: list[Etapa]) -> Iterable[Etapa]:
        for e in etapas:
            if símismo.concuerda(e):
                yield e

    def concuerda(símismo, etapa: Etapa) -> bool:
        raise NotImplementedError

    @staticmethod
    def _iter_etapas_huéspedes(etapa: EtapaFantasma) -> Iterable[Etapa]:
        etapa_huésped = etapa.etp_hués
        if isinstance(etapa_huésped, EtapaFantasma):
            return EspecificaciónEtapas._iter_etapas_huéspedes(etapa_huésped)
        else:
            yield etapa_huésped


class EspecificaciónEtapasOrganismo(EspecificaciónEtapas):
    def __init__(símismo, organismo: Organismo, incluir_parasitadas: bool):
        símismo.organismo = organismo
        símismo.incluir_parasitadas = incluir_parasitadas

    def concuerda(símismo, etapa: Etapa) -> bool:
        if isinstance(etapa, EtapaFantasma):
            if not símismo.incluir_parasitadas:
                return False
            for h in símismo._iter_etapas_huéspedes(etapa):
                if h.org == símismo.organismo:
                    return True
            return False
        else:
            return etapa.org == símismo.organismo


class EspecificaciónEtapaPorNombre(EspecificaciónEtapasOrganismo):
    def __init__(
            símismo, organismo: Organismo, nombre_etapa: str, incluir_parasitadas: bool
    ):
        super().__init__(organismo=organismo, incluir_parasitadas=incluir_parasitadas)
        símismo.nombre_etapa = nombre_etapa

    def concuerda(símismo, etapa: Etapa) -> bool:
        def _obt_huésped_base(f: EtapaFantasma) -> [Organismo, Etapa]:
            etapa_huésped = f.etp_hués
            if isinstance(etapa_huésped, EtapaFantasma):
                return _obt_huésped_base(etapa_huésped)
            else:
                return etapa_huésped.org, etapa_huésped

        if isinstance(etapa, EtapaFantasma):
            if not símismo.incluir_parasitadas:
                return False
            for h in símismo._iter_etapas_huéspedes(etapa):
                if h.org == símismo.organismo and símismo.nombre_concuerda(h.nombre):
                    return True
                return False
        else:
            return etapa.org == símismo.organismo and símismo.nombre_concuerda(etapa.nombre)

    def nombre_concuerda(símismo, nombre: str) -> bool:
        return nombre == símismo.nombre_etapa


class EspecificaciónEtapaPorPrincipioNombre(EspecificaciónEtapaPorNombre):
    def nombre_concuerda(símismo, nombre: str) -> bool:
        return símismo.nombre_etapa.startswith(nombre)


class EspecificaciónEtapasEtapa(EspecificaciónEtapas):
    def __init__(símismo, etapa: Etapa, incluir_parasitadas: bool):
        símismo.etapa = etapa
        símismo.incluir_parasitadas = incluir_parasitadas

    def concuerda(símismo, etapa: Etapa) -> bool:
        if isinstance(etapa, EtapaFantasma):
            if not símismo.incluir_parasitadas:
                return False
            return any(
                e == símismo.etapa for e in símismo._iter_etapas_huéspedes(etapa)
            )
        return etapa == símismo.etapa


ResolvableAEtapas = Organismo | Etapa | EspecificaciónEtapas


def generar_especificación_etapas(
        criterio: ResolvableAEtapas, incluir_parasitadas: bool
) -> EspecificaciónEtapas:
    if isinstance(criterio, EspecificaciónEtapas):
        return criterio
    elif isinstance(criterio, Organismo):
        return EspecificaciónEtapasOrganismo(
            organismo=criterio, incluir_parasitadas=incluir_parasitadas
        )
    elif isinstance(criterio, Etapa):
        return EspecificaciónEtapasEtapa(
            etapa=criterio, incluir_parasitadas=incluir_parasitadas
        )
    raise TypeError(criterio)


class SumaEtapas(SumaCosos):
    def __add__(símismo, otro):
        if isinstance(otro, Etapa):
            return SumaEtapas([otro, *símismo.cosos])
        else:
            return SumaEtapas(*list(otro), *símismo.cosos)
