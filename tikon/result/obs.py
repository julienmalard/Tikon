from ._matr import Matriz


class Obs(Matriz):
    def __init__(símismo, mód, var, datos, dims, tiempo):
        super().__init__(mód, var, dims=dims, tiempo=tiempo)
        símismo.poner_valor(datos)
