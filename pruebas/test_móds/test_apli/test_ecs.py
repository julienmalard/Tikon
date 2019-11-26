import unittest

from pruebas.test_móds.test_rae.test_ecs.utils import gen_modelo_reqs_clima
from tikon.central import Parcela, Exper, Tiempo
from tikon.móds.apli.apli import Aplicaciones
from tikon.móds.apli.ecs.descomp import EcDescomp
from tikon.móds.apli.ecs.mrtld import EcMortalidad
from tikon.móds.apli.ecs.utils import ECS_DESCOMP, ECS_MRTLD
from tikon.móds.apli.prods import Producto
from tikon.móds.rae.red import RedAE

from .rcrs.aplis import ins

exper = Exper('exper', Parcela('parc'))


class PruebaApli(unittest.TestCase):
    def test_descomp(símismo):
        prod = Producto('producto')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in EcDescomp.cls_ramas:
            with símismo.subTest(ec.nombre):
                prod.activar_ec(ECS_DESCOMP, subcateg='Ecuación', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=[RedAE(ins), Aplicaciones(prod)], t=t)
                mod.simular(str(ec), exper=exper, t=t)

    def test_mrtld(símismo):
        prod = Producto('producto')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)
        for ec in EcMortalidad.cls_ramas:
            with símismo.subTest(ec.nombre):
                prod.activar_ec(ECS_MRTLD, subcateg='Ecuación', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=[RedAE(ins), Aplicaciones(prod)], t=t)
                mod.simular(str(ec), exper=exper, t=t)
