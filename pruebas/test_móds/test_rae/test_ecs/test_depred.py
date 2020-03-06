import unittest

from pruebas.test_móds.test_rae.test_ecs.utils import gen_modelo_reqs_clima
from tikon.central import Parcela, Exper, Tiempo
from tikon.móds.rae.orgs.ecs.depred import EcDepred
from tikon.móds.rae.orgs.ecs.utils import ECS_DEPR
from tikon.móds.rae.orgs.insectos import LotkaVolterra
from tikon.móds.rae.red import RedAE

exper = Exper('exper', Parcela('parc'))


class PruebaDepred(unittest.TestCase):
    def test_depred(símismo):
        presa = LotkaVolterra('Presa')
        depred = LotkaVolterra('Depredador')
        depred_2 = LotkaVolterra('Depredador secundario')
        red = RedAE([presa, depred, depred_2])

        with red:
            depred.secome(presa)
            depred_2.secome(presa)
            depred_2.secome(depred)

        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in EcDepred.cls_ramas:
            with símismo.subTest(ec.nombre):
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=red, t=t)
                depred.activar_ec(ECS_DEPR, subcateg='Ecuación', ec=ec.nombre)
                depred_2.activar_ec(ECS_DEPR, subcateg='Ecuación', ec=ec.nombre)
                mod.simular(str(ec), exper=exper, t=10, depurar=True)
