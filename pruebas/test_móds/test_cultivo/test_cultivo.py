import unittest

import numpy as np
import numpy.testing as npt
import xarray as xr
import xarray.testing as xrt

from tikon.central import Parcela, Modelo, Exper
from tikon.central.matriz import Datos
from tikon.móds.cultivo.cult import Cultivo
from tikon.móds.cultivo.extrn import CombinSimsCult
from tikon.móds.cultivo.res import RES_BIOMASA, RES_HUMSUELO
from tikon.móds.rae.orgs.insectos import LotkaVolterra
from tikon.móds.rae.orgs.plantas.externa import Tomate
from tikon.móds.rae.red import RedAE
from tikon.móds.rae.utils import EJE_ETAPA, RES_POBS
from .rcrs.ejemplo import MiParcelaCultivoExterno


class PruebaExterno(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hum_suelo, cls.biomasa = 0.3, 4.5
        cls.mód_cult = Cultivo()
        cls.ins = LotkaVolterra('insecto')
        cls.tomate = Tomate()
        with RedAE([cls.tomate, cls.ins]) as cls.red:
            cls.ins.secome(cls.tomate)

    def _prueba_parc(símismo, parc):
        res = Modelo(
            [símismo.mód_cult, símismo.red]
        ).simular('cultivo', exper=Exper('exper', parc), t=5, vars_interés=True)['exper']

        npt.assert_equal(res[Cultivo.nombre][RES_BIOMASA].res.values, símismo.biomasa)
        npt.assert_equal(res[Cultivo.nombre][RES_HUMSUELO].res.values, símismo.hum_suelo)
        npt.assert_equal(
            res[RedAE.nombre][RES_POBS].res.loc[{EJE_ETAPA: símismo.tomate.etapas}].values, símismo.biomasa
        )

    def test_combin(símismo):
        símismo._prueba_parc(MiParcelaCultivoExterno(Parcela('parc'), símismo.hum_suelo, símismo.biomasa))

    def test_combin_estoc(símismo):
        símismo._prueba_parc(
            MiParcelaCultivoExterno(Parcela('parc'), símismo.hum_suelo, símismo.biomasa, combin='estoc')
        )

    def test_cultivo_externo(símismo):
        símismo._prueba_parc(
            MiParcelaCultivoExterno(Parcela('parc'), símismo.hum_suelo, símismo.biomasa)
        )


class PruebaCombinSimsCult(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reps = {'paráms': 5, 'estoc': 3}
        cls.coords = {'eje 1': ['a', 'b', 'c'], **{ll: range(v) for ll, v in cls.reps.items()}}
        cls.datos = Datos(0., dims=list(cls.coords), coords=cls.coords)

    def _verificar_agregar(símismo, combin, coords):
        agregado = combin.agregar(símismo.datos)
        xrt.assert_equal(agregado.a_xarray(), xr.DataArray(0., coords=coords, dims=list(coords)))
        return agregado

    def _verificar_desagregar(símismo, combin, agregado):
        desagregado = combin.desagregar(agregado, reps=símismo.reps)
        xrt.assert_equal(desagregado.a_xarray(), símismo.datos.transponer(desagregado.dims).a_xarray())

    def test_transf_lista(símismo):
        combin = CombinSimsCult(('estoc', 'paráms'))
        agr = símismo._verificar_agregar(
            combin,
            coords={'eje 1': símismo.coords['eje 1']}
        )
        símismo._verificar_desagregar(combin, agr)

    def test_sin_transf(símismo):
        combin = CombinSimsCult()
        agr = símismo._verificar_agregar(combin, coords=símismo.coords)
        símismo._verificar_desagregar(combin, agr)

    def test_transf_texto(símismo):
        combin = CombinSimsCult('estoc')
        agr = símismo._verificar_agregar(
            combin,
            coords={dim: símismo.coords[dim] for dim in ['eje 1', 'paráms']}
        )
        símismo._verificar_desagregar(combin, agr)

    def test_transf_dict(símismo):
        combin = CombinSimsCult({'estoc': np.mean})
        agr = símismo._verificar_agregar(
            combin,
            coords={dim: símismo.coords[dim] for dim in ['eje 1', 'paráms']}
        )
        símismo._verificar_desagregar(combin, agr)
