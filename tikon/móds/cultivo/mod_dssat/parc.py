from tikon.exper.parc import GeomParcela, Parcela
from tikon.móds.cultivo.extrn import ParcelasCultivoExterno

from tradssat.mgrs import ExpFileMgr


class ParcelasCultivoDSSAT(ParcelasCultivoExterno):

    def __init__(símismo, nombre, archivo_exp, geom=None, combin=None):
        símismo.mnjdr = mnjdr = ExpFileMgr(archivo_exp)
        lat, lon, elev = mnjdr.get_value('LAT'), mnjdr.get_value('LONG'), mnjdr.get_value('ELEV')
        geom = geom or GeomParcela(centroide=(lat, lon), elev=elev, superficie=mnjdr.get_value('PAREA'))

        super().__init__(Parcela(nombre, geom=geom), combin=combin)

    def gen_modelo_dssat(símismo, proveedor_meteo):
        return símismo.cls_modelo(
            parameterprovider=símismo._proveedor_parámetros, agromanager=símismo._agromanejo,
            weatherdataprovider=proveedor_meteo
        )

    def gen_simul(símismo, sim):
        return SimulDSSAT(sim=sim, parcelas=símismo)
