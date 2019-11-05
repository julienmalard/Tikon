import unittest

from tikon.estruc import Exper, Parcela, GrupoParcelas


class PruebaExperParc(unittest.TestCase):
    def test_1_parcela(símismo):
        exp = Exper('mi experimento', parcelas=Parcela('mi parcela'))
        símismo.assertEqual(len(exp.parcelas), 1)

    def test_más_parcelas(símismo):
        exp = Exper('mi experimento', parcelas=[Parcela('una'), Parcela('otra')])
        símismo.assertEqual(len(exp.parcelas), 2)

    def test_grupo_parcelas(símismo):
        exp = Exper('mi experimento', parcelas=GrupoParcelas([Parcela('una'), Parcela('otra')]))
        símismo.assertEqual(len(exp.parcelas), 2)

    def test_grupo_y_parcelas(símismo):
        exp = Exper('mi experimento', parcelas=[Parcela('una'), GrupoParcelas([Parcela('y'), Parcela('otra')])])
        símismo.assertEqual(len(exp.parcelas), 3)

