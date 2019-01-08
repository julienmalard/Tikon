from ._matr import MatrizTiempo


class Obs(MatrizTiempo):
    def __init__(símismo, mód, var, datos, dims, eje_tiempo):
        símismo.mód = mód
        símismo.var = var
        super().__init__(dims=dims, eje_tiempo=eje_tiempo)

        símismo.poner_valor(datos)

    def f_inic(símismo):
        return símismo.eje_tiempo.f_inic

    def n_días(símismo, f_inic=None):
        if f_inic is None or símismo.f_inic() is None:
            dif = 0
        else:
            dif = (f_inic - símismo.f_inic()).days
        return símismo.eje_tiempo.días.max() + dif
