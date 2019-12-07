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
            dm: [símismo.datos.coords[dm].index(c) for c in (crds if isinstance(crds, list) else [crds])]
            for dm, crds in dic.items()
        }

    def __getitem__(símismo, itema):
        return símismo.datos[símismo._índices(itema)]

    def __setitem__(símismo, llave, valor):
        símismo.datos[símismo._índices(llave)] = valor


class Datos(object):
    def __init__(símismo, val, dims, coords, nombre=None, atribs=None):

        if not isinstance(val, np.ndarray):
            if isinstance(val, (list, tuple)):
                val = np.array(val)
            else:
                val = np.full(shape=tuple(len(coords[dm]) for dm in dims), fill_value=val)

        símismo.matr = val
        símismo.dims = tuple(dims)
        símismo.coords = {ll: list(v) for ll, v in coords.items()}

        if set(símismo.dims) != set(símismo.coords):
            raise ValueError(set(símismo.dims), set(símismo.coords))
        frm = tuple(len(símismo.coords[dm]) for dm in símismo.dims)
        if frm != val.shape:
            raise ValueError(frm, val.shape)

        símismo.atribs = (atribs or {}).copy()
        símismo.nombre = nombre

        símismo.loc = Loc(símismo)

    @classmethod
    def de_xarray(cls, datos):
        coords = {
            ll: list(v.values if not np.issubdtype(v.values.dtype, np.datetime64) else pd.to_datetime(v.values))
            for ll, v in datos.coords.items()
        }
        return Datos(val=datos.values, dims=datos.dims, coords=coords, nombre=datos.name, atribs=datos.attrs)

    def a_xarray(símismo):
        return xr.DataArray(
            símismo.matr, coords=símismo.coords, dims=símismo.dims, name=símismo.nombre, attrs=símismo.atribs
        )

    def copiar(símismo):
        return Datos(
            símismo.matr.copy(), dims=símismo.dims, coords=símismo.coords, nombre=símismo.nombre, atribs=símismo.atribs
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

    def nuevo_como(símismo, vals, excluir=None):
        coords = símismo.coords
        dims = símismo.dims
        if excluir:
            if isinstance(excluir, str):
                excluir = [excluir]

            coords = {ll: v for ll, v in coords.items() if ll not in excluir}
            dims = tuple(dm for dm in dims if dm not in excluir)

        return Datos(vals, dims=dims, coords=coords, nombre=símismo.nombre, atribs=símismo.atribs)

    def transposar(símismo, dims):
        orden = [símismo.dims.index(d) for d in dims]
        return Datos(
            np.transpose(símismo.matr, orden), dims=dims, coords=símismo.coords,
            nombre=símismo.nombre, atribs=símismo.atribs
        )

    def expandir_dims(símismo, coords):
        return _expandir_dims(símismo, coords)

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

    def alinear(símismo, otro):
        copia = símismo.copiar()
        if isinstance(otro, Datos):
            if copia.dims != otro.dims:
                if set(copia.dims) != set(otro.dims):
                    # Agregar dims
                    copia = _expandir_dims(copia, otro)
                    otro = _expandir_dims(otro, copia)
                # Reordenar dims
                otro = otro.transposar(copia.dims)

            if copia.coords == otro.coords:
                return copia, otro.matr
            else:
                c_final = {
                    ll: [x for x in v if x in otro.coords[ll]] for ll, v in copia.coords.items() if ll in otro.coords
                }
                return copia.loc[c_final], otro.loc[c_final].matr

        return copia, otro

    def f_eje(símismo, f, dim, *args, **argsll):
        if dim is not None:
            vals = f(símismo.matr, axis=símismo._í_dims(dim), *args, **argsll)
            return símismo.nuevo_como(vals, excluir=dim if vals.shape != símismo.matr.shape else None)
        return f(símismo.matr)

    def prod(símismo, dim=None):
        return símismo.f_eje(np.ndarray.prod, dim=dim)

    def suma(símismo, dim=None):
        return símismo.f_eje(np.ndarray.sum, dim=dim)

    def qualquier(símismo, dim=None):
        return símismo.f_eje(np.ndarray.any, dim=dim)

    def donde(símismo, cond, otro):
        matrs = _extract_matrs(cond, símismo, otro)[1]
        return símismo.nuevo_como(np.where(*matrs))

    def f(símismo, f, *args, **argsll):
        copia = símismo.copiar()
        copia.fi(f, *args, **argsll)
        return copia

    def fi(símismo, f, *args, **argsll):
        símismo.matr[:] = f(símismo.matr, *args, **argsll)
        return símismo

    def __add__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr += y
        return x

    def __sub__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr -= y
        return x

    def __mul__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr *= y
        return x

    def __mod__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr %= y
        return x

    def __truediv__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr /= y
        return x

    def __floordiv__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr //= y
        return x

    def __pow__(símismo, pot, módulo=None):
        x, y = símismo.alinear(pot)
        x.matr **= y
        return x

    def __and__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr &= y
        return x

    def __or__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr |= y
        return x

    def __radd__(símismo, otro):
        return símismo + otro

    def __rsub__(símismo, otro):
        return -símismo + otro

    def __rmul__(símismo, otro):
        return símismo * otro

    def __rtruediv__(símismo, otro):
        return símismo.nuevo_como(1 / símismo.matr) * otro

    def __rfloordiv__(símismo, otro):
        return (otro / símismo).f(np.floor)

    def __eq__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr = x.matr == y
        return x

    def __gt__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr = x.matr > y
        return x

    def __lt__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr = x.matr < y
        return x

    def __ge__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr = x.matr >= y
        return x

    def __le__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr = x.matr <= y
        return x

    def __ne__(símismo, otro):
        x, y = símismo.alinear(otro)
        x.matr = x.matr != y
        return x

    def __iadd__(símismo, otro):
        if isinstance(otro, Datos):
            return símismo + otro
        símismo.matr += otro
        return símismo

    def __isub__(símismo, otro):
        if isinstance(otro, Datos):
            return símismo - otro
        símismo.matr -= otro
        return símismo

    def __imul__(símismo, otro):
        if isinstance(otro, Datos):
            return símismo * otro
        símismo.matr *= otro
        return símismo

    def __imod__(símismo, otro):
        if isinstance(otro, Datos):
            return símismo % otro
        símismo.matr %= otro
        return símismo

    def __itruediv__(símismo, otro):
        if isinstance(otro, Datos):
            return símismo / otro
        símismo.matr /= otro
        return símismo

    def __ifloordiv__(símismo, otro):
        if isinstance(otro, Datos):
            return símismo // otro
        símismo.matr //= otro
        return símismo

    def __ipow__(símismo, pot, módulo=None):
        if isinstance(pot, Datos):
            return símismo ** pot
        símismo.matr **= pot
        return símismo

    def __abs__(símismo):
        return símismo.nuevo_como(np.abs(símismo.matr))

    def __floor__(símismo):
        return símismo.nuevo_como(np.floor(símismo.matr))

    def __ceil__(símismo):
        return símismo.nuevo_como(np.ceil(símismo.matr))

    def __neg__(símismo):
        return símismo.nuevo_como(-símismo.matr)

    def __invert__(símismo):
        return símismo.nuevo_como(~símismo.matr)

    def __getitem__(símismo, itema):
        if isinstance(itema, dict):
            dims = tuple(dm for dm in símismo.dims if dm not in itema or not isinstance(itema[dm], int))
            coords = {
                dm: [símismo.coords[dm][í] for í in itema[dm]] if dm in itema else símismo.coords[dm] for dm in dims
            }
            return Datos(
                símismo.matr[símismo._índices(itema)], dims=dims, coords=coords,
                nombre=símismo.nombre, atribs=símismo.atribs
            )
        raise TypeError(type(itema))

    def __setitem__(símismo, llave, valor):
        if isinstance(valor, Datos):
            if valor.dims != símismo.dims:
                if set(símismo.dims) != set(valor.dims):
                    # Agregar dims
                    valor = _expandir_dims(valor, símismo[llave])
                # Reordenar dims
                valor = valor.transposar(símismo.dims)
            valor = valor.matr
        if isinstance(llave, dict):
            símismo.matr[símismo._índices(llave)] = valor
        else:
            símismo.matr[llave] = valor


def f_numpy(f, *args, **argsll):
    plntll, matrs = _extract_matrs(*args)
    if plntll:
        return plntll.nuevo_como(f(*matrs, **argsll))
    else:
        return f(*matrs, **argsll)


def máximo(x, y):
    return f_numpy(np.maximum, x, y)


def mínimo(x, y):
    return f_numpy(np.minimum, x, y)


def donde(cond, x, y):
    return f_numpy(np.where, cond, x, y)


def lleno_como(otro, valor, tipod='int'):
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


def _extract_matrs(*args):
    l_datos = [x for x in args if isinstance(x, Datos)]
    # Por el momento tomamos la matriz con más coordinadas como plantilla. Para ser más universal tendríamos que
    # alinear todas las matrices.
    plntll = sorted(l_datos, key=lambda x: -len(x.dims))[0] if l_datos else None
    if plntll:
        matrs = [plntll.alinear(x)[1] if isinstance(x, Datos) else x for x in args]
    else:
        matrs = [x.matr if isinstance(x, Datos) else x for x in args]
    return plntll, matrs


def _expandir_dims(princ, otra):
    if isinstance(otra, Datos):
        o_dims, o_coords = otra.dims, otra.coords
    else:
        o_coords = otra
        o_dims = list(o_coords)

    d_final = tuple([*princ.dims, *(d for d in o_dims if d not in princ.dims)])
    c_final = {dm: princ.coords[dm] if dm in princ.coords else o_coords[dm] for dm in d_final}
    frm_matr = tuple(len(v) if ll in princ.coords else 1 for ll, v in c_final.items())
    frm_final = tuple(len(v) for v in c_final.values())

    # Copia de `broadcast_to` necesaria para evitar error Numpy con Datos.matr += V después
    return Datos(
        np.broadcast_to(princ.matr.reshape(frm_matr), frm_final).copy(), d_final,
        coords=c_final, nombre=princ.nombre, atribs=princ.atribs
    )
