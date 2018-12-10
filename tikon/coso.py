class Coso(object):

    def __init__(símismo, nombre, ecs):
        símismo.nombre = nombre
        símismo.ecs = ecs.para_coso()

    def activar_ec(símismo, categ, subcateg, ec, **argspc):
        símismo.ecs.activar_ec(categ, subcateg, ec)

    def activar_ecs(símismo, dic_ecs):
        for categ, d_cat in dic_ecs.items():
            for sub, ec in d_cat.items():
                símismo.activar_ec(categ, sub, ec)

    def paráms(símismo):
        return símismo.ecs.paráms()

    def categ_activa(símismo, categ):
        return símismo.ecs[categ].verificar_activa()

    def espec_apriori(símismo, apriori, categ, sub_categ, ec, índs=None):
        símismo.ecs.espec_apriori(apriori, categ, sub_categ, ec, índs=índs)

    def __str__(símismo):
        return símismo.nombre
