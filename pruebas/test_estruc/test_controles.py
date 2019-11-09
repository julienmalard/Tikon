import unittest

from tikon.central import ControlesExper, Parcela


class PruebaControlesExper(unittest.TestCase):
    def test_nuevo_control(símismo):
        cntrl = ControlesExper(parcelas=[Parcela('mi parcela')])
        cntrl['variable'] = 1
        símismo.assertEqual(cntrl['variable'], 1)

    def test_cambiar_existente(símismo):
        cntrl = ControlesExper(parcelas=[Parcela('mi parcela')])
        cntrl['n_cohortes'] = 15
        símismo.assertEqual(cntrl['n_cohortes'], 15)

    def test_borrar_cambio_existente(símismo):
        cntrl = ControlesExper(parcelas=[Parcela('mi parcela')])
        cntrl['n_cohortes'] = 15
        cntrl['n_cohortes'] = None
        símismo.assertEqual(cntrl['n_cohortes'], 10)

    def test_contiene(símismo):
        cntrl = ControlesExper(parcelas=[Parcela('mi parcela')])
        cntrl['mi variable'] = 123
        símismo.assertTrue('mi variable' in cntrl)
        símismo.assertFalse('otro variable' in cntrl)
