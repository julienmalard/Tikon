from scipy.stats import uniform
from tikon.ecs.aprioris import APrioriDist

from tikon.ecs.dists import Dist, DistAnalítica
from tikon.ecs.árb_coso import ParámGeneral
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

    def a_dic(símismo):
        dic = {ll: v.a_dic() for ll, v in símismo.items()}
        return {ll: v for ll, v in dic.items() if v}

    def de_dic(símismo, dic):
        for ll, d in dic.items():
            if ll in símismo:
                sub = símismo[ll]
            else:
                símismo[ll] = símismo._sub_cls(ll)
                sub = símismo[ll]
            sub.de_dic(d)

    def borrar_calib(símismo, nombre):
        for dato in símismo.values():
            dato.borrar_calib(nombre)

    def renombrar_calib(símismo, nombre, nuevo):
        for dato in símismo.values():
            dato.renombrar_calib(nombre, nuevo)

    def borrar_inic(símismo):
        for dato in símismo.values():
            dato.borrar_inic()

    @property
    def _sub_cls(símismo):
        raise NotImplementedError

    def __str__(símismo):
        return símismo.nombre


class DatosVar(PlantillaDatosVals):
    _sub_cls = None

    def __init__(símismo, nombre):
        símismo.obs = []
        símismo.prm = ParámGeneral(nombre, coso=None, líms=None, inter=None, apriori_auto=None)
        super().__init__(nombre)

    def agregar_obs(símismo, obs):
        símismo.obs.append(obs)

    def espec_inic(símismo, dist, índs=None):
        símismo.prm.espec_apriori(apriori=APrioriDist(dist), inter=índs)

    def borrar_inic(símismo):
        símismo.prm.borrar_aprioris()

    def a_dic(símismo):
        return símismo.prm.a_dic()

    def de_dic(símismo, dic):
        símismo.prm.de_dic(dic)

    def borrar_calib(símismo, nombre):
        símismo.prm.borrar_calib(nombre)

    def renombrar_calib(símismo, nombre, nuevo):
        símismo.prm.renombrar_calib(nombre, nuevo)

    def __iter__(símismo):
        for i in range(len(símismo.obs)):
            yield i

    def __getitem__(símismo, itema):
        return símismo.obs[itema]


class DatosMód(PlantillaDatosVals):
    _sub_cls = DatosVar

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


class DatosExper(PlantillaDatosVals):
    _sub_cls = DatosMód

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

    def cargar_calibs(símismo, archivo):
        símismo.de_dic(leer_json(archivo))

    def guardar_calibs(símismo, directorio):
        guardar_json(símismo.a_dic(), directorio)
