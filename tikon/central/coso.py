import os

from tikon.utils import guardar_json, leer_json


class Coso(object):
    ecs_activas = True

    def __init__(símismo, nombre, ecs):
        símismo.nombre = nombre
        símismo.ecs = ecs.para_coso(coso=símismo)

    @property
    def índices_inter(símismo):
        return símismo.nombre

    def activar_ec(símismo, categ, subcateg, ec, **argspc):
        símismo.ecs.activar_ec(categ, subcateg, ec)

    def activar_ecs(símismo, dic_ecs):
        for categ, d_cat in dic_ecs.items():
            for sub, ec in d_cat.items():
                símismo.activar_ec(categ, sub, ec)

    def desactivar_ec(símismo, categ, subcateg=None):
        símismo.ecs.desactivar_ec(categ=categ, subcateg=subcateg)

    def categ_activa(símismo, categ, modelo, mód, exper):
        return símismo.ecs[categ].activa(modelo, mód, exper, coso=símismo)

    def espec_apriori(símismo, apriori, categ, sub_categ, ec, prm, índs=None):
        símismo.ecs.espec_apriori(apriori, categ, sub_categ, ec, prm, inter=índs)

    def borrar_aprioris(símismo, categ=None, sub_categ=None, ec=None, prm=None, índs=None):
        símismo.ecs.borrar_aprioris(categ, sub_categ, ec, prm, índs=índs)

    def verificar(símismo):
        símismo.ecs.verificar()

    def guardar_calibs(símismo, directorio=''):
        arch = os.path.join(directorio, símismo.nombre + '.json')
        guardar_json(símismo._ecs_a_json(), arch)

    def borrar_calib(símismo, nombre):
        símismo.ecs.borrar_calib(nombre)

    def renombrar_calib(símismo, nombre, nuevo):
        símismo.ecs.renombrar_calib(nombre, nuevo)

    def cargar_calibs(símismo, archivo):
        if os.path.splitext(archivo) != '.json':
            archivo = os.path.join(archivo, símismo.nombre + '.json')
        calibs = leer_json(archivo)
        símismo._ecs_de_json(calibs)

    def _ecs_a_json(símismo):
        return símismo.ecs.a_dic()

    def _ecs_de_json(símismo, calibs):
        símismo.ecs.de_dic(calibs)

    def __str__(símismo):
        return símismo.nombre

    def __eq__(símismo, otro):
        return isinstance(otro, símismo.__class__) and símismo.nombre == otro.nombre

    def __hash__(símismo):
        return hash(símismo.nombre)


class SumaCosos(object):
    def __init__(símismo, cosos):
        símismo.cosos = cosos

    def __add__(símismo, otro):
        return SumaCosos(*list(otro), *símismo.cosos)

    def __iter__(símismo):
        for coso in símismo.cosos:
            yield coso
