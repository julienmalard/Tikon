from copy import copy
from typing import Dict

from .dists import DistAnalítica, MnjdrDists


class PlantillaRamaEcCoso(object):
    def __init__(símismo, cls_pariente, ramas, coso):
        símismo.coso = coso
        símismo.cls_pariente = cls_pariente
        símismo._ramas = {str(r): r for r in ramas}

    def verificar_activa(símismo, mód):
        if símismo.cls_pariente.req_todas_ramas:
            return all(rm.verificar_activa(mód) for rm in símismo)
        else:
            return any(rm.verificar_activa(mód) for rm in símismo)

    def a_dic(símismo):
        return {ll: v for ll, v in {nmb: rm.a_dic() for nmb, rm in símismo._ramas.items()}.items() if len(v)}

    def __getitem__(símismo, itema):
        return símismo._ramas[str(itema)]

    def __setitem__(símismo, llave, valor):
        símismo._ramas[llave] = valor

    def __iter__(símismo):
        for rm in símismo._ramas.values():
            yield rm

    def __contains__(símismo, itema):
        return str(itema) in símismo._ramas

    def __copy__(símismo):
        ramas = [copy(rm) for rm in símismo._ramas.values()]
        return símismo.__class__(símismo.cls_pariente, ramas=ramas, coso=símismo.coso)

    def __eq__(símismo, otro):
        return símismo.cls_pariente == otro

    def __str__(símismo):
        return str(símismo.cls_pariente.nombre)


class ÁrbolEcsCoso(PlantillaRamaEcCoso):

    def espec_apriori(símismo, apriori, categ, sub_categ, ec, parám, índs=None):
        obj_parám = símismo._ramas[categ][sub_categ][ec][parám]
        obj_parám.espec_a_priori(apriori, inter=índs)

    def activar_ec(símismo, categ, subcateg, ec):
        símismo[categ][subcateg].activar_ec(ec)

    def desactivar_ec(símismo, categ, subcateg=None):
        símismo[categ].desactivar_ec(subcateg=subcateg)

    def de_dic(símismo, dic):
        raise NotImplementedError


class CategEcCoso(PlantillaRamaEcCoso):

    def activar_ec(símismo, subcateg, ec):
        símismo[subcateg].activar_ec(ec)

    def desactivar_ec(símismo, subcateg=None):
        if subcateg is None:
            subcateg = símismo._ramas.values()
        else:
            subcateg = [subcateg]
        for sub in subcateg:
            sub.desactivar_ec()


class SubcategEcCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente, ramas, coso):
        super().__init__(cls_pariente, ramas, coso)

        if cls_pariente.auto is not None:
            símismo._activada = next(ec for ec in símismo if ec.cls_pariente is cls_pariente.auto)
        else:
            símismo._activada = ramas[0]

        símismo._activada.activada = True

    def verificar_activa(símismo, mód):
        return símismo.ec_activa().verificar_activa(mód)

    def activar_ec(símismo, ec):
        try:
            obj_ec = símismo[ec]
            símismo._activada = obj_ec
            for rm in símismo._ramas.values():
                rm.activada = False

            obj_ec.activada = True

        except KeyError:
            raise ValueError(ec)

    def desactivar_ec(símismo):
        símismo.activar_ec('Nada')

    def ec_activa(símismo):
        return símismo._activada


class EcuaciónCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente, ramas, coso):
        super().__init__(cls_pariente, ramas, coso)
        símismo.activada = False

    def verificar_activa(símismo, mód):
        from .árb_mód import EcuaciónVacía
        if símismo.activada and símismo != EcuaciónVacía:
            inters = símismo.cls_pariente.inter()
            if inters:
                return all(mód.inter(símismo.coso, tipo=intr) for intr in inters)
            return True
        return False


class ParámCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente, coso):
        super().__init__(cls_pariente, ramas=[], coso=coso)

        símismo._calibs = {}  # type: Dict[str, MnjdrDists]
        símismo._a_priori = MnjdrDists()

        símismo.líms = símismo.cls_pariente.líms
        símismo.inter = símismo.cls_pariente.inter

    def verificar_activa(símismo, mód):
        return True  # Parámetros de una ecuación activa siempre están activados.

    def agregar_calib(símismo, id_cal, dist, inter=None):
        if id_cal not in símismo._calibs:
            símismo._calibs[id_cal] = MnjdrDists()

        símismo._calibs[id_cal].actualizar(dist, inter)

    def espec_a_priori(símismo, apriori, inter=None):
        dist = apriori.dist(símismo.líms)
        símismo._a_priori.actualizar(dist=dist, índs=inter)

    def a_priori(símismo, inter=None):
        return símismo._a_priori.obt_val(inter)

    def calib_base(símismo):
        return DistAnalítica.de_líms(símismo.líms)

    def dists_disp(símismo, inter, heredar):
        return {clb: dists.obt_val(índs=inter, heredar=heredar) for clb, dists in símismo._calibs.items()}

    def a_dic(símismo):
        return {ll: v for ll, v in {nmb: clb.a_dic() for nmb, clb in símismo._calibs.items()}.items() if len(v)}

    def __copy__(símismo):
        return ParámCoso(símismo.cls_pariente, coso=símismo.coso)
