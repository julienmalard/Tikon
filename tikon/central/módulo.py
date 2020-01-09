import os

from tikon.central.coso import Coso


class Módulo(object):
    cls_ecs = None
    eje_coso = None

    def __init__(símismo, cosos=None):

        cosos = cosos or []
        if isinstance(cosos, Coso):
            cosos = [cosos]

        símismo._cosos = {str(c): c for c in cosos}
        if len(símismo._cosos) != len(cosos):
            raise ValueError('Nombres duplicados en {}.'.format(', '.join(cosos)))

    def gen_ecs(símismo, modelo, mód, exper, n_reps):
        if símismo.cls_ecs:
            return símismo.cls_ecs(modelo, mód, exper, cosos=list(símismo._cosos.values()), n_reps=n_reps)

    def guardar_calibs(símismo, directorio=''):
        for c in símismo:
            símismo[c].guardar_calibs(os.path.join(directorio, c))

    def cargar_calibs(símismo, directorio=''):
        for c in símismo:
            símismo[c].cargar_calibs(os.path.join(directorio, c))

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        return símismo.cls_simul(mód=símismo, simul_exper=simul_exper, vars_interés=vars_interés, ecs=ecs)

    def borrar_aprioris(símismo):
        for c in símismo:
            símismo[c].borrar_aprioris()

    def inter(símismo, modelo, coso, tipo):
        raise ValueError('Interacciones no implementadas para módulo "{mód}".'.format(mód=símismo))

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def cls_simul(símismo):
        raise NotImplementedError

    def __contains__(símismo, itema):
        return itema in símismo._cosos.values() or itema in símismo._cosos

    def __getitem__(símismo, itema):
        return símismo._cosos[itema]

    def __iter__(símismo):
        for c in símismo._cosos:
            yield c

    def __str__(símismo):
        return símismo.nombre
