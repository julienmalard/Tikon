from copy import copy
from typing import Dict

from .dists import DistAnalítica, MnjdrDists


class PlantillaRamaEcCoso(object):
    def __init__(símismo, cls_pariente, ramas, coso):
        símismo.coso = coso
        símismo.cls_pariente = cls_pariente
        símismo._ramas = {str(r): r for r in ramas}

    def verificar_activa(símismo, modelo, mód):
        return any(rm.verificar_activa(modelo, mód) for rm in símismo)

    def a_dic(símismo):
        return {ll: v for ll, v in {nmb: rm.a_dic() for nmb, rm in símismo._ramas.items()}.items() if len(v)}

    def de_dic(símismo, dic):
        for rm in símismo:
            if str(rm) in dic:
                rm.de_dic(dic[str(rm)])

    def borrar_calib(símismo, nombre):
        for r in símismo:
            r.borrar_calib(nombre)

    def renombrar_calib(símismo, nombre, nuevo):
        for r in símismo:
            r.renombrar_calib(nombre, nuevo)

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

    def __str__(símismo):
        return str(símismo.cls_pariente.nombre)


class ÁrbolEcsCoso(PlantillaRamaEcCoso):

    def espec_apriori(símismo, apriori, categ, sub_categ, ec, parám, inter=None):
        obj_parám = símismo._ramas[categ][sub_categ][ec][parám]
        obj_parám.espec_apriori(apriori, inter=inter)

    def activar_ec(símismo, categ, subcateg, ec):
        símismo[categ][subcateg].activar_ec(ec)

    def desactivar_ec(símismo, categ, subcateg=None):
        símismo[categ].desactivar_ec(subcateg=subcateg)


class CategEcCoso(PlantillaRamaEcCoso):

    def activar_ec(símismo, subcateg, ec):
        símismo[subcateg].activar_ec(ec)

    def desactivar_ec(símismo, subcateg=None):
        if subcateg is None:
            subcateg = list(símismo._ramas)
        else:
            subcateg = [subcateg]
        for sub in subcateg:
            símismo[sub].desactivar_ec()


class SubcategEcCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente, ramas, coso):
        super().__init__(cls_pariente, ramas, coso)

        símismo._activada = ramas[0]

        símismo._activada.activada = True

    def verificar_activa(símismo, modelo, mód):
        return símismo.ec_activa().verificar_activa(modelo, mód)

    def activar_ec(símismo, ec):
        try:
            obj_ec = símismo[ec]
        except KeyError:
            raise ValueError('Ecuación {ec} no existe por aquí.'.format(ec=ec))

        símismo._activada = obj_ec
        for rm in símismo._ramas.values():
            rm.activada = False

        obj_ec.activada = True

    def desactivar_ec(símismo):
        símismo.activar_ec('Nada')

    def ec_activa(símismo):
        return símismo._activada


class EcuaciónCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente, ramas, coso):
        super().__init__(cls_pariente, ramas, coso)
        símismo.activada = False

    def verificar_activa(símismo, modelo, mód):
        if símismo.activada and str(símismo) != 'Nada':
            inters = símismo.cls_pariente.inter()
            if inters:
                return all(mód.inter(modelo, símismo.coso, tipo=intr) for intr in inters)
            return True
        return False


class ParámCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente, coso):
        super().__init__(cls_pariente, ramas=[], coso=coso)

        símismo._calibs = {}  # type: Dict[str, MnjdrDists]
        símismo._apriori = MnjdrDists()

        símismo.líms = símismo.cls_pariente.líms
        símismo.inter = símismo.cls_pariente.inter

    def verificar_activa(símismo, modelo, mód):
        return True  # Parámetros de una ecuación activa siempre están activados.

    def agregar_calib(símismo, id_cal, dist, inter=None):
        if id_cal not in símismo._calibs:
            símismo._calibs[id_cal] = MnjdrDists()

        símismo._calibs[id_cal].actualizar(dist, inter)

    def borrar_calib(símismo, nombre):
        símismo._calibs.pop(nombre)

    def renombrar_calib(símismo, nombre, nuevo):
        símismo._calibs[nuevo] = símismo._calibs.pop(nombre)

    def espec_apriori(símismo, apriori, inter=None):
        dist = apriori.dist(símismo.líms)
        símismo._apriori.actualizar(dist=dist, índs=inter)

    def apriori(símismo, inter=None):
        return símismo._apriori.obt_val(inter)

    def calib_base(símismo):
        return DistAnalítica.de_líms(símismo.líms)

    def dists_disp(símismo, inter, heredar):
        return {clb: dists.obt_val(índs=inter, heredar=heredar) for clb, dists in símismo._calibs.items()}

    def a_dic(símismo):
        return {ll: v for ll, v in {nmb: clb.a_dic() for nmb, clb in símismo._calibs.items()}.items() if len(v)}

    def de_dic(símismo, dic):
        for calib, d_dist in dic.items():
            símismo._calibs[calib] = MnjdrDists.de_dic(
                d_dist, mnjdr=símismo._calibs[calib] if calib in símismo._calibs else None
            )

    def __copy__(símismo):
        return ParámCoso(símismo.cls_pariente, coso=símismo.coso)
