from copy import copy
from typing import Dict

from .dists import DistAnalítica, MnjdrDists


class PlantillaRamaEcCoso(dict):
    def __init__(símismo, pariente, ramas, coso):
        símismo.coso = coso
        símismo.nombre = pariente.nombre
        símismo.pariente = pariente
        super().__init__(**{str(r): r for r in ramas})

    def activa(símismo, modelo, mód, exper, coso):
        return coso.ecs_activas \
               and símismo.pariente.activa(modelo, mód, exper) \
               and any(símismo[rm].activa(modelo, mód, exper, coso) for rm in símismo)

    def de_dic(símismo, dic):
        for rm in símismo:
            if rm in dic:
                símismo[rm].de_dic(dic[rm])

    def borrar_calib(símismo, nombre):
        for rm in símismo:
            símismo[rm].borrar_calib(nombre)

    def borrar_aprioris(símismo, *args, índs=None):
        ramas = args[0] if len(args) else None
        if isinstance(ramas, str):
            ramas = [ramas]
        elif ramas is None:
            ramas = iter(símismo)

        for rm in ramas:
            símismo[rm].borrar_aprioris(*(args[1:] if len(args) > 1 else []), índs=índs)

    def renombrar_calib(símismo, nombre, nuevo):
        for rm in símismo:
            símismo[rm].renombrar_calib(nombre, nuevo)

    def a_dic(símismo):
        return {ll: v for ll, v in {nmb: rm.a_dic() for nmb, rm in símismo.items()}.items() if len(v)}

    def __contains__(símismo, itema):
        return str(itema) in símismo

    def __copy__(símismo):
        ramas = [copy(rm) for rm in símismo.values()]
        return símismo.__class__(símismo.nombre, ramas=ramas, coso=símismo.coso)

    def __str__(símismo):
        return símismo.nombre


class ÁrbolEcsCoso(PlantillaRamaEcCoso):

    def espec_apriori(símismo, apriori, categ, sub_categ, ec, parám, inter=None):
        obj_parám = símismo[categ][sub_categ][ec][parám]
        obj_parám.espec_apriori(apriori, inter=inter)

    def activar_ec(símismo, categ, subcateg, ec):
        símismo[categ].activar_ec(subcateg, ec)

    def desactivar_ec(símismo, categ, subcateg=None):
        símismo[categ].desactivar_ec(subcateg=subcateg)


class CategEcCoso(PlantillaRamaEcCoso):

    def activar_ec(símismo, subcateg, ec):
        símismo[subcateg].activar_ec(ec)

    def desactivar_ec(símismo, subcateg=None):
        if subcateg is None:
            subcateg = list(símismo)
        else:
            subcateg = [subcateg]
        for sub in subcateg:
            símismo[sub].desactivar_ec()


class SubcategEcCoso(PlantillaRamaEcCoso):
    def __init__(símismo, pariente, ramas, coso):
        super().__init__(pariente, ramas, coso)

        símismo._activada = ramas[0]

        símismo._activada.activada = True

    def activa(símismo, modelo, mód, exper, coso):
        return símismo.ec_activa().activa(modelo, mód, exper, coso)

    def activar_ec(símismo, ec):
        try:
            obj_ec = símismo[ec]
        except KeyError:
            raise ValueError('Ecuación {ec} no existe por aquí.'.format(ec=ec))

        símismo._activada = obj_ec
        for rm in símismo.values():
            rm.activada = False

        obj_ec.activada = True

    def desactivar_ec(símismo):
        símismo.activar_ec('Nada')

    def ec_activa(símismo):
        return símismo._activada


class EcuaciónCoso(PlantillaRamaEcCoso):
    def __init__(símismo, pariente, ramas, coso):
        super().__init__(pariente, ramas, coso)
        símismo.activada = False

    def activa(símismo, modelo, mód, exper, coso):
        if símismo.activada and símismo.pariente.activa(modelo, mód, exper):
            inters = símismo.inter()
            if inters:
                return all(mód.inter(modelo, símismo.coso, tipo=intr) for intr in inters)
            return True
        return False

    def inter(símismo):
        return {
            tuple(prm.inter) if isinstance(prm.inter, list) else (prm.inter,)
            for prm in símismo.values() if prm.inter is not None
        }


class ParámCoso(PlantillaRamaEcCoso):
    def __init__(símismo, pariente, coso):
        símismo.líms = pariente.líms
        símismo.inter = pariente.inter
        símismo.apriori_auto = pariente.apriori
        símismo._calibs = {}  # type: Dict[str, MnjdrDists]
        símismo._apriori = MnjdrDists()

        super().__init__(pariente, ramas=[], coso=coso)

    def activa(símismo, modelo, mód, exper, coso):
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

    def borrar_aprioris(símismo, *args, índs=None):
        if len(args):
            raise ValueError()
        símismo._apriori.borrar(índs)

    def apriori(símismo, heredar=True, inter=None):
        return símismo._apriori.obt_val(inter, heredar=heredar)

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
        return ParámCoso(símismo.nombre, símismo.coso)
