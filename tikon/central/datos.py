from scipy.stats import uniform

from tikon.ecs.dists import Dist, DistAnalítica, MnjdrDists
from tikon.ecs.paráms import ValsParámCoso
from tikon.ecs.árb_mód import Parám
from tikon.result import Obs
from tikon.utils import guardar_json, leer_json


class PlantillaDatosVals(dict):

    def __init__(símismo, nombre):
        símismo.nombre = nombre
        super().__init__()

    def fechas(símismo):
        f_inic = f_final = None
        for dato in símismo:
            otra_inic, otra_final = símismo[dato].fechas()
            if (otra_inic is not None) and (f_inic is not None):
                f_inic = min(otra_inic, f_inic)
            else:
                f_inic = f_inic or otra_inic
            if (otra_final is not None) and (f_final is not None):
                f_final = max(otra_final, f_final)
            else:
                f_final = f_final or otra_final

        return f_inic, f_final


class DatosExper(PlantillaDatosVals):

    def agregar_obs(símismo, obs):
        if isinstance(obs, Obs):
            obs = [obs]
        for o_ in obs:
            if o_.mód not in símismo:
                símismo[o_.mód] = DatosMód(o_.mód)
            símismo[o_.mód].agregar_obs(o_)

    def espec_inic(símismo, dist, mód, var, índs=None):
        if not isinstance(dist, Dist):
            dist = DistAnalítica(uniform(dist, 0))

        mód, var = str(mód), str(var)
        if mód not in símismo:
            símismo[mód] = DatosMód(mód)
        símismo[mód].espec_inic(dist, var, índs=índs)

    def obt_obs(símismo, mód, var):
        mód, var = str(mód), str(var)
        if mód in símismo:
            return símismo[mód].obt_obs(var)

    def obt_inic(símismo, mód, var, índs):
        mód, var = str(mód), str(var)
        if mód in símismo:
            return símismo[mód].obt_inic(var, índs=índs)

    def gen_paráms(símismo, mód, obj_res):
        if mód not in símismo:
            símismo[mód] = DatosMód(mód)
        símismo[mód].gen_paráms(obj_res)

    def cargar_calib(símismo, archivo):
        símismo.de_dic(leer_json(archivo))

    def guardar_calib(símismo, directorio):
        guardar_json(símismo.a_dic(), directorio)


class DatosMód(PlantillaDatosVals):

    def agregar_obs(símismo, obs):
        if obs.var not in símismo:
            símismo[obs.var] = DatosVar(obs.var)
        símismo[obs.var].agregar_obs(obs)

    def espec_inic(símismo, dist, var, índs=None):
        if var not in símismo:
            símismo[var] = DatosVar(var)
        símismo[var].espec_inic(dist, índs=índs)

    def obt_obs(símismo, var):
        if var in símismo:
            return símismo[var].obs

    def obt_inic(símismo, var, índs):
        if var in símismo:
            return símismo[var].dists.obt_val(índs, heredar=True)

    def gen_paráms(símismo, obj_res):
        var = obj_res.nombre
        if var not in símismo:
            símismo[var] = DatosVar(var)
        símismo[var].gen_paráms(obj_res)


class DatosVar(PlantillaDatosVals):
    def __init__(símismo, nombre):
        símismo.obs = []
        símismo.dists = MnjdrDists()
        super().__init__(nombre)

    def agregar_obs(símismo, obs):
        símismo.obs.append(obs)

    def espec_inic(símismo, dist, índs=None):
        símismo.dists.actualizar(dist, índs=índs)

    def __iter__(símismo):
        for i in range(len(símismo.obs)):
            yield i

    def __getitem__(símismo, itema):
        return símismo.obs[itema]


class MnjdrInicExper(object):
    # para hacer: ¿combinar con MnjdrObsExper?
    def __init__(símismo):
        símismo._inic = {}

    def agregar_prm(símismo, mód, var, índs, prm_base):
        return símismo[mód].agregar_prm(var, índs, prm_base)

    def vals_paráms(símismo):
        return [vl for m in símismo for vl in símismo[m].vals_paráms()]


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
                dist = Dist.de_dic(v['val'])
                obj_val.prm_base.agregar_calib(ll, dist)


class ParámInic:
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
