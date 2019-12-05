class Datos(object):
    def __init__(símismo, datos):
        símismo.matr = datos.values
        símismo.dims = datos.dims
        símismo.coords = {ll: list(v.values) for ll, v in datos.coords.items()}

    def __add__(símismo, otro):
        if isinstance(otro, Datos):
            raise NotImplementedError

    def __sub__(símismo, otro):
        pass

    def __mul__(símismo, otro):
        pass

    def __mod__(símismo, otro):
        pass

    def __truediv__(símismo, otro):
        pass

    def __floordiv__(símismo, otro):
        pass

    def __pow__(símismo, power, módulo=None):
        pass

    def __iadd__(símismo, otro):
        if isinstance(otro, Datos):
            raise NotImplementedError
        símismo.matr += otro

    def __isub__(símismo, otro):
        pass

    def __imul__(símismo, otro):
        pass

    def __imod__(símismo, otro):
        pass

    def __itruediv__(símismo, otro):
        pass

    def __ifloordiv__(símismo, otro):
        pass

    def __ipow__(símismo, power, módulo=None):
        pass

    def __eq__(símismo, otro):
        pass

    def __gt__(símismo, otro):
        pass

    def __lt__(símismo, otro):
        pass

    def __ge__(símismo, otro):
        pass

    def __le__(símismo, otro):
        pass

    def __ne__(símismo, otro):
        pass

    def __abs__(símismo):
        pass

    def __floor__(símismo):
        pass

    def __neg__(símismo):
        pass

    def __invert__(símismo):
        pass
