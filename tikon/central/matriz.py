import functools
from typing import Any, Optional, Union, List

import numpy as np
import pandas as pd
import xarray as xr
from frozendict import frozendict


@functools.lru_cache
def _calc_índices(_dic, _coords, _dims):
    índices = []
    í_crds = {ll: list(range(len(v))) for ll, v in _coords.items()}
    for dm in _dims:
        if dm in _dic:
            v = _dic[dm]
            if isinstance(v, tuple):
                if v == tuple(range(_dic[dm][0], _dic[dm][-1] + 1)):
                    índices.append(slice(v[0], v[-1] + 1) if v != í_crds[dm] else slice(None))
                else:
                    índices.append(v)
            else:
                índices.append(v)
        else:
            índices.append(slice(None))
    return tuple(índices)


@functools.lru_cache
def _calc_índices_loc(coords, dic):
    return frozendict({
        dm: tuple(coords[dm].index(c) for c in (crds if isinstance(crds, (tuple, set, list)) else [crds]))
        for dm, crds in dic.items()
    })


@functools.lru_cache
def _proc_llave(dims, coords, llave):
    dims = tuple(dm for dm in dims if dm not in llave or not isinstance(llave[dm], int))
    coords = frozendict({
        dm: tuple(coords[dm][í] for í in llave[dm]) if dm in llave else coords[dm] for dm in dims
    })
    return dims, coords


class CoordsDatos(dict):
    def __init__(símismo, *args, **argsll):
        super().__init__(*args, **argsll)

    def __setitem__(símismo, llave, valor):
        raise ValueError(
            "No se pueden asignar coordenadas directamente en un objeto Datos. Llamar datos.asignar_coords en vez."
        )


class Loc(object):
    def __init__(símismo, datos):
        símismo.datos = datos

    def _índices(símismo, dic):
        if isinstance(dic, Datos):
            dic = dic.coords_internas
        return _calc_índices_loc(símismo.datos.coords_internas, dic)

    def __getitem__(símismo, itema):
        return símismo.datos[símismo._índices(itema)]

    def __setitem__(símismo, llave, valor):
        símismo.datos[símismo._índices(llave)] = valor


class Datos(object):
    def __init__(símismo, val, dims, coords, nombre=None, atribs=None, _verif=True, _conv_coords=None):

        if not isinstance(val, np.ndarray):
            if isinstance(val, (list, tuple)):
                val = np.array(val)
            else:
                val = np.full(shape=tuple(len(coords[dm]) for dm in dims), fill_value=val)

        símismo.matr = val
        símismo.dims = dims
        símismo._coords_internas = coords

        símismo._conv_coords = _conv_coords

        símismo.atribs = (atribs or {}).copy()
        símismo.nombre = nombre

        if _verif:
            símismo._verif_init()
        elif símismo._conv_coords is None:
            raise ValueError("Se debe especificar `_conv_coords` si `_verif_init===False`")

        símismo.loc = Loc(símismo)

    def _verif_init(símismo):
        símismo.dims = tuple(símismo.dims)
        símismo._conv_coords = {}
        símismo._coords_internas = símismo.codificar_coords(símismo._coords_internas)

        if set(símismo.dims) != set(símismo.coords_internas):
            raise ValueError(set(símismo.dims), set(símismo.coords_internas))
        frm = tuple(len(símismo.coords_internas[dm]) for dm in símismo.dims)
        if frm != símismo.matr.shape:
            raise ValueError(frm, símismo.matr.shape)

    @classmethod
    def de_xarray(cls, datos):
        coords = frozendict({
            ll: tuple(v.values if not np.issubdtype(v.values.dtype, np.datetime64) else pd.to_datetime(v.values))
            for ll, v in datos.coords.items()
        })
        return Datos(val=datos.values.copy(), dims=datos.dims, coords=coords, nombre=datos.name, atribs=datos.attrs)

    def a_xarray(símismo):
        return xr.DataArray(
            símismo.matr.copy(),
            coords=símismo.coords,
            dims=list(símismo.dims),
            name=símismo.nombre,
            attrs=símismo.atribs
        )

    def codificar_coords(símismo, coords: dict[str, Any]):
        return codificar_coords(coords, símismo)

    def _decodificar_coord(símismo, valor):
        def decodificar(v):
            return símismo._conv_coords[v] if v in símismo._conv_coords else v

        if isinstance(valor, (list, tuple)):
            return [decodificar(v) for v in valor]
        return decodificar(valor)

    def copiar(símismo):
        return Datos(símismo.matr.copy(), dims=símismo.dims, coords=símismo.coords_internas, nombre=símismo.nombre,
                     atribs=símismo.atribs, _conv_coords=símismo._conv_coords, _verif=False)

    def renombrar(símismo, cambios):
        copia = símismo.copiar()
        coords_final = dict(copia.coords_internas)
        for ant, nv in cambios.items():
            coords_final[nv] = coords_final.pop(ant)
        copia._coords_internas = frozendict(coords_final)
        copia.dims = tuple(cambios[dm] if dm in cambios else dm for dm in copia.dims)
        return copia

    def asignar_coords(símismo, eje, coords):
        símismo._coords_internas = frozendict({**símismo._coords_internas, **{
            eje: coords
        }})

    def llenar_nan(símismo, val):
        símismo.matr[np.isnan(símismo.matr)] = val
        return símismo

    def llenar_inf(símismo, val):
        símismo.matr[np.isinf(símismo.matr)] = val
        return símismo

    def nuevo_como(símismo, vals, excluir: Union[str, List[str]] = None):
        coords = símismo.coords_internas
        dims = símismo.dims
        if excluir:
            if isinstance(excluir, str):
                excluir = [excluir]

            coords = frozendict({ll: v for ll, v in coords.items() if ll not in excluir})
            dims = tuple(dm for dm in dims if dm not in excluir)

        return Datos(
            vals, dims=dims, coords=coords, nombre=símismo.nombre, atribs=símismo.atribs,
            _conv_coords=símismo._conv_coords, _verif=False
        )

    def transponer(símismo, dims):
        orden = [símismo.dims.index(d) for d in dims]
        return Datos(np.transpose(símismo.matr, orden), dims=dims, coords=símismo.coords_internas,
                     nombre=símismo.nombre,
                     atribs=símismo.atribs, _conv_coords=símismo._conv_coords, _verif=False)

    def expandir_dims(símismo, coords):
        if isinstance(coords, Datos):
            o_dims, o_coords = coords.dims, coords.coords_internas
        else:
            o_coords = coords
            o_dims = tuple(o_coords)
        return _expandir_dims(símismo, dims=o_dims, coords=o_coords)

    def dejar(símismo, dim):

        if len(símismo.coords_internas[dim]) != 1:
            raise ValueError('Dimensiones deben tener tamaño 1.')

        símismo.matr = símismo.matr.squeeze(símismo.dims.index(dim))
        símismo.dims = tuple(x for x in símismo.dims if x not in dim)
        símismo._coords_internas = frozendict({dm: símismo.coords_internas[dm] for dm in símismo.dims})
        símismo.loc = Loc(símismo)
        return símismo

    @property
    def coords_internas(símismo):
        return símismo._coords_internas

    @property
    def coords(símismo):
        return CoordsDatos({ll: símismo._decodificar_coord(v) for ll, v in símismo.coords_internas.items()})

    def _í_dims(símismo, dims):
        if isinstance(dims, str):
            return símismo.dims.index(dims)
        else:
            return tuple([símismo.dims.index(d) for d in dims])

    def _índices(símismo, dic):
        return _calc_índices(frozendict(dic), símismo.coords_internas, símismo.dims)

    def _proc_llave(símismo, llave):
        return _proc_llave(símismo.dims, símismo.coords_internas, frozendict(llave))

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
        if isinstance(itema, (dict, frozendict)):
            dims, coords = símismo._proc_llave(itema)
            return Datos(símismo.matr[símismo._índices(itema)], dims=dims, coords=coords, nombre=símismo.nombre,
                         atribs=símismo.atribs, _conv_coords=símismo._conv_coords, _verif=False)
        raise TypeError(type(itema))

    def __setitem__(símismo, llave, valor):
        if isinstance(valor, Datos):
            if isinstance(llave, (dict, frozendict)):
                dims, coords = símismo._proc_llave(llave)
            else:
                dims, coords = símismo.dims, símismo.coords_internas

            valor = _alinear_como_coords(dims=dims, coords=coords, otro=valor).matr

        if isinstance(llave, frozendict):
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
            coords[d] += [v for v in m.coords_internas[d] if v not in coords[d]]
        coords[d] = tuple(coords[d])

    _conv_coords = {c: v for m in matrs for c, v in m._conv_coords.items()}

    final = Datos(np.nan, dims=dims, coords=frozendict(coords), _conv_coords=_conv_coords, _verif=False)
    for m in matrs:
        final.loc[m.coords_internas] = m

    return final


def alinear(*datos):
    dts = _intersec_datos(*datos)
    return _redimensionar(*dts)


def alinear_2(dt1, dt2):
    if isinstance(dt2, Datos):
        dt1 = _expandir_dims(dt1, dims=dt2.dims, coords=dt2.coords_internas)
        dt2 = _expandir_dims(dt2, dims=dt1.dims, coords=dt1.coords_internas, guardar_orden=False)
        if dt1.coords_internas == dt2.coords_internas:
            return dt1, dt2.matr
        else:
            crds = _intersec_coords(dt1.coords_internas, dt2.coords_internas)
            return dt1.loc[crds], dt2.loc[crds].matr
    return dt1, dt2


def alinear_como(como, otro):
    return _alinear_como_coords(dims=como.dims, coords=como.coords_internas, otro=otro)


def _alinear_como_coords(dims, coords, otro):
    otro = _expandir_dims(otro, dims=dims, coords=coords, guardar_orden=False)
    if otro.coords_internas == coords:
        return otro
    else:
        return otro.loc[coords]


def _redimensionar(*args):
    datos = [x for x in args if isinstance(x, Datos)]

    dims = tuple(dict.fromkeys(dm for dt in datos for dm in dt.dims))
    coords = frozendict({dm: next(dt.coords_internas[dm] for dt in datos if dm in dt.coords_internas) for dm in dims})

    return [_expandir_dims(x, dims, coords, guardar_orden=False) if isinstance(x, Datos) else x for x in args]


def _redimensionar_como(plntll, *args):
    return [_expandir_dims(x, plntll.dims, plntll.coords_internas) if isinstance(x, Datos) else x for x in args]


def _intersec_datos(*args):
    datos = [x for x in args if isinstance(x, Datos)]

    c_final = _intersec_coords(*[dt.coords_internas for dt in datos])
    return [
        x.loc[frozendict({dm: tuple(c) for dm, c in c_final.items() if dm in x.coords_internas})] if isinstance(x,
                                                                                                                Datos) else x
        for x in args
    ]


@functools.lru_cache
def _intersec_coords(*args):
    dims = set(dm for crd in args for dm in crd)
    c_final = frozendict({
        dm: tuple(dict.fromkeys([
            c for crds in args if dm in crds for c in crds[dm]
            if all(c in crds_o[dm] for crds_o in args if dm in crds_o)
        ]))
        for dm in dims
    })

    return c_final


@functools.lru_cache
def _gen_f_expandir_dims(dims_datos, coords_datos, dims, coords, guardar_orden):
    dims_prior, extras = (dims_datos, dims) if guardar_orden else (dims, dims_datos)
    d_final = tuple([*dims_prior, *(d for d in extras if d not in dims_prior)])

    if dims_datos != d_final:
        if set(dims_datos) != set(d_final):
            # Agregar dims
            c_final = {dm: list(coords_datos[dm]) if dm in coords_datos else coords[dm] for dm in d_final}
            frm_matr = tuple(len(v) if ll in coords_datos else 1 for ll, v in c_final.items())
            frm_final = tuple(len(v) for v in c_final.values())

            def f(datos):
                # Copia de `broadcast_to` necesaria para evitar error Numpy con Datos.matr += V después
                datos = Datos(np.broadcast_to(datos.matr.reshape(frm_matr), frm_final).copy(), d_final,
                              coords=frozendict(
                                  {ll: tuple(v) if isinstance(v, list) else v for ll, v in c_final.items()}),
                              nombre=datos.nombre, atribs=datos.atribs, _conv_coords=datos._conv_coords, _verif=False)
                # Reordenar dims
                return datos.transponer(d_final)
        else:
            def f(datos):
                # Reordenar dims
                return datos.transponer(d_final)
    else:
        def f(datos):
            return datos
    return f


def _expandir_dims(datos, dims, coords, guardar_orden=True):
    f = _gen_f_expandir_dims(datos.dims, datos.coords_internas, dims, coords, guardar_orden=guardar_orden)
    return f(datos)


def codificar_coords(coords, datos: Optional[Datos] = None):
    return frozendict({
        ll: tuple(
            _codificar_coord(o, datos) for o in v
        ) if isinstance(v, (range, tuple, list, set, np.ndarray, pd.Index)) else (_codificar_coord(v, datos),) for
        ll, v in coords.items()
    })


def _codificar_coord(valor, datos):
    if isinstance(valor, (str, int, np.number)):
        return valor

    if type(valor) is pd.Timestamp:
        código = valor.toordinal()
    else:
        código = id(valor)
    if datos:
        datos._conv_coords[código] = valor
    return código
