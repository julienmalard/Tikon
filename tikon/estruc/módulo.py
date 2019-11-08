import os

from tikon.estruc.coso import Coso


class Módulo(object):

    def __init__(símismo, cosos=None):

        cosos = cosos or []
        if isinstance(cosos, Coso):
            cosos = [cosos]

        símismo._cosos = {str(c): c for c in cosos}

    def gen_ecs(símismo, n_reps):
        pass

    def guardar_calibs(símismo, directorio=''):
        for c in símismo:
            símismo[c].guardar_calibs(os.path.join(directorio, c.nombre))

    def cargar_calib(símismo, directorio=''):
        for c in símismo:
            símismo[c].cargar_calibs(os.path.join(directorio, c.nombre))

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        símismo.cls_simul(mód=símismo, simul_exper=simul_exper, vars_interés=vars_interés, ecs=ecs)

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def cls_simul(símismo):
        raise NotImplementedError

    def __getitem__(símismo, itema):
        return símismo._cosos[itema]

    def __iter__(símismo):
        for c in símismo._cosos:
            yield c

    def __str__(símismo):
        return símismo.nombre
