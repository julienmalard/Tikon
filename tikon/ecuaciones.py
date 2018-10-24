class ÁrbolEcs(object):
    def __init__(símismo, nombre, categs):
        símismo.nombre = nombre
        símismo.categs = categs

    def __str__(símismo):
        return símismo.nombre


class CategEc(object):
    def __init__(símismo, nombre, subcategs):
        símismo.nombre = nombre
        símismo.subcategs = subcategs

    def __str__(símismo):
        return símismo.nombre


class SubCategEc(object):
    def __init__(símismo, nombre, ecs):
        símismo.nombre = nombre
        símismo.ecs = ecs

    def __str__(símismo):
        return símismo.nombre


class Ecuación(object):

    def __init__(símismo, nombre, paráms):
        símismo.nombre = nombre
        símismo.paráms = paráms

    def eval(símismo, ):
        raise NotImplementedError

    def __str__(símismo):
        return símismo.nombre


class Parám(object):
    def __init__(símismo, nombre, líms, inter=None):
        símismo.nombre = nombre
        símismo.líms = líms
        símismo.inter = inter

    def __str__(símismo):
        return símismo.nombre