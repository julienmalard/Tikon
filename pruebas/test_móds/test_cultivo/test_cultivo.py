import unittest

import numpy.testing as npt
from tikon.central import Parcela, Modelo, Exper
from tikon.móds.cultivo.cult import Cultivo
from tikon.móds.cultivo.res import RES_BIOMASA, RES_HUMSUELO
from tikon.móds.rae.orgs.insectos import Sencillo
from tikon.móds.rae.orgs.plantas.externa import Tomate
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import EJE_ETAPA, RES_POBS

from .rcrs.ejemplo import MiParcelaCultivoExterno


class PruebaExterno(unittest.TestCase):
    def test_combin(símismo):
        parc = MiParcelaCultivoExterno(Parcela('parc'))

    def test_combin_estoc(símismo):
        parc = MiParcelaCultivoExterno(Parcela('parc'), combin='estoc')

    @staticmethod
    def test_cultivo_externo():
        hum_suelo, biomasa = 0.3, 4.5
        parc = MiParcelaCultivoExterno(Parcela('parc'), hum_suelo, biomasa)
        mód_cult = Cultivo()

        ins = Sencillo('insecto')
        tomate = Tomate()
        ins.secome(tomate)
        red = RedAE([tomate, ins])

        res = Modelo([mód_cult, red]).simular('cultivo', exper=Exper('exper', parc), t=5, vars_interés=True)['exper']

        npt.assert_equal(res[Cultivo.nombre][RES_BIOMASA].datos_t.values, biomasa)
        npt.assert_equal(res[Cultivo.nombre][RES_HUMSUELO].datos_t.values, hum_suelo)
        npt.assert_equal(res[red.nombre][RES_POBS].datos_t.loc[{EJE_ETAPA: tomate.etapas()}].values, biomasa)


class PruebaCombinSimsCult(unittest.TestCase):
    @unittest.skip('implementar')
    def test_sin_transf(símismo):
        pass

    @unittest.skip('implementar')
    def test_transf_texto(símismo):
        pass

    @unittest.skip('implementar')
    def test_transf_dict(símismo):
        pass

    @unittest.skip('implementar')
    def test_transf_lista(símismo):
        pass

    @unittest.skip('implementar')
    def test_agregar(símismo):
        pass

    @unittest.skip('implementar')
    def test_desagregar(símismo):
        pass
