import unittest

from pruebas.test_móds.test_rae.test_ecs.utils import gen_modelo_reqs_clima
from tikon.central import Parcela, Exper, Tiempo
from tikon.móds.rae.orgs.ecs.depred import EcDepred
from tikon.móds.rae.orgs.ecs.utils import ECS_DEPR
from tikon.móds.rae.orgs.insectos import Sencillo
from tikon.móds.rae.red import RedAE

exper = Exper('exper', Parcela('parc'))


class PruebaDepred(unittest.TestCase):
    def test_depred(símismo):
        presa = Sencillo('Presa')
        depred = Sencillo('Depredador')
        depred.secome(presa)

        depred_2 = Sencillo('Depredador secundario')
        depred_2.secome(presa)
        depred_2.secome(depred)

        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in EcDepred.cls_ramas:
            with símismo.subTest(ec.nombre):
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=RedAE([presa, depred, depred_2]), t=t)
                depred.activar_ec(ECS_DEPR, subcateg='Ecuación', ec=ec.nombre)
                depred_2.activar_ec(ECS_DEPR, subcateg='Ecuación', ec=ec.nombre)
                mod.simular(str(ec), exper=exper, t=10, depurar=True)
