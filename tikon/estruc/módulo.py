class Módulo(object):
    nombre = NotImplemented

    def gen_ecs(símismo, n_reps):
        pass

    def guardar_calibs(símismo, directorio=''):
        pass  # para hacer: genérico

    def cargar_calib(símismo, directorio=''):
        pass  # para hacer: genérico

    def requísitos(símismo, controles=False):
        raise NotImplementedError

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        raise NotImplementedError

    def __str__(símismo):
        return símismo.nombre
