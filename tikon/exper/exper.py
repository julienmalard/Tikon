import numpy as np


class Exper(object):
    def __init__(símismo):
        símismo.obs = MnjdrObsExper()
        símismo.controles = MnjdrControlesExper()

    def n_días(símismo):
        return símismo.obs.n_días(símismo.f_inic())

    def f_inic(símismo):
        return símismo.obs.f_inic()

    def obt_control(símismo, var):
        return símismo.controles[var]

    def obt_inic(símismo, mód, var):
        try:
            mód = símismo.obs[mód]
        except KeyError:
            return
        return mód.obt_inic(var)

    def agregar_obs(símismo, obs):
        símismo.obs.agregar_obs(obs)

    def obtener_obs(símismo, mód, var=None):
        if var:
            return símismo.obs[mód][var]
        return símismo.obs[mód]


_controles_auto = {  # para hacer: más bonito
    'parcelas': ['1'],
    'superficies': np.array([1.])
}


class MnjdrControlesExper(object):
    def __init__(símismo):
        símismo.d_vals = _controles_auto

    def __getitem__(símismo, itema):
        return símismo.d_vals[itema]


class MnjdrObsExper(object):
    def __init__(símismo):
        símismo._obs = {}

    def agregar_obs(símismo, obs):
        mód = str(obs.mód)
        if mód not in símismo._obs:
            símismo._obs[mód] = MnjdrObsMód()
        símismo._obs[mód].agregar_obs(obs, obs.var)

    def f_inic(símismo):
        fechas = [f for f in [obs.f_inic() for obs in símismo] if f]
        if fechas:
            return min(fechas)

    def n_días(símismo, f_inic):
        días = [f for f in [obs.n_días(f_inic) for obs in símismo] if f]
        if días:
            return max(días)

    def __iter__(símismo):
        for obs in símismo._obs.values():
            yield obs

    def __getitem__(símismo, itema):
        return símismo._obs[str(itema)]


class MnjdrObsMód(object):
    def __init__(símismo):
        símismo._obs = {}

    def agregar_obs(símismo, obs, var):
        símismo._obs[var] = obs

    def f_inic(símismo):
        try:
            min([f for f in [obs.f_inic() for obs in símismo] if f])
        except ValueError:
            return None

    def n_días(símismo, f_inic):
        return max([obs.n_días(f_inic) for obs in símismo])

    def obt_inic(símismo, var):
        try:
            return símismo[var]
        except KeyError:
            return

    def __contains__(símismo, itema):
        return itema in símismo._obs

    def __iter__(símismo):
        for obs in símismo._obs.values():
            yield obs

    def __getitem__(símismo, itema):
        return símismo._obs[str(itema)]
