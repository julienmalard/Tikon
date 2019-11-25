import unittest
from datetime import timedelta

import numpy as np
import numpy.testing as npt
import pandas as pd
from tikon.central import Modelo, Tiempo
from tikon.central.errores import ErrorRequísitos
from tikon.móds.manejo import Manejo, Regla
from tikon.móds.manejo.conds import CondVariable, Igual, SuperiorOIgual, InferiorOIgual, Superior, Inferior, \
    EntreInclusivo, EntreExclusivo, Incluye, Cada, CondFecha, CondO, CondDía, CondY, CondCadaDía
from tikon.utils import EJE_TIEMPO

from .rcrs.mod_incr import MiMódulo, exper, EstabRes2, AgregarRes2, AcciónReq, CondReq


class PruebaConds(unittest.TestCase):
    def test_cond_y(símismo):
        f_inic, f_final = '2000-01-01', '2000-01-05'
        cond1 = CondFecha('2000-01-03', prueba=SuperiorOIgual)
        cond2 = CondFecha('2000-01-04', prueba=InferiorOIgual)

        cond_o = CondY([cond1, cond2])
        acción = EstabRes2(1)
        regla = Regla(cond_o, acción)
        manejo = Manejo(regla)

        modelo = Modelo([MiMódulo(), manejo])
        res = modelo.simular('manejo', exper, t=Tiempo(f_inic, f_final), vars_interés=True)['exper']['módulo']['res 2']

        símismo.assertTrue((res.datos_t.loc[{EJE_TIEMPO: pd.Timestamp('2000-01-02')}] == 0).all())
        símismo.assertTrue((res.datos_t.loc[{EJE_TIEMPO: cond1.umbral}] == 1).all())

    def test_cond_o(símismo):
        f_inic, f_final = '2000-01-01', '2000-01-05'
        cond1 = CondFecha('2000-01-02')
        cond2 = CondFecha('2000-01-03')

        cond_o = CondO([cond1, cond2])
        acción = EstabRes2(1)
        regla = Regla(cond_o, acción)
        manejo = Manejo(regla)

        modelo = Modelo([MiMódulo(), manejo])
        res = modelo.simular('manejo', exper, t=Tiempo(f_inic, f_final), vars_interés=True)['exper']['módulo']['res 2']

        símismo.assertTrue((res.datos_t.loc[{EJE_TIEMPO: cond1.umbral}] == 1).all())

    def test_cond_fecha(símismo):
        f_inic, f_final = '2000-01-01', '2000-01-05'
        cond = CondFecha('2000-01-02')
        acción = EstabRes2(1)
        regla = Regla(cond, acción)
        manejo = Manejo(regla)

        modelo = Modelo([MiMódulo(), manejo])
        res = modelo.simular('manejo', exper, t=Tiempo(f_inic, f_final), vars_interés=True)['exper']['módulo']['res 2']

        símismo.assertTrue((res.datos_t.loc[{EJE_TIEMPO: cond.umbral}] == 1).all())

    def test_cond_día(símismo):
        f_inic, f_final = '2000-01-01', '2000-01-05'
        cond = CondDía(3)
        acción = EstabRes2(1)
        regla = Regla(cond, acción)
        manejo = Manejo(regla)

        modelo = Modelo([MiMódulo(), manejo])
        res = modelo.simular('manejo', exper, t=Tiempo(f_inic, f_final), vars_interés=True)['exper']['módulo']['res 2']

        símismo.assertTrue((res.datos_t.loc[{EJE_TIEMPO: pd.Timestamp(f_inic) + timedelta(cond.umbral)}] == 1).all())

    def test_cond_cada(símismo):
        f_inic, f_final = '2000-01-01', '2000-01-06'
        cond_1 = CondCadaDía(2)
        acción_1 = EstabRes2(0)
        regla_1 = Regla(cond_1, acción_1)

        cond_2 = CondCadaDía(2, desfase=1)
        acción_2 = EstabRes2(1)
        regla_2 = Regla(cond_2, acción_2)
        manejo = Manejo([regla_1, regla_2])

        modelo = Modelo([MiMódulo(), manejo])
        res = modelo.simular('manejo', exper, t=Tiempo(f_inic, f_final), vars_interés=True)['exper']['módulo']['res 2']

        símismo.assertTrue((res.datos_t[{EJE_TIEMPO: np.arange(0, 6, 2)}] == 0).all())
        símismo.assertTrue((res.datos_t[{EJE_TIEMPO: np.arange(1, 6, 2)}] == 1).all())


class PruebaPruebas(unittest.TestCase):
    @staticmethod
    def test_superior_o_igual():
        prb = SuperiorOIgual(3)
        npt.assert_equal(prb([0, 3, 4]), [False, True, True])

    @staticmethod
    def test_inferior_o_igual():
        prb = InferiorOIgual(3)
        npt.assert_equal(prb([0, 3, 4]), [True, True, False])

    @staticmethod
    def test_superior():
        prb = Superior(3)
        npt.assert_equal(prb([0, 3, 4]), [False, False, True])

    @staticmethod
    def test_inferior():
        prb = Inferior(3)
        npt.assert_equal(prb([0, 3, 4]), [True, False, False])

    @staticmethod
    def test_igual():
        prb = Igual(3)
        npt.assert_equal(prb([0, 3, 4]), [False, True, False])

    @staticmethod
    def test_entre_inclusivo():
        prb = EntreInclusivo(3, 5)
        npt.assert_equal(prb([0, 3, 4, 5, 6]), [False, True, True, True, False])

    @staticmethod
    def test_entre_exclusivo():
        prb = EntreExclusivo(3, 5)
        npt.assert_equal(prb([0, 3, 4, 5, 6]), [False, False, True, False, False])

    @staticmethod
    def test_incluye():
        prb = Incluye([3, 4, 5])
        npt.assert_equal(prb([0, 3, 4, 5, 6]), [False, True, True, True, False])

    @staticmethod
    def test_cada():
        prb = Cada(3)
        npt.assert_equal(prb([0, 1, 2, 3, 4, 5, 6]), [True, False, False, True, False, False, True])


class PruebaManejo(unittest.TestCase):
    def test_manejo(símismo):
        cond = CondVariable('módulo', 'res 1', prueba=Igual(3), espera=1)
        acción = EstabRes2(1)
        regla = Regla(cond, acción)
        manejo = Manejo(reglas=regla)
        modelo = Modelo([MiMódulo(), manejo])
        res = modelo.simular('manejo', exper, t=5, vars_interés=True)['exper']['módulo']
        símismo.assertTrue((res['res 2'].datos_t.where(res['res 1'].datos_t == 3).fillna(1) == 1).all())

    def test_requísitos_acción(símismo):
        acción = AcciónReq(3)
        cond = CondVariable('módulo', 'res 1', prueba=Igual(3), espera=1)
        modelo = Modelo([MiMódulo(), Manejo(Regla(cond, acción))])
        with símismo.assertRaises(ErrorRequísitos):
            modelo.simular('requísito', exper=exper, t=5)

    def test_requísitos_cond(símismo):
        acción = AcciónReq(3)
        cond = CondReq('módulo', 'res 1', prueba=Igual(3), espera=1)
        modelo = Modelo([MiMódulo(), Manejo(Regla(cond, acción))])
        with símismo.assertRaises(ErrorRequísitos):
            modelo.simular('requísito', exper=exper, t=5)

    def test_múltiples_acciones(símismo):
        f_inic, f_final = '2000-01-01', '2000-01-05'
        cond = CondFecha('2000-01-02')
        acción1 = AgregarRes2(1)
        acción2 = AgregarRes2(1)
        regla = Regla(cond, [acción1, acción2])
        manejo = Manejo(reglas=regla)
        modelo = Modelo([MiMódulo(), manejo])
        res = modelo.simular('manejo', exper, t=Tiempo(f_inic, f_final), vars_interés=True)['exper']['módulo']['res 2']
        símismo.assertTrue((res.datos_t.loc[{EJE_TIEMPO: cond.umbral}] == 2).all())

    def test_múltiples_reglas(símismo):
        f_inic, f_final = '2000-01-01', '2000-01-05'
        cond1 = CondFecha('2000-01-02')
        acción1 = EstabRes2(1)
        regla1 = Regla(cond1, acción1)

        cond2 = CondFecha('2000-01-03')
        acción2 = EstabRes2(2)
        regla2 = Regla(cond2, acción2)
        manejo = Manejo([regla1, regla2])

        modelo = Modelo([MiMódulo(), manejo])
        res = modelo.simular('manejo', exper, t=Tiempo(f_inic, f_final), vars_interés=True)['exper']['módulo']['res 2']

        símismo.assertTrue((res.datos_t.loc[{EJE_TIEMPO: cond1.umbral}] == 1).all())
        símismo.assertTrue((res.datos_t.loc[{EJE_TIEMPO: cond2.umbral}] == 2).all())
