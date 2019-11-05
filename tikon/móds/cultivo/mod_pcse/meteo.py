import numpy as np
import pandas as pd
from pcse.base import WeatherDataProvider, WeatherDataContainer
from pcse.db import NASAPowerWeatherDataProvider
from pcse.util import reference_ET


class ProveedorMeteoPCSEPandas(NASAPowerWeatherDataProvider):
    _convs = {
        "IRRAD": 1000,  # kJ/m2/día -> J/m2/día
        "VAP": 10,  # kPa -> hPa
        "RAIN": 0.10,  # mm -> cm
    }
    _conv_nombres = {
        'temp_máx': 'TMAX', 'temp_mín': 'TMIN', 'precip': 'RAIN', 'temp_prom': 'TEMP', 'cob_nieve': 'SNOWDEPTH',
        'rad_solar': 'IRRAD', 'vap': 'VAP', 'veloc_viento': 'WIND', 'hum_rel': 'RHUM'
    }
    angstA = 0.29
    angstB = 0.49

    def __init__(símismo, bd_pandas, lat, lon, elev):
        WeatherDataProvider.__init__(símismo)

        bd_pandas = bd_pandas.rename({vr: vr_pcse for vr, vr_pcse in símismo._conv_nombres.items() if vr in bd_pandas})

        if 'WIND' not in bd_pandas:
            bd_pandas['WIND'] = 1  # en m/s; valor automático consistente con DSSAT
        if 'VAP' not in bd_pandas:
            bd_pandas['VAP'] = _calc_vap(bd_pandas)  # kPa

        for var, conv in símismo._convs:
            bd_pandas[var] *= conv

        for f in bd_pandas['fecha']:
            día = pd.to_datetime(f)
            fila = {"DAY": día, **{vr: bd_pandas[vr].loc[{'fecha': f}] for vr in bd_pandas.colnames}}

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
