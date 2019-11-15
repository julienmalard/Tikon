from scipy.stats import uniform

from tikon.ecs.dists import Dist, DistAnalítica, MnjdrDists
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
        return []

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
        return []

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
