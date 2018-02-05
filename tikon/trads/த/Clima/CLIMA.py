from tikon.Clima.CLIMA import Clima
from tikon.Clima.CLIMA import Diario


class Diario(Diario):

    def buscar(தன், fecha_inic, fecha_fin):
        return super().buscar(fecha_inic=fecha_inic, fecha_fin=fecha_fin)


class Clima(Clima):

    def gendiario(தன், fecha_inic, fecha_fin):
        return super().gendiario(fecha_inic=fecha_inic, fecha_fin=fecha_fin)
