from tikon.ecs.paráms import ValsParámCoso
from tikon.ecs.árb_coso import ParámCoso
from tikon.utils import guardar_json


class MnjdrInicExper(object):
    # para hacer: ¿combinar con MnjdrObsExper?
    def __init__(símismo):
        símismo._inic = {}

    def agregar_prm(símismo, mód, var, índs, prm_base, tmñ):
        símismo[mód].agregar_prm(var, índs, prm_base, tmñ)

    def vals_paráms(símismo):
        return [vl for m in símismo for vl in m[1].vals_paráms()]

    def guardar_calib(símismo, directorio):
        dic_calib = símismo._calib_a_dic()
        guardar_json(dic_calib, directorio)

    def _calib_a_dic(símismo):
        return {m[0]: m[1].dic_calib() for m in símismo}

    def __getitem__(símismo, itema):
        return símismo._inic[str(itema)]

    def __iter__(símismo):
        for m in símismo._inic.items():
            yield m


class MnjdrInicMód(object):
    def __init__(símismo):
        símismo._inic = {}

    def vals_paráms(símismo):
        return [vl for vr in símismo._inic.values() for vl in vr.vals_paráms()]

    def agregar_prm(símismo, var, índs, prm_base, tmñ):
        símismo[var].agregar_prm(índs, prm_base, tmñ)

    def obt_inic(símismo, var):
        try:
            inic_var = símismo[var]
        except KeyError:
            inic_var = MnjdrInicVar(var)
            símismo._inic[var] = inic_var

        return inic_var

    def dic_calib(símismo):
        return {vr[0]: vr[1].dic_calib() for vr in símismo}

    def __getitem__(símismo, itema):
        return símismo._inic[str(itema)]

    def __iter__(símismo):
        for vr in símismo._inic.values():
            return vr


class ParámInic():
    def __init__(símismo, índs, prm_base, tmñ):
        símismo.índs = índs
        símismo.prm_base = prm_base
        símismo.vals_prm = ValsParámCoso(tmñ=tmñ, prm_base=símismo.prm_base)

    def vals_parám(símismo):
        return símismo.vals_prm

    def valor(símismo):
        return símismo.vals_prm.val()



class MnjdrInicVar(object):
    def __init__(símismo, var):
        símismo.var = var
        símismo.vals = set()

    def agregar_prm(símismo, índs, prm_base, tmñ):
        símismo.vals.add(ParámInic(índs, prm_base, tmñ=tmñ))

    def vals_paráms(símismo):
        return [v.vals_parám() for v in símismo]

    def __iter__(símismo):
        for v in símismo.vals:
            yield v
