import unittest

from pcse.models import Wofost71_PP
from tikon.central import Modelo, Exper, Tiempo
from tikon.móds.clima import Clima
from tikon.móds.cultivo.cult import Cultivo
from tikon.móds.cultivo.mod_pcse.clima import FuenteMeteoPCSE
from tikon.móds.cultivo.mod_pcse.parc import ParcelasCultivoPCSE
from tikon.móds.cultivo.res import RES_HUMSUELO
from tikon.móds.rae.orgs.insectos import LotkaVolterra
from tikon.móds.rae.orgs.plantas.externa import RemolachaAzucarera
from tikon.móds.rae.red import RedAE

from pruebas.test_móds.test_cultivo.rcrs.pcse import prov_paráms, prov_meteo, agromanejo


class PruebaPCSE(unittest.TestCase):

    def test_pcse(símismo):
        gusanito = LotkaVolterra('soy gusano')
        remolacha = RemolachaAzucarera()
        gusanito.secome(remolacha)
        red = RedAE([remolacha, gusanito])

        modelo = Wofost71_PP
        parc = ParcelasCultivoPCSE(
            'parc', modelo, prov_paráms=prov_paráms, prov_meteo=prov_meteo, agromanejo=agromanejo
        )
        clima = Clima(fuentes=(FuenteMeteoPCSE(prov_meteo),))
        t = Tiempo('2000-04-01', '2000-04-15')
        res = Modelo(
            [Cultivo, red, clima]
        ).simular('cultivo', exper=Exper('exper', parc), t=t, vars_interés=True)['exper']
        pass
