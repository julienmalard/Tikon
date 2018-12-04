class Coso(object):

    def __init__(símismo, nombre, ecs):
        símismo.nombre = nombre
        símismo.ecs = ecs()

    def activar_ec(símismo, categ, subcateg, ec, **argspc):
        símismo.ecs.activar_ec(categ, subcateg, ec)

    def activar_ecs(símismo, dic_ecs):
        for categ, d_cat in dic_ecs.items():
            for sub, ec in d_cat.items():
                símismo.activar_ec(categ, sub, ec)

    def paráms(símismo):
        return símismo.ecs.paráms()

    def verificar_activa(símismo, cls_base_ec):
        return símismo.ecs.verificar_activa(cls_base_ec)

    def espec_apriori(símismo, categ, sub_categ, ec, parám, rango, certidumbre, índs=None):
        símismo.ecs.espec_apriori(categ, sub_categ, ec, parám, rango, certidumbre, índs=índs)

    def __str__(símismo):
        return símismo.nombre
