class Exper(object):
    def __init__(símismo):
        símismo.obs = MnjdrObsExper()
        símismo.controles = MnjdrControlesExper()

    def días(símismo):
        return símismo.obs.días()

    def f_inic(símismo):
        return símismo.obs.f_inic()

    def obt_control(símismo, var):
        return símismo.controles[var]

    def agregar_obs(símismo, obs, mód, var, coords):
        pass

    def obtener_obs(símismo, mód, var, coords):
        pass


_controles_auto = {
    'parcelas': ['1'],
    'superficies': [1.]
}


class MnjdrControlesExper(object):
    def __init__(símismo):
        símismo.d_vals = _controles_auto

    def __getitem__(símismo, itema):
        return símismo.d_vals[itema]


class MnjdrObsExper(object):
    def f_inic(símismo):
        pass


class Observación(object):
    pass
