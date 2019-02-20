import os

from tikon.utils import guardar_json, jsonificar, leer_json


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

    def desactivar_ec(símismo, categ, subcateg=None):
        símismo.ecs.desactivar_ec(categ=categ, subcateg=subcateg)

    def categ_activa(símismo, categ, mód):
        return símismo.ecs[categ].verificar_activa(mód)

    def espec_apriori(símismo, apriori, categ, sub_categ, ec, prm, índs=None):
        símismo.ecs.espec_apriori(apriori, categ, sub_categ, ec, prm, índs=índs)

    def guardar_calib(símismo, directorio=''):
        arch = os.path.join(directorio, símismo.nombre + '.json')
        guardar_json(símismo._ecs_a_json(), arch)

    def _ecs_a_json(símismo):
        return jsonificar(símismo.ecs.a_dic())

    def borrar_calib(símismo, nombre):
        símismo.ecs.borrar_calib(nombre)

    def cargar_calib(símismo, archivo):
        if os.path.splitext(archivo) != '.json':
            archivo = os.path.join(archivo, símismo.nombre + '.json')
        calibs = leer_json(archivo)
        símismo._ecs_de_json(calibs)

    def _ecs_de_json(símismo, calibs):
        símismo.ecs.de_dic(calibs)

    def __str__(símismo):
        return símismo.nombre
