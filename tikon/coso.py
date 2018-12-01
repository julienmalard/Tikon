from copy import copy


class Coso(object):

    def __init__(símismo, nombre, ecs):
        símismo.nombre = nombre
        símismo.ecs = copy(ecs)

    def activar_ec(símismo, categ, subcateg, ec, **argspc):
        símismo.ecs.activar_ec(categ, subcateg, ec)

    def activar_ecs(símismo, dic_ecs):
        for categ, d_cat in dic_ecs.items():
            for sub, ec in d_cat.items():
                símismo.activar_ec(categ, sub, ec)

    def obt_ec_activa(símismo, categ, subcateg):
        return símismo.ecs[categ][subcateg]

    def espec_apriori(símismo):
        símismo.ecs.espec_apriori()

    def __str__(símismo):
        return símismo.nombre
