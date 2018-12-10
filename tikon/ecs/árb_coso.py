from typing import Dict

from .dists import DistAnalítica, MnjdrDists, MnjdrDistsClbs


class PlantillaRamaEcCoso(object):
    def __init__(símismo, cls_pariente, ramas):
        símismo.cls_pariente = cls_pariente
        símismo._ramas = {str(r): r for r in ramas}

    def paráms(símismo):
        return [pr for rm in símismo for pr in rm.paráms()]

    def verificar_activa(símismo):
        return any(rm.verificar_activa() for rm in símismo)

    def __getitem__(símismo, itema):
        return símismo._ramas[str(itema)]

    def __iter__(símismo):
        for rm in símismo._ramas.values():
            yield rm

    def __contains__(símismo, itema):
        return str(itema) in símismo._ramas

    def __eq__(símismo, otro):
        return símismo.cls_pariente == otro

    def __str__(símismo):
        return str(símismo.cls_pariente.nombre)


class ÁrbolEcsCoso(PlantillaRamaEcCoso):

    def espec_apriori(símismo, apriori, categ, sub_categ, ec, parám, índs=None):
        obj_parám = símismo._ramas[categ][sub_categ][ec][parám]
        obj_parám.espec_a_priori(apriori, índs=índs)

    def activar_ec(símismo, categ, subcateg, ec):
        símismo[categ][subcateg].activar_ec(ec)

    def leer(símismo, arch):
        pass

    def escribir(símismo, arch):
        pass


class CategEcCoso(PlantillaRamaEcCoso):

    def activar_ec(símismo, subcateg, ec):
        símismo[subcateg].activar_ec(ec)


class SubcategEcCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente, ramas):
        super().__init__(cls_pariente, ramas)

        if cls_pariente.auto is not None:
            símismo._activada = next(ec for ec in símismo if ec.cls_pariente is cls_pariente.auto)
        else:
            símismo._activada = ramas[0]

    def verificar_activa(símismo, cls_base_ec=None):
        from .árb_mód import EcuaciónVacía
        return not símismo.ec_activa() == EcuaciónVacía

    def activar_ec(símismo, ec):
        try:
            símismo._activada = símismo[ec]
        except KeyError:
            raise ValueError(ec)

    def ec_activa(símismo):
        return símismo._activada


class EcuaciónCoso(PlantillaRamaEcCoso):
    pass


class ParámCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente):

        super().__init__(cls_pariente, ramas=[])

        símismo._calibs = {}  # type: Dict[str, MnjdrDists]
        símismo._a_priori = MnjdrDists()
        símismo._calib_activa = None  # type: MnjdrDistsClbs

        símismo.líms = símismo.cls_pariente.líms

    def paráms(símismo):
        return símismo

    def agregar_calib(símismo, id_cal, dist, índs=None):
        if id_cal not in símismo._calibs:
            símismo._calibs[id_cal] = MnjdrDists()

        símismo._calibs[id_cal].actualizar(dist, índs)

    def espec_a_priori(símismo, apriori, índs=None):

        dist = apriori.dist(símismo.líms)
        # para hacer
        if índs is None:
            símismo._a_priori.actualizar(dist=dist, índs=índs)

    def estab_calib_activa(símismo, índs):
        # para hacer
        if símismo._calib_activa is None:
            símismo._calib_activa = MnjdrDistsClbs()

        símismo._calib_activa.actualizar(índs)

    def guardar_calib_activa(símismo, id_cal, í_trazas, pesos):

        símismo._calibs[id_cal] = símismo._calib_activa.obt_trazas(í_trazas, pesos)
        símismo._calib_activa = None

    def a_priori(símismo, índs=None):
        return símismo._a_priori.obt_val(índs)

    def calib_base(símismo):
        return DistAnalítica.de_líms(símismo.líms)
