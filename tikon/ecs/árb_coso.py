from typing import Dict

from .dists import DistAnalítica, MnjdrDists
from .paráms import MatrParámCoso, ValsParámCoso, ValsParámCosoInter


class PlantillaRamaEcCoso(object):
    def __init__(símismo, cls_pariente, ramas):
        símismo.cls_pariente = cls_pariente
        símismo._ramas = {str(r): r for r in ramas}

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
        obj_parám.espec_a_priori(apriori, inter=índs)

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

        símismo._activada.activada = True

    def verificar_activa(símismo):
        from .árb_mód import EcuaciónVacía
        return símismo.ec_activa() != EcuaciónVacía

    def activar_ec(símismo, ec):
        try:
            obj_ec = símismo[ec]
            símismo._activada = obj_ec
            for rm in símismo._ramas.values():
                rm.activada = False

            obj_ec.activada = True

        except KeyError:
            raise ValueError(ec)

    def ec_activa(símismo):
        return símismo._activada


class EcuaciónCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente, ramas):
        super().__init__(cls_pariente, ramas)
        símismo.activada = False

    def verificar_activa(símismo):
        return símismo.activada


class ParámCoso(PlantillaRamaEcCoso):
    def __init__(símismo, cls_pariente):

        super().__init__(cls_pariente, ramas=[])

        símismo._calibs = {}  # type: Dict[str, MnjdrDists]
        símismo._a_priori = MnjdrDists()
        símismo._vals_activos = NotImplemented

        símismo.líms = símismo.cls_pariente.líms
        símismo.inter = símismo.cls_pariente.inter
        símismo.mód = símismo.cls_pariente.mód

    def verificar_activa(símismo):
        return True  # Parámetros de una ecuación activa siempre están activados.

    def obt_inter(símismo):
        if símismo.inter is not None:
            return símismo.mód.inter(símismo.inter)

    def gen_matr_parám(símismo, n_rep):
        inters = símismo.obt_inter()
        if inters is None:
            vals = ValsParámCoso(tmñ=n_rep, prm_base=símismo)
        else:
            vals = ValsParámCosoInter({
                í: ValsParámCoso(tmñ=n_rep, prm_base=símismo, inter=inter)
                for í, inter in inters
            }, tmñ_inter=inters.tmñ)

        return MatrParámCoso(vals)

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
