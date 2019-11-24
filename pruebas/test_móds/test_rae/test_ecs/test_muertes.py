import unittest

from pruebas.test_móds.test_rae.test_ecs.utils import gen_modelo_reqs_clima
from tikon.central import Parcela, Exper, Tiempo
from tikon.móds.rae.orgs.ecs.muertes import EcMuerte
from tikon.móds.rae.orgs.ecs.utils import ECS_MRTE
from tikon.móds.rae.orgs.insectos import MetamCompleta
from tikon.móds.rae.red import RedAE

exper = Exper('exper', Parcela('parc'))


class PruebaMuertes(unittest.TestCase):
    def test_ecs(símismo):
        insecto = MetamCompleta('metam completa')
        f_inic, f_final = '2000-01-01', '2000-01-10'
        t = Tiempo(f_inic, f_final)

        for ec in EcMuerte.cls_ramas:
            with símismo.subTest(ec.nombre):
                insecto.activar_ec(ECS_MRTE, subcateg='Ecuación', ec=ec.nombre)
                mod = gen_modelo_reqs_clima(ec, exper=exper, módulos=RedAE(insecto), t=t)
                mod.simular(str(ec), exper=exper, t=t)
