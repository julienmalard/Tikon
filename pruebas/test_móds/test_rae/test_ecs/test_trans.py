import unittest

from pruebas.test_móds.test_rae.test_ecs.utils import gen_modelo_reqs_clima
from tikon.central import Parcela, Exper, Tiempo
from tikon.móds.rae.orgs.ecs.trans import ProbTrans, MultTrans
from tikon.móds.rae.orgs.ecs.utils import ECS_TRANS
from tikon.móds.rae.orgs.insectos import MetamCompleta
from tikon.móds.rae.red import RedAE

exper = Exper('exper', Parcela('parc'))


class PruebaCrec(unittest.TestCase):
    def test_probs(símismo):
        insecto = MetamCompleta('metam completa')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in ProbTrans.cls_ramas:
            with símismo.subTest(ec.nombre):
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=RedAE(insecto), t=t)
                insecto.activar_ec(ECS_TRANS, subcateg='Prob', ec=ec.nombre)
                mod.simular(str(ec), exper=exper, t=10)

    def test_mult(símismo):
        insecto = MetamCompleta('metam completa')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in MultTrans.cls_ramas:
            with símismo.subTest(ec.nombre):
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=RedAE(insecto), t=t)
                insecto.activar_ec(ECS_TRANS, subcateg='Mult', ec=ec.nombre)
                mod.simular(str(ec), exper=exper, t=10)
