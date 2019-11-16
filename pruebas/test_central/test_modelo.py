import shutil
import tempfile
import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd
import xarray as xr
import xarray.testing as xrt
from pruebas.test_central.rcrs import tiempo_obs
from tikon.central import Modelo
from tikon.central.errores import ErrorRequísitos, ErrorNombreInválido
from tikon.utils import EJE_TIEMPO

from .rcrs import \
    var_con_punto, inic_modelo, obt_valor, poner_valor_extern, poner_valor, res_inicializable


class PruebaModelo(unittest.TestCase):

    @staticmethod
    def test_inic_con_1_módulo():
        Modelo(inic_modelo.Módulo1())

    @staticmethod
    def test_inic_con_lista_módulos():
        Modelo([inic_modelo.Módulo1(), inic_modelo.Módulo2()])

    @staticmethod
    def test_inic_con_clase_módulo():
        Modelo(inic_modelo.Módulo1)

    @staticmethod
    def test_inic_con_lista_mixta():
        Modelo([inic_modelo.Módulo1, inic_modelo.Módulo2()])

    def test_módulo_con_punto(símismo):
        from .rcrs import módulo_con_punto
        with símismo.assertRaises(ErrorNombreInválido):
            módulo_con_punto.modelo.simular('módulo con punto', exper=módulo_con_punto.exper, t=10)

    def test_var_con_punto(símismo):
        with símismo.assertRaises(ErrorNombreInválido):
            var_con_punto.modelo.simular('var con punto', exper=var_con_punto.exper, t=10)

    def test_req_modelo_falta(símismo):
        from .rcrs import req_modelo_falta
        with símismo.assertRaises(ErrorRequísitos):
            req_modelo_falta.modelo.simular('simul modelo falta', exper=req_modelo_falta.exper, t=10)

    def test_req_var_falta(símismo):
        from .rcrs import req_var_falta
        with símismo.assertRaises(ErrorRequísitos):
            req_var_falta.modelo.simular('var modelo falta', exper=req_var_falta.exper, t=10)

    def test_req_control_falta(símismo):
        from .rcrs import req_cntrl_falta
        with símismo.assertRaises(ErrorRequísitos):
            req_cntrl_falta.modelo.simular('simul modelo falta', exper=req_cntrl_falta.exper, t=10)

    @staticmethod
    def test_obt_valor():
        modelo = obt_valor.modelo
        exper = obt_valor.exper
        exper.controles['var'] = 2
        res_mód = modelo.simular('valor control', exper=exper, t=10)['exper']['módulo']
        xrt.assert_equal(res_mód['res 1'].datos, res_mód['res 2'].datos)

    def test_poner_valor(símismo):
        modelo = poner_valor.modelo
        modelo_rel = poner_valor.modelo_rel
        exper = poner_valor.exper
        with símismo.subTest(relativo=False):
            res = modelo.simular('valor control', exper=exper, t=10, vars_interés=True)
            npt.assert_equal(res['exper']['módulo']['res'].datos.values, 1)
        with símismo.subTest(relativo=True):
            res = modelo_rel.simular('valor control', exper=exper, t=10, vars_interés=True)
            datos_res = res['exper']['módulo']['res'].datos_t
            xrt.assert_equal(
                datos_res,
                xr.DataArray(
                    np.arange(11), coords={EJE_TIEMPO: datos_res[EJE_TIEMPO]}, dims=[EJE_TIEMPO]
                ).broadcast_like(datos_res)
            )

    @staticmethod
    def test_obt_valor_control():
        from .rcrs import obt_valor_control
        modelo = obt_valor_control.modelo
        exper = obt_valor_control.exper
        exper.controles['var'] = 2
        res = modelo.simular('valor control', exper=exper, t=10)
        npt.assert_equal(res['exper']['módulo']['res'].datos.values, 2)

    @staticmethod
    def test_obt_valor_extern():
        from .rcrs import obt_valor_extern
        modelo = obt_valor_extern.modelo
        exper = obt_valor_extern.exper
        res = modelo.simular('valor extern', exper=exper, t=10)
        xrt.assert_equal(res['exper']['módulo 1']['res 1'].datos, res['exper']['módulo 2']['res 2'].datos)

    @staticmethod
    def test_poner_valor_extern():
        modelo = poner_valor_extern.modelo
        exper = poner_valor_extern.exper
        const = poner_valor_extern.const
        res = modelo.simular('valor extern', exper=exper, t=1)
        npt.assert_equal(res['exper']['módulo 1']['res 1'].datos.values, const)

    @staticmethod
    def test_res_inicializable():
        modelo, exper, const = res_inicializable.modelo, res_inicializable.exper, res_inicializable.const
        res = modelo.simular('inicializado', exper=exper, t=1, vars_interés=True)
        datos_res = res['exper']['módulo']['res'].datos_t
        xrt.assert_equal(
            datos_res,
            xr.DataArray(
                const, coords={EJE_TIEMPO: datos_res[EJE_TIEMPO]}, dims=[EJE_TIEMPO]
            ).broadcast_like(datos_res)
        )

    @staticmethod
    def test_tiempo_de_obs():
        exper = tiempo_obs.exper
        modelo = tiempo_obs.modelo
        f_inic, f_final = tiempo_obs.f_inic, tiempo_obs.f_final
        res = modelo.simular('tiempo numérico', exper=exper)['exper']['módulo']['res']
        npt.assert_equal(res.datos_t[EJE_TIEMPO].values, pd.date_range(f_inic, f_final, freq='D'))

    @staticmethod
    def test_tiempo_numérico_de_obs():
        exper = tiempo_obs.exper
        modelo = tiempo_obs.modelo
        f_inic = tiempo_obs.f_inic
        res = modelo.simular('tiempo numérico', exper=exper, t=10)['exper']['módulo']['res']
        npt.assert_equal(res.datos_t[EJE_TIEMPO].values, pd.date_range(f_inic, periods=11, freq='D'))

    def test_no_obs_no_tiempo(símismo):
        exper = tiempo_obs.exper_sin_obs
        modelo = tiempo_obs.modelo
        with símismo.assertRaises(ValueError):
            modelo.simular('sin tiempo o obs', exper)


class PruebaGraficar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from .rcrs.graficar_res import modelo, exper
        cls.res = modelo.simular('graficar', exper)
        cls.dir = tempfile.mkdtemp()

    def test_graficar_res(símismo):
        símismo.res.graficar(símismo.dir)

    def test_graficar_confianza(símismo):
        símismo.res.graficar(símismo.dir, argsll={'incert': 'confianza'})

    def test_graficar_componentes(símismo):
        símismo.res.graficar(símismo.dir, argsll={'incert': 'componentes'})

    def test_graficar_tipo_error(símismo):
        with símismo.assertRaises(ValueError):
            símismo.res.graficar(símismo.dir, argsll={'incert': 'nombre erróneo'})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)
