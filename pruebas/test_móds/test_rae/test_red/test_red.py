import unittest

from pruebas.test_móds.test_rae.rcrs import redes as r
from tikon.central import Modelo
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.red.red import ErrorParasitismoCircular


class PruebaRed(unittest.TestCase):
    def test_1_insecto(símismo):
        res = Modelo(r.red_1_insecto).simular('1 insecto', exper=r.exper, t=10, depurar=True)

    def test_depred(símismo):
        símismo.assertSetEqual(r.red_depred.presas(), set(r.sencillo.etapas))
        res = Modelo(r.red_depred).simular('depred sub', exper=r.exper, t=10, depurar=True)

    def test_depred_mútliples(símismo):
        símismo.assertSetEqual(
            set(r.red_depred_mútliples.presas()), set(r.sencillo.etapas).union(r.otro_sencillo.etapas)
        )
        res = Modelo(r.red_depred_mútliples).simular('depred', exper=r.exper, t=10, depurar=True)

    def test_parasitismo(símismo):
        res = Modelo(r.red_parasitismo).simular('parasitismo', exper=r.exper, t=10, depurar=True)

    def test_esfécido(símismo):
        res = Modelo(r.red_esfécido).simular('esfécido', exper=r.exper, t=10, depurar=True)

    def test_hiperparasitismo(símismo):
        res = Modelo(r.red_hiperparasitismo).simular('esfécido', exper=r.exper, t=10, depurar=True)

    def test_parasitismo_circular(símismo):
        with símismo.assertRaises(ErrorParasitismoCircular):
            with RedAE():
                r.parasitoide.parasita(r.metam_completa)
                r.hiperparasitoide.parasita(r.parasitoide)
                r.parasitoide.parasita(r.hiperparasitoide)

    def test_parasitoide_generalista(símismo):
        # Verifica que múltiples transiciones a la misma etapa (de huéspedes al parasitoide adulto) funcionen
        res = Modelo(r.red_paras_generalista).simular('paras generalista', exper=r.exper, t=10, depurar=True)

    @unittest.skip('Implementar')
    def test_canibalismo(símismo):
        pass

    @unittest.skip('Implementar')
    def test_depredador_y_parasitoide(símismo):
        # Verificar que depredador come fantasma
        pass

    @unittest.skip('Implementar')
    def test_depredador_e_hyperparasitoide(símismo):
        pass

    @unittest.skip('Implementar')
    def test_depredador_de_parasitoide(símismo):
        pass

    @unittest.skip('Implementar')
    def test_depredador_de_fantasma(símismo):
        pass

    @unittest.skip('Implementar')
    def test_depredador_de_hyperparasitoide(símismo):
        pass


class PruebaParasitismo(unittest.TestCase):
    @unittest.skip('Implementar')
    def test_entra_auto_mútiples_juveniles(símismo):
        pass

    @unittest.skip('Implementar')
    def test_entra_auto_sin_juvenil(símismo):
        pass

    @unittest.skip('Implementar')
    def test_entra_auto_juvenil_único(símismo):
        pass

    @unittest.skip('Implementar')
    def test_entra_auto_huevo(símismo):
        pass

    @unittest.skip('Implementar')
    def test_emerg_auto(símismo):
        pass

    @unittest.skip('Implementar')
    def test_emerg_auto_entra_final(símismo):
        pass

    @unittest.skip('Implementar')
    def test_emerge_antes_entra(símismo):
        pass

    @unittest.skip('Implementar')
    def test_sin_espec(símismo):
        pass
