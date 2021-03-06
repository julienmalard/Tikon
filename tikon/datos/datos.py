import numpy as np
import pandas as pd
import xarray as xr


class Loc(object):
    def __init__(símismo, datos):
        símismo.datos = datos

    def _índices(símismo, dic):
        if isinstance(dic, Datos):
            dic = dic.coords
        return {
            dm: [símismo.datos.coords[dm].index(c) for c in (crds if isinstance(crds, (list, set)) else [crds])]
            for dm, crds in dic.items()
        }

    def __getitem__(símismo, itema):
        return símismo.datos[símismo._índices(itema)]

    def __setitem__(símismo, llave, valor):
        símismo.datos[símismo._índices(llave)] = valor


class Datos(object):
    def __init__(símismo, val, dims, coords, nombre=None, atribs=None, verif=True):

        if not isinstance(val, np.ndarray):
            if isinstance(val, (list, tuple)):
                val = np.array(val)
            else:
                val = np.full(shape=tuple(len(coords[dm]) for dm in dims), fill_value=val)

        símismo.matr = val
        símismo.dims = tuple(dims) if verif else dims
        símismo.coords = {ll: list(v) for ll, v in coords.items()} if verif else coords.copy()

        símismo.atribs = (atribs or {}).copy()
        símismo.nombre = nombre

        símismo.loc = Loc(símismo)

        if verif:
            if set(símismo.dims) != set(símismo.coords):
                raise ValueError(set(símismo.dims), set(símismo.coords))
            frm = tuple(len(símismo.coords[dm]) for dm in símismo.dims)
            if frm != val.shape:
                raise ValueError(frm, val.shape)

    @classmethod
    def de_xarray(cls, datos):
        coords = {
            ll: list(v.values if not np.issubdtype(v.values.dtype, np.datetime64) else pd.to_datetime(v.values))
            for ll, v in datos.coords.items()
        }
        return Datos(val=datos.values.copy(), dims=datos.dims, coords=coords, nombre=datos.name, atribs=datos.attrs)

    def a_xarray(símismo):
        return xr.DataArray(
            símismo.matr.copy(), coords=símismo.coords, dims=símismo.dims, name=símismo.nombre, attrs=símismo.atribs
        )

    def copiar(símismo):
        return Datos(
            símismo.matr.copy(), dims=símismo.dims, coords=símismo.coords, nombre=símismo.nombre, atribs=símismo.atribs,
            verif=False
        )

    def renombrar(símismo, cambios):
        copia = símismo.copiar()
        for ant, nv in cambios.items():
            copia.coords[nv] = copia.coords.pop(ant)
            copia.dims = tuple(cambios[dm] if dm in cambios else dm for dm in copia.dims)
        return copia

    def llenar_nan(símismo, val):
        símismo.matr[np.isnan(símismo.matr)] = val
        return símismo

    def llenar_inf(símismo, val):
        símismo.matr[np.isinf(símismo.matr)] = val
        return símismo

    def nuevo_como(símismo, vals, excluir=None):
        coords = símismo.coords
        dims = símismo.dims
        if excluir:
            if isinstance(excluir, str):
                excluir = [excluir]

            coords = {ll: v for ll, v in coords.items() if ll not in excluir}
            dims = tuple(dm for dm in dims if dm not in excluir)

        return Datos(vals, dims=dims, coords=coords, nombre=símismo.nombre, atribs=símismo.atribs, verif=False)

    def transposar(símismo, dims):
        orden = [símismo.dims.index(d) for d in dims]
        return Datos(
            np.transpose(símismo.matr, orden), dims=dims, coords=símismo.coords,
            nombre=símismo.nombre, atribs=símismo.atribs, verif=False
        )

    def expandir_dims(símismo, coords):
        if isinstance(coords, Datos):
            o_dims, o_coords = coords.dims, coords.coords
        else:
            o_coords = coords
            o_dims = list(o_coords)
        return _expandir_dims(símismo, dims=o_dims, coords=o_coords)

    def dejar(símismo, dim):

        if len(símismo.coords[dim]) != 1:
            raise ValueError('Dimensiones deben tener tamaño 1.')

        símismo.matr = símismo.matr.squeeze(símismo.dims.index(dim))
        símismo.dims = tuple(x for x in símismo.dims if x not in dim)
        símismo.coords = {dm: símismo.coords[dm] for dm in símismo.dims}
        return símismo

    def _í_dims(símismo, dims):
        if isinstance(dims, str):
            return símismo.dims.index(dims)
        else:
            return tuple([símismo.dims.index(d) for d in dims])

    def _índices(símismo, dic):
        índices = []
        í_crds = {ll: list(range(len(v))) for ll, v in símismo.coords.items()}
        for dm in símismo.dims:
            if dm in dic:
                v = dic[dm]
                if isinstance(v, list):
                    if v == list(range(dic[dm][0], dic[dm][-1] + 1)):
                        índices.append(slice(v[0], v[-1] + 1) if v != í_crds[dm] else slice(None))
                    else:
                        índices.append(v)
                else:
                    índices.append(v)
            else:
                índices.append(slice(None))
        return tuple(índices)

    def _proc_llave(símismo, llave):
        dims = tuple(dm for dm in símismo.dims if dm not in llave or not isinstance(llave[dm], int))
        coords = {
            dm: [símismo.coords[dm][í] for í in llave[dm]] if dm in llave else símismo.coords[dm] for dm in dims
        }
        return dims, coords

    def redond(símismo, n=None):
        return símismo.nuevo_como(np.round(símismo.matr, decimals=n or 0))

    def f_eje(símismo, f, dim, *args, **argsll):
        if dim is not None:
            vals = f(símismo.matr, axis=símismo._í_dims(dim), *args, **argsll)

            # Algunas funciones como `np.take_along_axis` no destruyen el eje especificado
            excluir = dim if vals.shape != símismo.matr.shape else None
            return símismo.nuevo_como(vals, excluir=excluir)
        return f(símismo.matr)

    def prod(símismo, dim=None):
        return símismo.f_eje(np.ndarray.prod, dim=dim)

    def suma(símismo, dim=None):
        return símismo.f_eje(np.ndarray.sum, dim=dim)

    def cualquier(símismo, dim=None):
        return símismo.f_eje(np.ndarray.any, dim=dim)

    def donde(símismo, cond, otro):
        m_cond = alinear_como(símismo, cond).matr if isinstance(cond, Datos) else cond
        m_otro = alinear_como(símismo, otro).matr if isinstance(otro, Datos) else otro
        return símismo.nuevo_como(np.where(m_cond, símismo.matr, m_otro))

    def f(símismo, f, *args, **argsll):
        copia = símismo.copiar()
        copia.fi(f, *args, **argsll)
        return copia

    def fi(símismo, f, *args, **argsll):
        símismo.matr[:] = f(símismo.matr, *args, **argsll)
        return símismo

    def __add__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr + y)

    def __sub__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr - y)

    def __mul__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr * y)

    def __mod__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr % y)

    def __truediv__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr / y)

    def __floordiv__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr // y)

    def __pow__(símismo, pot, módulo=None):
        x, y = alinear_2(símismo, pot)
        return x.nuevo_como(x.matr ** y)

    def __and__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr & y)

    def __or__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr | y)

    def __radd__(símismo, otro):
        return símismo + otro

    def __rsub__(símismo, otro):
        return -símismo + otro

    def __rmul__(símismo, otro):
        return símismo * otro

    def __rmod__(símismo, otro):
        otro = símismo.nuevo_como(otro)
        return otro % símismo

    def __rtruediv__(símismo, otro):
        return símismo.nuevo_como(1 / símismo.matr) * otro

    def __rfloordiv__(símismo, otro):
        return (otro / símismo).f(np.floor)

    def __rpow__(símismo, otro):
        otro = símismo.nuevo_como(otro)
        return otro % símismo

    def __rand__(símismo, otro):
        return símismo & otro

    def __ror__(símismo, otro):
        raise símismo | otro

    def __eq__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr == y)

    def __gt__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr > y)

    def __lt__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr < y)

    def __ge__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr >= y)

    def __le__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr <= y)

    def __ne__(símismo, otro):
        x, y = alinear_2(símismo, otro)
        return x.nuevo_como(x.matr != y)

    def __iadd__(símismo, otro):
        if isinstance(otro, Datos):
            res = símismo + otro
            símismo.loc[res] = res
        else:
            símismo.matr += otro
        return símismo

    def __isub__(símismo, otro):
        if isinstance(otro, Datos):
            res = símismo - otro
            símismo.loc[res] = res
        else:
            símismo.matr -= otro
        return símismo

    def __imul__(símismo, otro):
        if isinstance(otro, Datos):
            res = símismo * otro
            símismo.loc[res] = res
        else:
            símismo.matr *= otro
        return símismo

    def __imod__(símismo, otro):
        if isinstance(otro, Datos):
            res = símismo % otro
            símismo.loc[res] = res
        else:
            símismo.matr %= otro
        return símismo

    def __itruediv__(símismo, otro):
        if isinstance(otro, Datos):
            res = símismo / otro
            símismo.loc[res] = res
        else:
            símismo.matr /= otro
        return símismo

    def __ifloordiv__(símismo, otro):
        if isinstance(otro, Datos):
            res = símismo // otro
            símismo.loc[res] = res
        else:
            símismo.matr //= otro
        return símismo

    def __ipow__(símismo, pot, módulo=None):
        if isinstance(pot, Datos):
            res = símismo ** pot
            símismo.loc[res] = res
        else:
            símismo.matr **= pot
        return símismo

    def __abs__(símismo):
        return símismo.nuevo_como(np.abs(símismo.matr))

    def __neg__(símismo):
        return símismo.nuevo_como(-símismo.matr)

    def __invert__(símismo):
        return símismo.nuevo_como(~símismo.matr)

    def __getitem__(símismo, itema):
        if isinstance(itema, dict):
            dims, coords = símismo._proc_llave(itema)
            return Datos(
                símismo.matr[símismo._índices(itema)], dims=dims, coords=coords,
                nombre=símismo.nombre, atribs=símismo.atribs, verif=False
            )
        raise TypeError(type(itema))

    def __setitem__(símismo, llave, valor):
        if isinstance(valor, Datos):
            if isinstance(llave, dict):
                dims, coords = símismo._proc_llave(llave)
            else:
                dims, coords = símismo.dims, símismo.coords

            valor = _alinear_como_coords(dims=dims, coords=coords, otro=valor).matr

        if isinstance(llave, dict):
            símismo.matr[símismo._índices(llave)] = valor
        else:
            símismo.matr[llave] = valor


def f_numpy(f, *datos, **argsll):
    dts = alinear(*datos)
    plntll = next((dt for dt in dts if isinstance(dt, Datos)), None)
    args = [dt.matr if isinstance(dt, Datos) else dt for dt in dts]
    if plntll:
        return plntll.nuevo_como(f(*args, **argsll))
    else:
        return f(*dts, **argsll)


def máximo(x, y):
    return f_numpy(np.maximum, x, y)


def mínimo(x, y):
    return f_numpy(np.minimum, x, y)


def donde(cond, x, y):
    return f_numpy(np.where, cond, x, y)


def lleno_como(otro, valor, tipod=None):
    return otro.nuevo_como(np.full(otro.matr.shape, valor, dtype=tipod))


def combinar(*matrs):
    dims = matrs[0].dims
    coords = {}

    for d in dims:
        coords[d] = []
        for m in matrs:
            coords[d] += [v for v in m.coords[d] if v not in coords[d]]

    final = Datos(np.nan, dims=dims, coords=coords)
    for m in matrs:
        final.loc[m.coords] = m

    return final


def alinear(*datos):
    dts = _intersec_datos(*datos)
    return _redimensionar(*dts)


def alinear_2(dt1, dt2):
    if isinstance(dt2, Datos):
        dt1 = _expandir_dims(dt1, dims=dt2.dims, coords=dt2.coords)
        dt2 = _expandir_dims(dt2, dims=dt1.dims, coords=dt1.coords, guardar_orden=False)
        if dt1.coords == dt2.coords:
            return dt1, dt2.matr
        else:
            crds = _intersec_coords(dt1.coords, dt2.coords)
            return dt1.loc[crds], dt2.loc[crds].matr
    return dt1, dt2


def alinear_como(como, otro):
    return _alinear_como_coords(dims=como.dims, coords=como.coords, otro=otro)


def _alinear_como_coords(dims, coords, otro):
    otro = _expandir_dims(otro, dims=dims, coords=coords, guardar_orden=False)
    if otro.coords == coords:
        return otro
    else:
        return otro.loc[coords]


def _redimensionar(*args):
    datos = [x for x in args if isinstance(x, Datos)]

    dims = list(dict.fromkeys(dm for dt in datos for dm in dt.dims))
    coords = {dm: next(dt.coords[dm] for dt in datos if dm in dt.coords) for dm in dims}

    return [_expandir_dims(x, dims, coords, guardar_orden=False) if isinstance(x, Datos) else x for x in args]


def _redimensionar_como(plntll, *args):
    return [_expandir_dims(x, plntll.dims, plntll.coords) if isinstance(x, Datos) else x for x in args]


def _intersec_datos(*args):
    datos = [x for x in args if isinstance(x, Datos)]

    c_final = _intersec_coords(*[dt.coords for dt in datos])
    return [
        x.loc[{dm: c for dm, c in c_final.items() if dm in x.coords}] if isinstance(x, Datos) else x for x in args
    ]


def _intersec_coords(*args):
    dims = set(dm for crd in args for dm in crd)
    c_final = {
        dm: list(dict.fromkeys([
            c for crds in args if dm in crds for c in crds[dm]
            if all(c in crds_o[dm] for crds_o in args if dm in crds_o)
        ]))
        for dm in dims
    }

    return c_final


def _expandir_dims(datos, dims, coords, guardar_orden=True):
    dims_prior, extras = (datos.dims, dims) if guardar_orden else (dims, datos.dims)
    d_final = tuple([*dims_prior, *(d for d in extras if d not in dims_prior)])

    if datos.dims != d_final:
        if set(datos.dims) != set(d_final):
            # Agregar dims
            c_final = {dm: datos.coords[dm] if dm in datos.coords else coords[dm] for dm in d_final}
            frm_matr = tuple(len(v) if ll in datos.coords else 1 for ll, v in c_final.items())
            frm_final = tuple(len(v) for v in c_final.values())

            # Copia de `broadcast_to` necesaria para evitar error Numpy con Datos.matr += V después
            datos = Datos(
                np.broadcast_to(datos.matr.reshape(frm_matr), frm_final).copy(), d_final,
                coords=c_final, nombre=datos.nombre, atribs=datos.atribs
            )
        # Reordenar dims
        datos = datos.transposar(d_final)

    return datos
