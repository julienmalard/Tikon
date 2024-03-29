import unittest

import numpy as np
import numpy.testing as npt
import xarray as xr
import xarray.testing as xrt

from tikon.central.matriz import Datos, lleno_como, combinar, máximo, mínimo, donde, f_numpy, codificar_coords


def _prb_igl(dts, mxr):
    xrt.assert_equal(dts.a_xarray(), mxr)


def _datos_igls(dt1, dt2, caso, meta=False):
    caso.assertTupleEqual(dt1.dims, dt2.dims)
    caso.assertDictEqual(dt1.coords, dt2.coords)
    npt.assert_equal(dt1.matr, dt2.matr)
    if meta:
        caso.assertEqual(dt1.nombre, dt2.nombre)
        caso.assertDictEqual(dt1.atribs, dt2.atribs)


def _datos(mxr=True):
    dts = Datos(np.arange(2 * 3, dtype=float).reshape((2, 3)), dims=['a', 'b'],
                coords={'a': [1, 2], 'b': ['x', 'y', 'z']}, nombre='datos', atribs={'unidades': 'gatos'})
    if mxr:
        return dts, dts.a_xarray()
    return dts


class PruebaAritmética(unittest.TestCase):

    def test_plus(símismo):
        dts, mxr = _datos()
        _prb_igl(dts + 3, mxr + 3)

    def test_menos(símismo):
        dts, mxr = _datos()
        _prb_igl(dts - 3, mxr - 3)

    def test_mult(símismo):
        dts, mxr = _datos()
        _prb_igl(dts * 3, mxr * 3)

    def test_div(símismo):
        dts, mxr = _datos()
        _prb_igl(dts / 3, mxr / 3)

    def test_div_ent(símismo):
        dts, mxr = _datos()
        _prb_igl(dts // 3, mxr // 3)

    def test_pot(símismo):
        dts, mxr = _datos()
        _prb_igl(dts ** 3, mxr ** 3)

    def test_ig(símismo):
        dts, mxr = _datos()
        _prb_igl(dts == 3, mxr == 3)

    def test_noig(símismo):
        dts, mxr = _datos()
        _prb_igl(dts != 3, mxr != 3)

    def test_sup(símismo):
        dts, mxr = _datos()
        _prb_igl(dts > 3, mxr > 3)

    def test_supig(símismo):
        dts, mxr = _datos()
        _prb_igl(dts >= 3, mxr >= 3)

    def test_inf(símismo):
        dts, mxr = _datos()
        _prb_igl(dts < 3, mxr < 3)

    def test_infig(símismo):
        dts, mxr = _datos()
        _prb_igl(dts <= 3, mxr <= 3)

    def test_y(símismo):
        dts, mxr = _datos()
        _prb_igl((dts < 5) & (dts > 2), (mxr < 5) & (mxr > 2))

    def test_o(símismo):
        dts, mxr = _datos()
        _prb_igl((dts < 2) | (dts > 6), (mxr < 2) | (mxr > 6))

    def test_abs(símismo):
        dts, mxr = _datos()
        _prb_igl(abs(dts), abs(mxr))

    def test_redond(símismo):
        dts, mxr = _datos()
        _prb_igl(dts.redond(), mxr.round())


class PruebaAritméticaAug(unittest.TestCase):
    def test_iplus(símismo):
        dts, mxr = _datos()
        dts += 3
        _prb_igl(dts, mxr + 3)

    def test_imenos(símismo):
        dts, mxr = _datos()
        dts -= 3
        _prb_igl(dts, mxr - 3)

    def test_imult(símismo):
        dts, mxr = _datos()
        dts *= 3
        _prb_igl(dts, mxr * 3)

    def test_idiv(símismo):
        dts, mxr = _datos()
        dts /= 3
        _prb_igl(dts, mxr / 3)

    def test_idiv_ent(símismo):
        dts, mxr = _datos()
        dts //= 3
        _prb_igl(dts, mxr // 3)

    def test_ipot(símismo):
        dts, mxr = _datos()
        dts **= 3
        _prb_igl(dts, mxr ** 3)


class PruebaDatos(unittest.TestCase):
    def test_copiar(símismo):
        dts = _datos(False)
        dts2 = dts.copiar()
        _datos_igls(dts, dts2, símismo, meta=True)
        dts2 += 3
        npt.assert_equal(dts.matr + 3, dts2.matr)

    def test_renombrar(símismo):
        dts, mxr = _datos()
        _prb_igl(dts.renombrar({'a': 'c'}), mxr.rename({'a': 'c'}))

    def test_llenar_nan(símismo):
        dts = _datos(False)
        dts.donde(dts < 4, np.nan)
        mxr = dts.a_xarray()
        dts.llenar_nan(-1)
        _prb_igl(dts, mxr.fillna(-1))

    def test_nuevo_como(símismo):
        dts = _datos(False)
        _datos_igls(dts, dts.nuevo_como(dts.matr), símismo, meta=True)

    def test_expandir_dims(símismo):
        dts, mxr = _datos()
        dts.expandir_dims(dts.codificar_coords({'c': [1]}))
        mxr.expand_dims('c', 1)
        _prb_igl(dts, mxr)

    def test_transposar(símismo):
        dts, mxr = _datos()
        _prb_igl(dts.transponer(['b', 'a']), mxr.transpose(*['b', 'a']))

    def test_dejar(símismo):
        dts = _datos(False)
        dts = dts.loc[dts.codificar_coords({'b': ['x']})]
        mxr = dts.a_xarray()
        _prb_igl(dts.dejar('b'), mxr.squeeze('b').drop_vars('b'))

    def test_dejar_no_unitario(símismo):
        with símismo.assertRaises(ValueError):
            _datos(False).dejar('a')


class PruebaFDatos(unittest.TestCase):
    def test_f_eje(símismo):
        dts, mxr = _datos()
        _prb_igl(dts.f_eje(np.median, dim='a'), mxr.reduce(np.median, dim='a'))

    def test_prod(símismo):
        dts, mxr = _datos()
        with símismo.subTest(dim=True):
            símismo.assertEqual(dts.prod(), mxr.prod().item())
        with símismo.subTest(dim='a'):
            _prb_igl(dts.prod('a'), mxr.prod('a'))

    def test_suma(símismo):
        dts, mxr = _datos()
        with símismo.subTest(dim=True):
            símismo.assertEqual(dts.suma(), mxr.sum().item())
        with símismo.subTest(dim='a'):
            _prb_igl(dts.suma('a'), mxr.sum('a'))

    def test_cualquier(símismo):
        dts = _datos(False) >= 4
        mxr = dts.a_xarray()
        with símismo.subTest(dim=True):
            símismo.assertEqual(dts.cualquier(), mxr.any().item())
        with símismo.subTest(dim='a'):
            _prb_igl(dts.cualquier('a'), mxr.any('a'))

    def test_donde(símismo):
        dts, mxr = _datos()
        _prb_igl(dts.donde(dts > 3, -1), mxr.where(mxr > 3, -1))

    def test_f(símismo):
        dts, mxr = _datos()
        _prb_igl(dts.f(np.log), np.log(mxr))

    def test_fi(símismo):
        dts, mxr = _datos()
        dts.fi(np.log)
        _prb_igl(dts, np.log(mxr))


class PruebaSel(unittest.TestCase):
    def test_sel_1_eje(símismo):
        dts, mxr = _datos()
        sel = {'b': [0, 2]}
        _prb_igl(dts[codificar_coords(sel)], mxr[sel])

    def test_sel_2_ejes(símismo):
        dts, mxr = _datos()
        sel = {'a': [0], 'b': [0, 2]}
        _prb_igl(dts[codificar_coords(sel)], mxr[sel])

    def test_poner_val(símismo):
        dts, mxr = _datos()
        sel = {'b': [0, 2]}
        dts[codificar_coords(sel)] = -1
        mxr[sel] = -1
        _prb_igl(dts, mxr)

    def test_poner_de_datos(símismo):
        dts, mxr = _datos()
        nuevo = dts.nuevo_como(-1)

        dts[:] = nuevo
        mxr[:] = nuevo.a_xarray()
        _prb_igl(dts, mxr)

    def test_poner_de_datos_1_eje(símismo):
        dts, mxr = _datos()
        nuevo = dts.nuevo_como(-1)
        sel = {'b': [0, 2]}

        dts[codificar_coords(sel)] = nuevo
        mxr[sel] = nuevo[codificar_coords(sel)].a_xarray()
        _prb_igl(dts, mxr)

    def test_poner_de_datos_sub(símismo):
        dts, mxr = _datos()
        nuevo = dts.nuevo_como(-1)
        sel = {'b': [0, 2]}

        dts[codificar_coords(sel)] = nuevo
        mxr[sel] = nuevo[codificar_coords(sel)].a_xarray()
        _prb_igl(dts, mxr)


class PruebaLoc(unittest.TestCase):
    def test_loc_1_eje(símismo):
        dts, mxr = _datos()
        sel = {'b': ['x', 'z']}
        _prb_igl(dts.loc[codificar_coords(sel)], mxr.loc[sel])

    def test_loc_poner_val(símismo):
        dts, mxr = _datos()
        sel = {'b': ['x', 'z']}

        with símismo.subTest(rel=False):
            dts.loc[codificar_coords(sel)] = -1
            mxr.loc[sel] = -1
            _prb_igl(dts, mxr)
        dts, mxr = _datos()

        with símismo.subTest(rel=True):
            dts.loc[codificar_coords(sel)] -= 1
            mxr.loc[sel] -= 1
            _prb_igl(dts, mxr)


class PruebaAritméticaLoc(unittest.TestCase):
    @unittest.skip('implementar')
    def test_aritméticaloc(símisom):
        pass


class PruebaPruebaAritméticaAugLoc(unittest.TestCase):
    @unittest.skip('implementar')
    def test_aritméticaaugloc(símisom):
        pass


class PruebaFuncs(unittest.TestCase):
    def test_combin(símismo):
        dts, mxr = _datos()
        otro = dts.copiar()
        otro.asignar_coords('b', ('u', 'v', 'w'))
        mxr_otro = mxr.copy()
        mxr_otro.coords['b'] = ['u', 'v', 'w']
        _prb_igl(combinar(otro, dts), mxr_otro.combine_first(mxr))

    def test_f_numpy(símismo):
        dts = _datos(False)
        dt1 = dts < 5
        dt2 = dts > 2
        _prb_igl(f_numpy(np.logical_or, dt1, dt2), np.logical_or(dt1.a_xarray(), dt2.a_xarray()))

    def test_máximo(símismo):
        dts, mxr = _datos()
        otro = dts + np.random.normal(size=dts.matr.shape)
        mxr_otro = otro.a_xarray()
        _prb_igl(máximo(dts, otro), np.maximum(mxr, mxr_otro))

    def test_mínimo(símismo):
        dts, mxr = _datos()
        otro = dts + np.random.normal(size=dts.matr.shape)
        mxr_otro = otro.a_xarray()
        _prb_igl(mínimo(dts, otro), np.minimum(mxr, mxr_otro))

    def test_donde(símismo):
        dts, mxr = _datos()
        _prb_igl(donde(dts > 4, dts, -1), xr.where(mxr > 4, mxr, -1))

    def test_lleno_como(símismo):
        dts = _datos(False)
        lleno = lleno_como(dts, 4)
        dts[:] = 4
        _datos_igls(lleno, dts, símismo, meta=True)
