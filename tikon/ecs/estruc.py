from copy import deepcopy
from typing import Dict

from tikon.ecs.dists import DistAnalítica, DistCalib


class ÁrbolEcs(object):
    def __init__(símismo, nombre, categs=None):
        """

        Parameters
        ----------
        nombre: str
        categs: list[CategEc]

        """

        símismo.nombre = nombre

        if categs is None:
            categs = {}
        símismo.categs = {str(cat): cat for cat in categs}

    def agregar_categ(símismo, categ):
        símismo.categs[str(categ)] = categ

    def espec_apriori(símismo, categ, sub_categ, ec, parám, rango, certidumbre, índs=None):

        obj_parám = símismo.categs[categ][sub_categ][ec][parám]  # type: Parám
        obj_parám.espec_a_priori(rango, certidumbre, índs=índs)

    def activas(símismo):
        return [cat.activas() for cat in símismo.categs]

    def activar_ec(símismo, categ, subcateg, ec):
        símismo[categ].activar_ec(subcateg, ec)

    def leer(símismo, arch):
        pass

    def escribir(símismo, arch):
        pass

    def __getattr__(símismo, itema):
        return símismo.categs[itema]

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo))
        for cat in símismo.categs.values():
            copia.agregar_categ(cat.__copy__())
        return copia

    def __str__(símismo):
        return símismo.nombre


class CategEc(object):
    def __init__(símismo, nombre, subs=None):
        """

        Parameters
        ----------
        nombre
        subs
        """
        símismo.nombre = nombre

        if subs is None:
            subs = {}
        símismo.subcategs = {str(sub): sub for sub in subs}

    def agregar_subcateg(símismo, subcateg):
        símismo.subcategs[str(subcateg)] = subcateg

    def activas(símismo):
        return [sub.activa() for sub in símismo.subcategs]

    def activar_ec(símismo, subcateg, ec):
        símismo[subcateg].activar_ec(ec)

    def __getitem__(símismo, itema):
        return símismo.subcategs[itema]

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo))
        for sub in símismo.subcategs.values():
            copia.agregar_subcateg(sub.__copy__())
        return copia

    def __str__(símismo):
        return símismo.nombre


class SubCategEc(object):
    def __init__(símismo, nombre, ecs, activa=None):
        símismo.nombre = nombre
        if ecs is None:
            ecs = []
        símismo.ecs = {str(ec): ec for ec in ecs}
        símismo._activa = ''

        if activa is None:
            activa = ecs[0]
        símismo.activar_ec(activa)

    def activar_ec(símismo, ec):

        if ec not in símismo.ecs:
            raise ValueError(ec)

        símismo._activa = str(ec)

    def activa(símismo):
        return símismo.ecs[símismo._activa]

    def agregar_ec(símismo, ec):
        símismo.ecs[str(ec)] = ec

    def __getitem__(símismo, itema):
        try:
            return next(e for e in símismo.ecs if str(e) == itema)
        except StopIteration:
            raise KeyError(itema)

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo))
        for ec in símismo.ecs.values():
            copia.agregar_ec(ec.__copy__())
        return copia

    def __str__(símismo):
        return símismo.nombre


class Ecuación(object):
    def __init__(símismo, nombre, paráms=None, fun=None, ref=None, dscr=None):
        símismo.nombre = nombre
        símismo.ref = ref
        símismo.dscr = dscr
        símismo.fun = fun

        if paráms is None:
            paráms = {}
        símismo.paráms = {str(prm): prm for prm in paráms}

    def agregar_parám(símismo, parám):
        símismo.paráms[str(parám)] = parám

    def __call__(símismo, cf, paso, ):
        if símismo.fun is not None:
            return símismo.fun(cf, paso, matr_egr, **argspc)

    def __getitem__(símismo, itema):
        return símismo.paráms[itema]

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo))
        copia.ref = símismo.ref
        copia.dscr = símismo.dscr

        for prm in símismo.paráms.values():
            copia.agregar_parám(prm.__copy__())
        return copia

    def __str__(símismo):
        return símismo.nombre


class EcuaciónVacía(Ecuación):
    def __init__(símismo):
        super().__init__('Nada')


class Parám(object):
    def __init__(símismo, nombre, líms, inter=None, unids=None):
        símismo.nombre = nombre
        símismo.líms = líms
        símismo.inter = inter
        símismo.unids = unids

        símismo._calibs = {}  # type: Dict[str, MnjdrDists]
        símismo._a_priori = MnjdrDists()
        símismo._calib_activa = None  # type: MnjdrDistsClbs

    def agregar_calib(símismo, id_cal, dist, índs=None):
        if id_cal not in símismo._calibs:
            símismo._calibs[id_cal] = MnjdrDists()

        símismo._calibs[id_cal].actualizar(dist, índs)

    def estab_calib_activa(símismo, índs):
        if símismo._calib_activa is None:
            símismo._calib_activa = MnjdrDistsClbs()

        símismo._calib_activa.actualizar(índs)

    def espec_a_priori(símismo, rango, certidumbre, índs=None):

        dist = DistAnalítica.de_dens(dens=certidumbre, líms_dens=rango, líms=símismo.líms)
        if índs is None:
            símismo._a_priori.actualizar(dist=dist, índs=índs)

    def guardar_calib_activa(símismo, id_cal, í_trazas, pesos):

        símismo._calibs[id_cal] = símismo._calib_activa.obt_trazas(í_trazas, pesos)
        símismo._calib_activa = None

    def calib_base(símismo):
        return DistAnalítica.de_líms(símismo.líms)

    def obt_vals(símismo, n, calibs=None, índs=None):
        if isinstance(n, int):
            raise NotImplementedError
        else:
            raise NotImplementedError

    def a_priori(símismo, índs=None):
        return símismo._a_priori.obt_val(índs)

    def __copy__(símismo):
        return deepcopy(símismo)
        # copia = símismo.__class__(str(símismo), símismo.líms, símismo.inter, unids=símismo.unids)
        # copia.ecs = deepcopy(símismo.ecs)
        # copia.a_prioris = deepcopy(símismo.a_prioris)

    def __str__(símismo):
        return símismo.nombre


class MnjdrDists(object):
    def __init__(símismo):
        símismo.val = None
        símismo.índs = {}

    def actualizar(símismo, dist, índs=None):
        if isinstance(índs, str):
            índs = [índs]
        else:
            índs = list(índs)  # generar copia

        if índs is None or not len(índs):
            símismo.val = dist
        else:
            í = índs.pop(0)
            sub_dist = símismo.__class__()
            sub_dist.actualizar(dist, índs)
            símismo.índs[í] = sub_dist

    def obt_val(símismo, índs=None):

        if isinstance(índs, str):
            índs = [índs]
        else:
            índs = list(índs)  # generar copia

        if índs is None or not len(índs):
            return símismo.val
        else:
            í = índs.pop(0)
            if í in símismo.índs:
                return símismo.índs[í].obt_valor(índs)
            else:
                return símismo.val

    def __getitem__(símismo, itema):
        return símismo.índs[itema]


class MnjdrDistsClbs(MnjdrDists):

    def actualizar(símismo, dist, índs=None):
        if not isinstance(dist, DistCalib):
            raise TypeError
        super().actualizar(dist=dist, índs=índs)

    def obt_trazas(símismo, mnjdr=None):
        if mnjdr is None:
            mnjdr = MnjdrDists()
        mnjdr.actualizar(dist=símismo.val.gen_traza())

        for í, mnjdr_í in símismo.índs:
            mnjdr.actualizar(mnjdr_í.obt_trazas(mnjdr=mnjdr), índs=í)

        return mnjdr


class FuncEc(object):
    def __call__(self, cf, paso, módulo, matr_egr=None):
        raise NotImplementedError
