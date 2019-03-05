from tikon.ecs.dists import Dist
from tikon.ecs.paráms import ValsParámCoso
from tikon.ecs.árb_mód import Parám
from tikon.utils import guardar_json, leer_json


class MnjdrInicExper(object):
    # para hacer: ¿combinar con MnjdrObsExper?
    def __init__(símismo):
        símismo._inic = {}

    def agregar_prm(símismo, mód, var, índs, prm_base):
        return símismo[mód].agregar_prm(var, índs, prm_base)

    def vals_paráms(símismo):
        return [vl for m in símismo for vl in símismo[m].vals_paráms()]

    def agregar_mód(símismo, mód):
        símismo._inic[str(mód)] = MnjdrInicMód()
        return símismo[mód]

    def guardar_calib(símismo, directorio):
        dic_calib = símismo._calib_a_dic()
        guardar_json(dic_calib, directorio)

    def _calib_a_dic(símismo):
        return {m: símismo[m].a_dic() for m in símismo}

    def __getitem__(símismo, itema):
        return símismo._inic[str(itema)]

    def __iter__(símismo):
        for m in símismo._inic:
            yield m

    def cargar_calib(símismo, archivo):
        d_calib = leer_json(archivo)
        for m, dic in d_calib.items():
            try:
                mód = símismo[m]
            except KeyError:
                símismo.agregar_mód(m)
                mód = símismo[m]
            mód.de_dic(dic)


class MnjdrInicMód(object):
    def __init__(símismo):
        símismo._inic = {}

    def vals_paráms(símismo):
        return [vl for vr in símismo._inic.values() for vl in vr.vals_paráms()]

    def agregar_prm(símismo, var, índs, prm_base):
        return símismo[var].agregar_prm(índs, prm_base)

    def obt_inic(símismo, var):
        try:
            inic_var = símismo[var]
        except KeyError:
            inic_var = MnjdrInicVar(var)
            símismo._inic[var] = inic_var

        return inic_var

    def a_dic(símismo):
        return {vr[0]: vr[1].a_dic() for vr in símismo}

    def de_dic(símismo, dic):
        for vr, d in dic.items():
            if vr in símismo:
                obj_var = símismo[vr]
            else:
                obj_var = MnjdrInicVar(vr)
                símismo._inic[vr] = obj_var
            obj_var.de_dic(d)

    def __getitem__(símismo, itema):
        return símismo._inic[str(itema)]

    def __iter__(símismo):
        for vr in símismo._inic.items():
            yield vr


class ParámInic():
    def __init__(símismo, índs, prm_base):
        símismo.índs = índs
        símismo.prm_base = prm_base
        símismo.vals_prm = None  # type: ValsParámCoso

    def vals_parám(símismo):
        return símismo.vals_prm

    def iniciar_prm(símismo, tmñ):
        símismo.vals_prm = ValsParámCoso(tmñ=tmñ, prm_base=símismo.prm_base)

    def valor(símismo):
        return símismo.vals_prm.val()

    def a_dic(símismo):
        return {'val': símismo.prm_base.a_dic(), 'índs': {ll: str(v) for ll, v in símismo.índs.items()}}


class MnjdrInicVar(object):
    def __init__(símismo, var):
        símismo.var = var
        símismo.vals = set()

    def agregar_prm(símismo, índs, prm_base):
        prm = ParámInic(índs, prm_base)
        símismo.vals.add(prm)
        return prm

    def vals_paráms(símismo):
        return [v.vals_parám() for v in símismo]

    def obt_val(símismo, índs):
        for v in símismo:
            if v.índs == índs:
                return v
        raise KeyError(índs)

    def a_dic(símismo):
        return {str(í): vr.a_dic() for í, vr in enumerate(símismo)}

    def de_dic(símismo, dic):
        for d_vls in dic.values():
            índs = d_vls['índs']
            val = d_vls['val']
            try:
                obj_val = símismo.obt_val(índs)
            except KeyError:
                class prm(Parám):
                    nombre = 'inic'
                    líms = (0, None)

                obj_val = símismo.agregar_prm(índs, prm.para_coso(None))

            for ll, v in val.items():
                dist = Dist.gen_dist(v['val'])
                obj_val.prm_base.agregar_calib(ll, dist)



    def __iter__(símismo):
        for v in símismo.vals:
            yield v
