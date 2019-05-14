import numpy as np
import scipy.interpolate as interp

from tikon.estruc.tiempo import EjeTiempo
from tikon.result.dims import Coord, Dims


class Matriz(object):
    def __init__(símismo, dims):

        símismo.dims = dims
        símismo._matr = np.zeros(dims.frm())

    def poner_valor(símismo, vals, rel=False, índs=None):
        if índs is None:
            if rel:
                símismo._matr[:] += vals
            else:
                símismo._matr[:] = vals
        else:
            if rel:
                símismo._matr[símismo.rebanar(índs)] += vals
            else:
                símismo._matr[símismo.rebanar(índs)] = vals

    def obt_valor(símismo, índs=None):
        if índs is None:
            return símismo._matr
        else:
            return símismo._matr[símismo.rebanar(índs)]

    def sumar(símismo, eje):
        í_eje = símismo.dims.í_eje(eje)
        return símismo._matr.sum(axis=í_eje)

    def rebanar(símismo, índs):
        return símismo.dims.rebanar(índs)

    def reinic(símismo):
        símismo._matr[:] = 0

    def ejes(símismo):
        return símismo.dims.ejes()

    def í_eje(símismo, eje):
        return símismo.dims.í_eje(eje)

    def n_ejes(símismo):
        return símismo.dims.n_ejes()

    def iter_índs(símismo, excluir=None):
        return símismo.dims.iter_índs(excluir=excluir)

    def a_dic(símismo):
        return {'dims': símismo.dims.a_dic(), 'val': símismo._matr.tolist()}

    @classmethod
    def de_dic(cls, dic):
        m = cls(Dims.de_dic(dic['dims']))
        m.poner_valor(np.array(dic['val']))
        return m


class MatrizTiempo(Matriz):
    def __init__(símismo, dims, eje_tiempo):
        """

        Parameters
        ----------
        dims: Dims
        eje_tiempo: EjeTiempo

        """
        símismo.eje_tiempo = eje_tiempo
        super().__init__(dims={'días': Coord(eje_tiempo.días)} + dims)

    def obt_val_t(símismo, t, índs=None):
        if not isinstance(t, EjeTiempo):
            t = EjeTiempo(días=t)

        días_act = símismo.eje_tiempo.días
        índs_t = símismo.eje_tiempo.índices(t)
        eje = símismo.í_eje('días')

        f = interp.interp1d(x=días_act, y=símismo.obt_valor(índs), axis=eje)
        return f(índs_t)

    def a_dic(símismo):
        dic = super().a_dic()
        dic['tiempo'] = símismo.eje_tiempo.a_dic()
        return dic

    @classmethod
    def de_dic(cls, dic):
        dims = dic['dims'].copy()
        dims.pop('días')
        m = cls(dims=dims, eje_tiempo=EjeTiempo.de_dic(dic['tiempo']))
        m.poner_valor(np.array(dic['val']))
