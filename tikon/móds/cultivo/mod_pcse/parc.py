from pcse.engine import Engine
from tikon.central.parc import Parcela, GeomParcela
from tikon.móds.cultivo.extrn import ParcelasCultivoExterno

from .sim import SimulPCSE


class ParcelasCultivoPCSE(ParcelasCultivoExterno):

    def __init__(símismo, nombre, modelo, geom=None, combin=None):
        """

        Parameters
        ----------
        nombre
        modelo: Engine
        geom
        """
        símismo.nombre = nombre
        símismo.cls_modelo = modelo.__class__
        símismo._proveedor_parámetros = modelo.parameterprovider
        símismo._agromanejo = modelo.agromanager

        pdm = modelo.weatherdataprovider
        geom = geom or GeomParcela(
            centroide=(float(pdm.latitude), float(pdm.longitude)), elev=float(pdm.elev)
        )

        super().__init__(Parcela(nombre, geom=geom), combin=combin)

    def gen_modelo_pcse(símismo, proveedor_meteo):
        return símismo.cls_modelo(
            parameterprovider=símismo._proveedor_parámetros, agromanager=símismo._agromanejo,
            weatherdataprovider=proveedor_meteo
        )

    def gen_simul(símismo, sim):
        return SimulPCSE(sim=sim, parcelas=símismo)
