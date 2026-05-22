import unittest

from .rcrs.trampas import modelo, exper


class PruebaAplicaciones(unittest.TestCase):
    def test_apli(símismo):
        modelo.simular("aplis", exper=exper, t=10)
