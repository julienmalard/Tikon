import unittest

from pruebas.test_móds.test_rae.test_ecs.utils import gen_modelo_reqs_clima
from tikon.central import Parcela, Exper, Tiempo, GeomParcela
from tikon.móds.rae.orgs.ecs.mov import Distancia, Atracción
from tikon.móds.rae.orgs.ecs.utils import ECS_MOV
from tikon.móds.rae.orgs.insectos import MetamCompleta, Sencillo
from tikon.móds.rae.red import RedAE

exper = Exper('exper', [Parcela('parc'), Parcela('parc 2', geom=GeomParcela(centroide=(11.0025001, 76.9656001)))])


class PruebaMovimiento(unittest.TestCase):
    def test_atr(símismo):
        insecto = Sencillo('sencillo')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)

        for ec in Atracción.cls_ramas:
            with símismo.subTest(ec.nombre):
                insecto.activar_ec(ECS_MOV, subcateg='Atracción', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=RedAE(insecto), t=t)
                mod.simular(str(ec), exper=exper, t=t, depurar=True)

    def test_dist(símismo):
        insecto = Sencillo('sencillo')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)

        for ec in Distancia.cls_ramas:
            with símismo.subTest(ec.nombre):
                insecto.activar_ec(ECS_MOV, subcateg='Distancia', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=RedAE(insecto), t=t)
                mod.simular(str(ec), exper=exper, t=t, depurar=True)
