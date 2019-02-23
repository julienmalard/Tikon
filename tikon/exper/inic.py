from tikon.ecs.árb_coso import ParámCoso


class MnjdrInicExper(object):
    # para hacer: ¿combinar con MnjdrObsExper?
    def __init__(símismo):
        símismo._inic = {}

    def agregar_prm(símismo, mód, var, índs, prm_base):
        símismo[mód].agregar_prm(var, índs, prm_base)

    def vals_paráms(símismo):
        return [vl for m in símismo._inic.values() for vl in m.vals_paráms()]

    def __getitem__(símismo, itema):
        return símismo._inic[str(itema)]


class MnjdrInicMód(object):
    def __init__(símismo):
        símismo._inic = {}

    def vals_paráms(símismo):
        return [vl for vr in símismo._inic.values() for vl in vr.vals_paráms()]

    def agregar_prm(símismo, var, índs, prm_base):
        símismo[var].agregar_prm(índs, prm_base)

    def obt_inic(símismo, var):
        try:
            inic_var = símismo[var]
        except KeyError:
            inic_var = MnjdrInicVar(var)
            símismo._inic[var] = inic_var

        return inic_var

    def __getitem__(símismo, itema):
        return símismo._inic[str(itema)]


class ParámInic():
    def __init__(símismo, índs, prm_base):
        símismo.índs = índs
        símismo.prm_base = prm_base


class MnjdrInicVar(object):
    def __init__(símismo, var):
        símismo.var = var
        símismo.vals = set()

    def agregar_prm(símismo, índs, prm_base):
        símismo.vals.add(ParámInic(índs, prm_base))

    def __iter__(símismo):
        for v in símismo.vals:
            yield v


class ValInic(object):
    def __init__(símismo, dims):
        símismo.dims = dims

    def valor(símismo):
        raise NotImplementedError
