import unittest

from pruebas.test_móds.test_rae.test_ecs.utils import gen_modelo_reqs_clima
from tikon.central import Parcela, Exper, Tiempo
from tikon.móds.rae.orgs.ecs.crec.ec import EcCrec
from tikon.móds.rae.orgs.ecs.crec.tasa import TasaCrec
from tikon.móds.rae.orgs.ecs.utils import ECS_CREC
from tikon.móds.rae.orgs.insectos import LotkaVolterra
from tikon.móds.rae.red import RedAE

exper = Exper('exper', Parcela('parc'))


class PruebaCrec(unittest.TestCase):
    def test_ecs(símismo):
        insecto = LotkaVolterra('sencillo')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in EcCrec.cls_ramas:
            with símismo.subTest(ec.nombre):
                insecto.activar_ec(ECS_CREC, subcateg='Ecuación', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=RedAE(insecto), t=t)
                mod.simular(str(ec), exper=exper, t=t, depurar=True)

    def test_modifs(símismo):
        insecto = LotkaVolterra('sencillo')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in TasaCrec.cls_ramas:
            with símismo.subTest(ec.nombre):
                insecto.activar_ec(ECS_CREC, subcateg='Tasa', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=RedAE(insecto), t=t)
                mod.simular(str(ec), exper=exper, t=t, depurar=True)
