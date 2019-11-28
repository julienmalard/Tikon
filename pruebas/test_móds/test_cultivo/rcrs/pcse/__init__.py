import os

from pcse.base import ParameterProvider
from pcse.db import NASAPowerWeatherDataProvider
from pcse.fileinput import CABOFileReader, YAMLAgroManagementReader
from pcse.util import WOFOST71SiteDataProvider

dir_base = os.path.split(__file__)[0]
prov_paráms = ParameterProvider(
    sitedata=WOFOST71SiteDataProvider(WAV=100, CO2=360),
    soildata=CABOFileReader(os.path.join(dir_base, 'ec3.soil')),
    cropdata=CABOFileReader(os.path.join(dir_base, 'sug0601.crop'))
)
agromanejo = YAMLAgroManagementReader(os.path.join(dir_base, 'sugarbeet_calendar.agro'))
prov_meteo = NASAPowerWeatherDataProvider(latitude=52, longitude=5)
