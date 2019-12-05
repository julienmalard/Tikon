import unittest

from tikon.central import Modelo
from pruebas.test_móds.test_rae.rcrs import redes


class PruebaRed(unittest.TestCase):
    def test_1_insecto(símismo):
        res = Modelo(redes.red_1_insecto).simular('1 insecto', exper=redes.exper, t=10, depurar=True)

    def test_red_depred(símismo):
        res = Modelo(redes.red_depred).simular('depred', exper=redes.exper, t=10, depurar=True)

    def test_red_depred_sub(símismo):
        res = Modelo(redes.red_depred_sub).simular('depred sub', exper=redes.exper, t=10, depurar=True)

    def test_red_parasitismo(símismo):
        res = Modelo(redes.red_parasitismo).simular('parasitismo', exper=redes.exper, t=10, depurar=True)

    def test_red_esfécido(símismo):
        res = Modelo(redes.red_esfécido).simular('esfécido', exper=redes.exper, t=10, depurar=True)