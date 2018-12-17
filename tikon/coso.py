class Coso(object):

    def __init__(símismo, nombre, ecs):
        símismo.nombre = nombre
        símismo.ecs = ecs.para_coso(coso=símismo)

    def activar_ec(símismo, categ, subcateg, ec, **argspc):
        símismo.ecs.activar_ec(categ, subcateg, ec)

    def activar_ecs(símismo, dic_ecs):
        for categ, d_cat in dic_ecs.items():
            for sub, ec in d_cat.items():
                símismo.activar_ec(categ, sub, ec)

    def categ_activa(símismo, categ, mód):
        return símismo.ecs[categ].verificar_activa(mód)

    def espec_apriori(símismo, apriori, categ, sub_categ, ec, prm, índs=None):
        símismo.ecs.espec_apriori(apriori, categ, sub_categ, ec, prm, índs=índs)

    def __str__(símismo):
        return símismo.nombre
