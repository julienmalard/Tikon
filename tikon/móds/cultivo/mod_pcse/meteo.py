import numpy as np
import pandas as pd
from pcse.base import WeatherDataProvider, WeatherDataContainer
from pcse.db import NASAPowerWeatherDataProvider
from pcse.util import reference_ET

conv_nombres = {
    'temp_máx': 'TMAX', 'temp_mín': 'TMIN', 'precip': 'RAIN', 'temp_prom': 'TEMP', 'cob_nieve': 'SNOWDEPTH',
    'rad_solar': 'IRRAD', 'vap': 'VAP', 'veloc_viento': 'WIND', 'hum_rel': 'RHUM'
}
conv_inv = {v: ll for ll, v in conv_nombres.items()}
convs_unids = {
    "rad_solar": 1000,  # kJ/m2/día -> J/m2/día
    "vap": 10,  # kPa -> hPa
    "precip": 0.10,  # mm -> cm
}


class ProveedorMeteoPCSEPandas(NASAPowerWeatherDataProvider):
    angstA = 0.29
    angstB = 0.49

    def __init__(símismo, bd_pandas, lat, lon, elev):
        WeatherDataProvider.__init__(símismo)

        if 'veloc_viento' not in bd_pandas:
            bd_pandas['veloc_viento'] = 1  # en m/s; valor automático consistente con DSSAT
        if 'vap' not in bd_pandas:
            bd_pandas['vap'] = _calc_vap(bd_pandas)  # kPa

        for var, conv in convs_unids.items():
            bd_pandas[var] *= conv

        bd_pandas = bd_pandas.rename({vr: vr_pcse for vr, vr_pcse in conv_nombres.items() if vr in bd_pandas},
                                     axis='columns')

        for f in bd_pandas.index:
            día = pd.to_datetime(f)
            fila = {
                "DAY": día,
                **{conv_nombres[vr] if vr in conv_nombres else vr: bd_pandas[vr][f] for vr in bd_pandas.columns}
            }

            # Reference ET in mm/day
            e0, es0, et0 = reference_ET(
                LAT=lat, ELEV=elev, ANGSTA=símismo.angstA, ANGSTB=símismo.angstB, ETMODEL='PM', **fila
            )

            # convert to cm/day
            fila["E0"] = e0 / 10.
            fila["ES0"] = es0 / 10.
            fila["ET0"] = et0 / 10.
            wdc = WeatherDataContainer(LAT=lat, LON=lon, ELEV=elev, **fila)
            símismo._store_WeatherDataContainer(wdc, día)


def _calc_vap(bd):
    t_rocío = _calc_t_rocío(bd)
    # Ecuación de DSSAT (VPSAT)
    vap = 610.78 * np.exp(17.269 * t_rocío / (t_rocío + 237.30))
    return vap / 1000  # Pa -> kPa


def _calc_t_rocío(bd):
    # Ecuación de DSSAT (CALC_TDEW)
    t_mín = bd['TMIN']
    if 'RHUM' in bd:  # fraccional, y no en % como en DSSAT
        r_hum = bd['RHUM']
        if r_hum.max() > 1:
            r_hum /= 100
        a, b, c = 0.61078, 17.269, 237.3
        es = a * np.exp(b * t_mín / (t_mín + c))
        ea = r_hum * es
        log_ratio = np.log(ea / a)
        return c * log_ratio / (b - log_ratio)
    return t_mín
