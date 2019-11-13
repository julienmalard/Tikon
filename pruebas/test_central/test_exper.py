import unittest

from tikon.central import Exper, Parcela, GrupoParcelas
from tikon.utils import EJE_PARC


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

    def test_controles(símismo):
        exp = Exper('mi experimento', parcelas=[Parcela('una'), Parcela('otra')])
        símismo.assertListEqual(exp.controles['parcelas'], ['una', 'otra'])
        for cntrl in ['superficies', 'elevaciones', 'centroides', 'distancias']:
            with símismo.subTest(cntrl):
                símismo.assertListEqual(exp.controles[cntrl][EJE_PARC].values.tolist(), ['una', 'otra'])

    @unittest.skip('implementar')
    def test_datos(símismo):
        pass
