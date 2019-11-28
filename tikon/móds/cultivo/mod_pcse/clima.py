import pandas as pd
from تقدیر.ذریعہ_نکتہ import ذریعہ_نکتہ

from .meteo import conv_inv, convs_unids


class FuenteMeteoPCSE(ذریعہ_نکتہ):
    _vars_pcse = ["TMAX", "TMIN", "TEMP", "IRRAD", "RAIN", "WIND", "VAP"]

    def __init__(símismo, proveedor, خاکے=None):
        lat, lon, elev = proveedor.latitude, proveedor.longitude, proveedor.elevation
        símismo.proveedor = proveedor
        super().__init__(عرض=lat, طول=lon, بلندی=elev, خاکے=خاکے, تبدیل_عمودی_ستون=None)

    @property
    def متغیرات(símismo):
        return [conv_inv[vr] for vr in símismo._vars_pcse]

    def _کوائف_بنانا(símismo, سے, تک, عرض, طول, بلندی, خاکے):
        datos_pd = pd.DataFrame.from_dict(símismo.proveedor.export())
        datos_pd = datos_pd.set_index('DAY')
        datos_pd.index = pd.to_datetime(datos_pd.index).to_period('D')
        pd_final = pd.DataFrame(
            columns=símismo._vars_pcse,
            index=pd.period_range(símismo.proveedor.first_date, símismo.proveedor.last_date, freq='D')
        )
        pd_final = pd_final.fillna(datos_pd).rename(columns={**conv_inv})

        for var, conv in convs_unids.items():
            pd_final[var] /= conv

        return pd_final
