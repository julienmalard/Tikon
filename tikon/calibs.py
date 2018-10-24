from copy import deepcopy

ID_NO_INFORM = '0'


class ÁrbolEcs(object):
    def __init__(símismo, nombre, categs=None):
        símismo.nombre = nombre

        categs = set(categs) if categs is not None else set()

        símismo.categs = categs

    def agregar_categ(símismo, categ):
        símismo.categs.add(categ)

    def __getitem__(símismo, itema):
        try:
            return next(c for c in símismo.categs if str(c) == itema)
        except StopIteration:
            raise KeyError(itema)

    def espec_apriori(símismo, categ, sub_categ, ec, parám, rango, certidumbre, índs=None):
        pass

    def leer(símismo, arch):
        pass

    def escribir(símismo, arch):
        pass

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo))
        for cat in símismo.categs:
            copia.agregar_categ(cat.__copy__())
        return copia

    def __str__(símismo):
        return símismo.nombre


class CategEc(object):
    def __init__(símismo, nombre, subs=None):
        símismo.nombre = nombre
        símismo.subcategs = set(subs) if subs is not None else set()

    def agregar_subcateg(símismo, subcateg):
        símismo.subcategs.add(subcateg)

    def __getitem__(símismo, itema):
        try:
            return next(s for s in símismo.subcategs if str(s) == itema)
        except StopIteration:
            raise KeyError(itema)

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo))
        for sub in símismo.subcategs:
            copia.agregar_subcateg(sub.__copy__())
        return copia

    def __str__(símismo):
        return símismo.nombre


class SubCategEc(object):
    def __init__(símismo, nombre, ecs=None):
        símismo.nombre = nombre
        símismo.ecs = set(ecs) if ecs is not None else set()

    def agregar_ec(símismo, ec):
        símismo.ecs.add(ec)

    def __getitem__(símismo, itema):
        try:
            return next(e for e in símismo.ecs if str(e) == itema)
        except StopIteration:
            raise KeyError(itema)

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo))
        for ec in símismo.ecs:
            copia.agregar_ec(ec.__copy__())
        return copia

    def __str__(símismo):
        return símismo.nombre


class Ecuación(object):
    def __init__(símismo, nombre, paráms=None):
        símismo.nombre = nombre

        símismo.paráms = set(paráms) if paráms is not None else set()

    def agregar_parám(símismo, parám):
        símismo.paráms.add(parám)

    def __getitem__(símismo, itema):
        try:
            return next(p for p in símismo.paráms if str(p) == itema)
        except StopIteration:
            raise KeyError(itema)

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo))
        for prm in símismo.paráms:
            copia.agregar_parám(prm.__copy__())
        return copia

    def __str__(símismo):
        return símismo.nombre


class Parám(object):
    def __init__(símismo, nombre, líms, inter=None):
        símismo.nombre = nombre
        símismo.líms = líms
        símismo.inter = inter

        símismo.calibs = {}
        símismo.calibs_inter = {}

        símismo.agregar_calib(id_cal=ID_NO_INFORM, val=símismo.líms)

    def agregar_calib(símismo, id_cal, val, inter=None):
        if inter is None:
            símismo.calibs[id_cal] = val
        else:
            if inter not in símismo.calibs_inter:
                símismo.calibs_inter[inter] = {}

            símismo.calibs_inter[inter][id_cal] = [val]

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo), símismo.líms, símismo.inter)
        copia.calibs = deepcopy(símismo.calibs)
        copia.calibs_inter = deepcopy(símismo.calibs_inter)

    def __str__(símismo):
        return símismo.nombre

