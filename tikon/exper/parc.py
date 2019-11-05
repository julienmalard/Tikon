import os
from functools import partial

import numpy as np
import pyproj
import shapefile
import xarray as xr
from geopy.distance import distance
from shapely.geometry import Polygon
from shapely.ops import transform
from tikon.result.utils import EJE_PARC, EJE_DEST, EJE_COORD


class Parcela(object):
    def __init__(símismo, nombre, geom):
        símismo.nombre = nombre

        símismo.geom = geom or GeomParcela()


class ParcelaShp(Parcela):
    def __init__(símismo, archivo, nombre=None):
        nombre = nombre or os.path.splitext(os.path.split(archivo)[1])[0]
        coords = shapefile.Reader(archivo).shapeRecords()[0].shape.__geo_interface__['geometry']
        polígono = Polygon(coords)
        geom = GeomParcela(centroide=polígono.centroid, superficie=_área_de_polígono(polígono), coords=coords)
        super().__init__(nombre, geom=geom)


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
            centroide = centroide or polígono.centroid
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

    superficies = xr.DataArray([prc.geom.superficie for prc in parcelas], coords={EJE_PARC: nombres}, dims=[EJE_PARC])
    elevs = xr.DataArray([prc.geom.elevación for prc in parcelas], coords={EJE_PARC: nombres}, dims=[EJE_PARC])
    cntrds = xr.DataArray(
        [prc.geom.centroide for prc in parcelas],
        coords={EJE_PARC: nombres, EJE_COORD: ['lat', 'lon']},
        dims=[EJE_PARC, EJE_COORD]
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

    return transform(proj, polígono).area
