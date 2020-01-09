import os
import tempfile
import unittest
from datetime import date

import numpy as np
import numpy.testing as npt
import pandas as pd
import xarray as xr
import xarray.testing as xrt

from pruebas.test_central.rcrs import tiempo_obs
from tikon.central import Modelo, Parcela, Exper
from tikon.central.errores import ErrorRequísitos, ErrorNombreInválido
from tikon.utils import EJE_TIEMPO, EJE_ESTOC, EJE_PARÁMS
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
        xrt.assert_equal(res_mód['res 1'].res, res_mód['res 2'].res)

    def test_poner_valor(símismo):
        modelo = poner_valor.modelo
        modelo_rel = poner_valor.modelo_rel
        exper = poner_valor.exper
        with símismo.subTest(relativo=False):
            res = modelo.simular('valor control', exper=exper, t=10, vars_interés=True)
            npt.assert_equal(res['exper']['módulo']['res'].res[{EJE_TIEMPO: slice(1, None)}].values, 1)
        with símismo.subTest(relativo=True):
            res = modelo_rel.simular('valor control', exper=exper, t=10, vars_interés=True)
            datos_res = res['exper']['módulo']['res'].res
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
        npt.assert_equal(res['exper']['módulo']['res'].res.values, 2)

    @staticmethod
    def test_obt_valor_extern():
        from .rcrs import obt_valor_extern
        modelo = obt_valor_extern.modelo
        exper = obt_valor_extern.exper
        res = modelo.simular('valor extern', exper=exper, t=10)
        xrt.assert_equal(res['exper']['módulo 1']['res 1'].res, res['exper']['módulo 2']['res 2'].res)

    @staticmethod
    def test_poner_valor_extern():
        modelo = poner_valor_extern.modelo
        exper = poner_valor_extern.exper
        const = poner_valor_extern.const
        res = modelo.simular('valor extern', exper=exper, t=1)
        npt.assert_equal(res['exper']['módulo 1']['res 1'].res.values, const)

    @staticmethod
    def test_res_inicializable():
        modelo, exper, const = res_inicializable.modelo, res_inicializable.exper, res_inicializable.const
        res = modelo.simular('inicializado', exper=exper, t=1, vars_interés=True)
        datos_res = res['exper']['módulo']['res'].res
        xrt.assert_equal(
            datos_res,
            xr.DataArray(
                const, coords={EJE_TIEMPO: datos_res[EJE_TIEMPO]}, dims=[EJE_TIEMPO]
            ).broadcast_like(datos_res)
        )

    def test_múltiples_exper(símismo):
        modelo = poner_valor.modelo
        expers = [Exper('exper', Parcela('parcela')), Exper('exper 2', Parcela('parcela'))]
        res = modelo.simular('valor control', exper=expers, t=10, vars_interés=True)
        símismo.assertSetEqual({'exper', 'exper 2'}, set(res))

    def test_error_exper_indénticos(símismo):
        modelo = poner_valor.modelo
        expers = [Exper('exper', Parcela('parcela')), Exper('exper', Parcela('parcela'))]
        with símismo.assertRaises(ValueError):
            modelo.simular('valor control', exper=expers, t=10, vars_interés=True)

    @staticmethod
    def test_reps_ent():
        modelo = obt_valor.modelo
        exper = obt_valor.exper
        exper.controles['var'] = 2
        res_mód = modelo.simular('valor control', exper=exper, t=2, reps=4)['exper']['módulo']['res 1']
        npt.assert_equal(res_mód.res[EJE_ESTOC], np.arange(4))
        npt.assert_equal(res_mód.res[EJE_PARÁMS], np.arange(4))

    @staticmethod
    def test_espec_reps():
        modelo = obt_valor.modelo
        exper = obt_valor.exper
        exper.controles['var'] = 2
        res_mód = modelo.simular(
            'valor control', exper=exper, t=2, reps={'estoc': 4, 'paráms': 3}
        )['exper']['módulo']['res 1']
        npt.assert_equal(res_mód.res[EJE_ESTOC], np.arange(4))
        npt.assert_equal(res_mód.res[EJE_PARÁMS], np.arange(3))

    def test_error_reps(símismo):
        modelo = obt_valor.modelo
        exper = obt_valor.exper
        exper.controles['var'] = 2
        with símismo.assertRaises(ValueError):
            modelo.simular(
                'valor control', exper=exper, t=2, reps={'estoc': 4, 'no soy opción': 3}
            )


class PruebaTiempo(unittest.TestCase):

    @staticmethod
    def test_tiempo_de_obs():
        exper = tiempo_obs.exper
        modelo = tiempo_obs.modelo
        f_inic, f_final = tiempo_obs.f_inic, tiempo_obs.f_final
        res = modelo.simular('tiempo numérico', exper=exper)['exper']['módulo']['res']
        npt.assert_equal(res.res[EJE_TIEMPO].values, pd.date_range(f_inic, f_final, freq='D'))

    @staticmethod
    def test_tiempo_numérico_de_obs():
        exper = tiempo_obs.exper
        modelo = tiempo_obs.modelo
        f_inic = tiempo_obs.f_inic
        res = modelo.simular('tiempo numérico', exper=exper, t=10)['exper']['módulo']['res']
        npt.assert_equal(res.res[EJE_TIEMPO].values, pd.date_range(f_inic, periods=11, freq='D'))

    @staticmethod
    def test_obs_tiempo_numérico():
        exper = tiempo_obs.exper_obs_numérico
        modelo = tiempo_obs.modelo
        f_inic = date.today()
        res = modelo.simular('obs numérico', exper=exper)['exper']['módulo']['res']
        npt.assert_equal(res.res[EJE_TIEMPO].values, pd.date_range(f_inic, periods=5, freq='D'))

    @staticmethod
    def test_tiempo_fecha_de_obs_tiempo_numérico():
        exper = tiempo_obs.exper_obs_numérico
        modelo = tiempo_obs.modelo
        f_inic = '2000-01-01'
        res = modelo.simular('obs numérico', exper=exper, t=f_inic)['exper']['módulo']['res']
        npt.assert_equal(res.res[EJE_TIEMPO].values, pd.date_range(f_inic, periods=5, freq='D'))

    @staticmethod
    def test_tiempo_num_de_obs_tiempo_numérico():
        exper = tiempo_obs.exper_obs_numérico
        modelo = tiempo_obs.modelo
        res = modelo.simular('obs numérico', exper=exper, t=10)['exper']['módulo']['res']
        npt.assert_equal(res.res[EJE_TIEMPO].values, pd.date_range(date.today(), periods=11, freq='D'))

    @staticmethod
    def test_no_obs_no_tiempo():
        exper = tiempo_obs.exper_sin_obs
        modelo = tiempo_obs.modelo
        res = modelo.simular('sin tiempo o obs', exper, vars_interés=True)['exper']['módulo']['res']
        npt.assert_equal(res.res[EJE_TIEMPO].values, pd.date_range(date.today(), periods=31, freq='D'))


class PruebaGraficar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from .rcrs.modelo_calib import generar
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        cls.res = modelo.simular('graficar', exper)

    def _verificar_gráfico(símismo, **args):
        with tempfile.TemporaryDirectory() as dir_:
            símismo.res.graficar(dir_, **args)
            símismo.assertTrue(sum([len(files) for r, d, files in os.walk(dir_)]) == 1)

    def test_graficar_sin_incert(símismo):
        símismo._verificar_gráfico(argsll={'incert': None})

    def test_graficar_confianza(símismo):
        símismo._verificar_gráfico(argsll={'incert': 'confianza'})

    def test_graficar_componentes(símismo):
        símismo._verificar_gráfico(argsll={'incert': 'componentes'})

    def test_graficar_tipo_error(símismo):
        with tempfile.TemporaryDirectory() as dir_:
            with símismo.assertRaises(ValueError):
                símismo.res.graficar(dir_, argsll={'incert': 'nombre erróneo'})
