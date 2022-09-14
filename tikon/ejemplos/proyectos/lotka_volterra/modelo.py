from tikon.central import Modelo
from tikon.móds.rae.orgs.insectos import LotkaVolterra
from tikon.móds.rae.red import RedAE

presa = LotkaVolterra("presa")
depredador = LotkaVolterra("depredador")

RedLotkaVolterra = RedAE([presa, depredador])

with RedLotkaVolterra:
    depredador.secome(presa)

modelo = Modelo(RedLotkaVolterra)
