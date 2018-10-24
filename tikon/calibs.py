from copy import deepcopy

ID_NO_INFORM = '0'


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
        obj_parám.agregar_a_priori(rango, certidumbre, índs=índs)

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
    def __init__(símismo, nombre, ecs=None):
        símismo.nombre = nombre
        if ecs is None:
            ecs = {}
        símismo.ecs = {str(ec): ec for ec in ecs}

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
        símismo.dscr=dscr
        símismo.fun = fun

        if paráms is None:
            paráms = {}
        símismo.paráms = {str(prm): prm for prm in paráms}

    def agregar_parám(símismo, parám):
        símismo.paráms[str(parám)] = parám

    def __call__(símismo, cf, paso, matr_egr=None, **argspc):
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



class Parám(object):
    def __init__(símismo, nombre, líms, inter=None, unids=None):
        símismo.nombre = nombre
        símismo.líms = líms
        símismo.inter = inter

        símismo.calibs = {}
        símismo.a_prioris = {}

        símismo.agregar_calib(id_cal=ID_NO_INFORM, val=símismo.líms)

    def agregar_calib(símismo, id_cal, val, índs=None):

        if id_cal not in símismo.calibs:
            símismo.calibs[id_cal] = {}

        if inter is None:
            símismo.calibs[id_cal]['val'] = val
        else:
            símismo.calibs[id_cal][]
        if inter not in símismo.calibs_inter:
                símismo.calibs_inter[inter] = {}

            símismo.calibs_inter[inter][id_cal] = [val]

    def agregar_a_priori(símismo, rango, certidumbre, índs=None):
        if inter is None:
            símismo.a_prioris =

    def __copy__(símismo):
        copia = símismo.__class__(str(símismo), símismo.líms, símismo.inter)
        copia.calibs = deepcopy(símismo.calibs)
        copia.calibs_inter = deepcopy(símismo.calibs_inter)

    def __str__(símismo):
        return símismo.nombre
