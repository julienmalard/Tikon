from tikon.central.parc import Parcela, GeomParcela
from tikon.móds.cultivo.extrn import ParcelasCultivoExterno

from .sim import SimulPCSE


class ParcelasCultivoPCSE(ParcelasCultivoExterno):

    def __init__(símismo, nombre, modelo, prov_paráms, prov_meteo, agromanejo, geom=None, combin=None):
        símismo.nombre = nombre
        símismo.cls_modelo = modelo
        símismo._proveedor_parámetros = prov_paráms
        símismo._agromanejo = agromanejo

        símismo._pdm_orig = prov_meteo
        geom = geom or GeomParcela(
            centroide=(float(prov_meteo.latitude), float(prov_meteo.longitude)), elev=float(prov_meteo.elevation)
        )

        super().__init__(Parcela(nombre, geom=geom), combin=combin)

    def gen_modelo_pcse(símismo, proveedor_meteo):
        proveedor_meteo = proveedor_meteo or símismo._pdm_orig
        return símismo.cls_modelo(
            parameterprovider=símismo._proveedor_parámetros, agromanagement=símismo._agromanejo,
            weatherdataprovider=proveedor_meteo
        )

    def gen_simul(símismo, sim):
        return SimulPCSE(sim=sim, parcelas=símismo)
