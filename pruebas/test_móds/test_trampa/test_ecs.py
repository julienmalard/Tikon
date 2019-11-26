import unittest

from pruebas.test_móds.test_rae.test_ecs.utils import gen_modelo_reqs_clima
from tikon.central import Parcela, Exper, Tiempo
from tikon.móds.rae.red import RedAE
from tikon.móds.trampa.ecs.captura import EcCaptura
from tikon.móds.trampa.ecs.descomp import EcDescomp
from tikon.móds.trampa.ecs.utils import ECS_DESCOMP, ECS_CAPTURA
from tikon.móds.trampa.mód import Trampas
from tikon.móds.trampa.trampas import Trampa

from .rcrs.trampas import ins

exper = Exper('exper', Parcela('parc'))


class PruebaApli(unittest.TestCase):
    def test_descomp(símismo):
        trampa = Trampa('amarilla')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in EcDescomp.cls_ramas:
            with símismo.subTest(ec.nombre):
                trampa.activar_ec(ECS_DESCOMP, subcateg='Ecuación', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=[RedAE(ins), Trampas(trampa)], t=t)
                mod.simular(str(ec), exper=exper, t=t)

    def test_captura(símismo):
        trampa = Trampa('amarilla')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in EcCaptura.cls_ramas:
            with símismo.subTest(ec.nombre):
                trampa.activar_ec(ECS_CAPTURA, subcateg='Ecuación', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=[RedAE(ins), Trampas(trampa)], t=t)
                mod.simular(str(ec), exper=exper, t=t)
