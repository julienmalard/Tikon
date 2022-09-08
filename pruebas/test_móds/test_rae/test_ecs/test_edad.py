import unittest

from pruebas.test_móds.test_rae.test_ecs.utils import gen_modelo_reqs_clima
from tikon.central import Parcela, Exper, Tiempo
from tikon.ecs import EcuaciónVacía
from tikon.móds.rae.orgs.ecs.edad import EcEdad
from tikon.móds.rae.orgs.ecs.utils import ECS_EDAD
from tikon.móds.rae.orgs.insectos import MetamCompleta
from tikon.móds.rae.red import RedAE

exper = Exper('exper', Parcela('parc'))


class PruebaEdad(unittest.TestCase):
    def test_ecs(símismo):
        insecto = MetamCompleta('metam completa')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)

        for ec in EcEdad.cls_ramas:
            if ec is EcuaciónVacía:
                continue
            with símismo.subTest(ec.nombre):
                insecto.activar_ec(ECS_EDAD, subcateg='Ecuación', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=RedAE(insecto), t=t)
                mod.simular(str(ec), exper=exper, t=t, depurar=True)
