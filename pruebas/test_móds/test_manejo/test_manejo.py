import unittest

from tikon.central import Modelo
from tikon.móds.manejo import Manejo, Regla
from tikon.móds.manejo.conds import CondVariable, Igual
from .rcrs.mod_incr import MiMódulo, exper, EstabRes2


class PruebaManejo(unittest.TestCase):
    def test_manejo(símismo):
        cond = CondVariable('módulo', 'res 1', prueba=Igual(3), espera=1)
        acción = EstabRes2(1)
        regla = Regla(cond, acción)
        manejo = Manejo(reglas=regla)
        modelo = Modelo([MiMódulo(), manejo])
        res = modelo.simular('manejo', exper, t=5, vars_interés=True)['exper']['módulo']
        símismo.assertTrue((res['res 2'].datos_t.loc[res['res 1'].datos_t == 3] == 1).all())

    @unittest.skip('implementar')
    def test_requísitos_acción(símismo):
        pass

    @unittest.skip('implementar')
    def test_requísitos_regla(símismo):
        pass

    @unittest.skip('implementar')
    def test_múltiples_acciones(símismo):
        pass

    @unittest.skip('implementar')
    def test_múltiples_reglas(símismo):
        pass


class PruebaConds(unittest.TestCase):
    pass


class PruebaPruebas(unittest.TestCase):
    pass
