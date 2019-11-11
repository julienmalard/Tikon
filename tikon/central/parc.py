from functools import partial

import numpy as np
import pyproj
import xarray as xr
from geopy.distance import distance
from shapely.geometry import Polygon
from shapely.ops import transform
from tikon.central.utils import EJE_PARC, EJE_DEST, EJE_COORD


class Parcela(object):
    def __init__(símismo, nombre, geom=None):
        símismo.nombre = nombre

        símismo.geom = geom or GeomParcela()

    def __str__(símismo):
        return símismo.nombre


class GrupoParcelas(object):
    def __init__(símismo, parcelas):
        símismo.parcelas = parcelas


class GeomParcela(object):
    def __init__(símismo, centroide=None, elev=None, superficie=None, coords=None):
        """

        Parameters
        ----------
        centroide
        elev
        superficie
        coords:
            **Deben** ser en formato WGS-84 (EPSG:4326). Si no sabes lo que es probablement no tienes que preocuparte.
        """
        if coords is not None:
            polígono = Polygon(coords)
            superficie = superficie or _área_de_polígono(polígono)
            centroide = centroide or (polígono.centroid.xy[0][0], polígono.centroid.xy[1][0])
        else:
            centroide = centroide or (11.0025, 76.9656)
            superficie = superficie or 1
            coords = [centroide]

        símismo.coords = coords
        símismo.superficie = superficie
        símismo.centroide = centroide
        símismo.elev = np.nan if elev is None else elev


def _controles_parc(parcelas):
    nombres = [prc.nombre for prc in parcelas]

    superficies = xr.DataArray(
        [prc.geom.superficie for prc in parcelas], coords={EJE_PARC: nombres}, dims=[EJE_PARC], attrs={'unids': 'ha'}
    )
    elevs = xr.DataArray(
        [prc.geom.elev for prc in parcelas], coords={EJE_PARC: nombres}, dims=[EJE_PARC], attrs={'unids': 'm'}
    )
    cntrds = xr.DataArray(
        [prc.geom.centroide for prc in parcelas],
        coords={EJE_PARC: nombres, EJE_COORD: ['lat', 'lon']},
        dims=[EJE_PARC, EJE_COORD],
        attrs={'unids': 'grados'}
    )
    distancias = xr.apply_ufunc(_dstn, cntrds, cntrds.rename({EJE_PARC: EJE_DEST}), input_core_dims=[[EJE_COORD]] * 2)

    return {
        'parcelas': nombres,
        'superficies': superficies,
        'centroides': cntrds,
        'distancias': distancias,
        'elevaciones': elevs
    }


def _dstn(a, b):
    return np.vectorize(lambda de, hacia: distance(de, hacia).m, signature='(n),(n)->()')(a, b)


def _área_de_polígono(polígono):
    proj = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(
            proj='aea',
            lat_1=polígono.bounds[1],
            lat_2=polígono.bounds[3]
        )
    )

    return transform(proj, polígono).area / 10000
