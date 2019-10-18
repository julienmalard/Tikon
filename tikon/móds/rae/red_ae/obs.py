import numpy as np
import pandas as pd

from tikon.estruc.tiempo import EjeTiempo
from tikon.result.dims import Dims, Coord
from tikon.result.obs import Obs
from .red import RedAE


class ObsRAE(Obs):
    def __init__(símismo, var, datos, dims, eje_tiempo):
        super().__init__(mód=RedAE.nombre, var=var, datos=datos, dims=dims, eje_tiempo=eje_tiempo)


class ObsPobs(ObsRAE):
    def __init__(símismo, datos, dims, eje_tiempo):
        super().__init__(var='Pobs', datos=datos, dims=dims, eje_tiempo=eje_tiempo)

    @classmethod
    def de_csv(cls, archivo, col_tiempo, corresp, parc=None, factor=1):
        csv_pd = pd.read_csv(archivo, encoding='utf8')

        parc = parc or '1'  # para hacer: sincronizar con opciones automáticas

        coords = {
            'etapa': Coord(list(corresp.values())),
            'parc': Coord([parc])
        }

        datos_t = csv_pd[col_tiempo]
        try:
            días = datos_t.astype(float).values
            f_inic = None
        except ValueError:
            raise NotImplementedError

        tiempo = EjeTiempo(días, f_inic=f_inic)

        dims = Dims(coords)
        datos = np.zeros((len(tiempo), *dims.frm()))

        # para hacer: más elegante
        datos[
            (slice(None), *dims.rebanar({'etapa': list(corresp.values()), 'parc': parc}))
        ] = csv_pd[list(corresp.keys())]*factor

        return ObsPobs(datos=datos, dims=dims, eje_tiempo=tiempo)


class ObsDepred(ObsRAE):
    def __init__(símismo, datos, dims, eje_tiempo):
        super().__init__(var='Depred', datos=datos, dims=dims, eje_tiempo=eje_tiempo)
