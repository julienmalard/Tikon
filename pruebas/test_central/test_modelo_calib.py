import shutil
import tempfile
import unittest

from tikon.central.calibs import EspecCalibsCorrida


class PruebaCalibEcs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from .rcrs.modelo_calib import generar
        cls.dir_ = tempfile.mkdtemp()
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        modelo.calibrar('calib', exper, n_iter=30)
        modelo.guardar_calibs(cls.dir_)

    def test_cargar_calib(símismo):
        from .rcrs.modelo_calib import generar
        otro = generar()
        otro_modelo = otro['modelo']
        otro_exper = otro['exper']
        otro_modelo.cargar_calibs(símismo.dir_)
        valid = otro_modelo.simular('valid', otro_exper, calibs=['calib']).validar()
        símismo.assertGreater(valid['ens'], 0.95)

    def test_calib_paráms_mód(símismo):
        from .rcrs.modelo_calib_mód import modelo, exper, módulo1, coso1, coso2
        modelo.calibrar('calib', exper, n_iter=30, paráms=módulo1)
        dists_disp_1 = coso1.ecs['categ']['subcateg']['ec']['a'].dists_disp(inter=None, heredar=False)
        dists_disp_2 = coso2.ecs['categ']['subcateg']['ec']['a'].dists_disp(inter=None, heredar=False)
        símismo.assertIn('calib', dists_disp_1)
        símismo.assertNotIn('calib', dists_disp_2)

    def test_renombrar_calib(símismo):
        from .rcrs.modelo_calib import generar
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        coso = gen['coso']
        modelo.cargar_calibs(símismo.dir_)

        coso.renombrar_calib('calib', 'otro nombre')
        valid = modelo.simular('valid', exper, calibs=['otro nombre']).validar()
        símismo.assertGreater(valid['ens'], 0.95)

    def test_borrar_calib(símismo):
        from .rcrs.modelo_calib import generar
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        coso = gen['coso']
        modelo.cargar_calibs(símismo.dir_)

        coso.borrar_calib('calib')
        valid = modelo.simular('valid', exper).validar()
        símismo.assertLess(valid['ens'], 0.90)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir_)


class PruebaCalibTiempo(unittest.TestCase):
    def test_obs_tiempo_numérico(símismo):
        from .rcrs.modelo_calib import generar
        gen = generar(fechas=False)
        modelo = gen['modelo']
        exper = gen['exper']
        modelo.calibrar('calib', exper, n_iter=30)
        valid = modelo.simular('valid', exper).validar()
        símismo.assertGreater(valid['ens'], 0.95)


class PruebaCalibInic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from .rcrs.modelo_calib_inic import generar
        cls.dir_ = tempfile.mkdtemp()
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        modelo.calibrar('calib', exper, n_iter=50)
        modelo.guardar_calibs(cls.dir_)
        exper.guardar_calibs(cls.dir_)

    def test_cargar_calib(símismo):
        from .rcrs.modelo_calib_inic import generar
        otro = generar()
        otro_modelo = otro['modelo']
        otro_exper = otro['exper']
        otro_modelo.cargar_calibs(símismo.dir_)
        otro_exper.cargar_calibs(símismo.dir_)

        valid = otro_modelo.simular('valid', otro_exper, calibs=EspecCalibsCorrida(['calib'])).validar()
        símismo.assertGreater(valid['ens'], 0.95)

    def test_renombrar_calib(símismo):
        from .rcrs.modelo_calib_inic import generar
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        coso = gen['coso']
        modelo.cargar_calibs(símismo.dir_)
        exper.cargar_calibs(símismo.dir_)

        coso.renombrar_calib('calib', 'otro nombre')
        exper.renombrar_calib('calib', 'otro nombre')
        valid = modelo.simular('valid', exper, calibs=EspecCalibsCorrida(['otro nombre'])).validar()
        símismo.assertGreater(valid['ens'], 0.95)

    def test_borrar_calib(símismo):
        from .rcrs.modelo_calib_inic import generar
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        modelo.cargar_calibs(símismo.dir_)
        exper.cargar_calibs(símismo.dir_)

        exper.borrar_calib('calib')
        valid = modelo.simular('valid', exper).validar()
        símismo.assertLess(valid['ens'], 0.90)

    def test_calib_exluir_inic(símismo):
        from .rcrs.modelo_calib_inic import generar
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        módulo = gen['módulo']
        exper.cargar_calibs(símismo.dir_)
        # para hacer: opción sin aprioris únicamente para exper
        modelo.calibrar('calib', exper, n_iter=50, paráms=módulo, calibs=EspecCalibsCorrida(aprioris=False))
        valid = modelo.simular('valid', exper, calibs=EspecCalibsCorrida(['calib'])).validar()
        símismo.assertGreater(valid['ens'], 0.95)

    def test_calib_solamente_inic(símismo):
        from .rcrs.modelo_calib_inic import generar
        gen = generar()
        modelo = gen['modelo']
        exper = gen['exper']
        modelo.cargar_calibs(símismo.dir_)
        modelo.calibrar('calib', exper, n_iter=50, paráms=exper)
        valid = modelo.simular('valid', exper, calibs=EspecCalibsCorrida(['calib'])).validar()
        símismo.assertGreater(valid['ens'], 0.90)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir_)
