class Acción(object):
    def __init__(símismo, mód, func):
        símismo.mód = mód
        símismo.func = func

    def call(símismo, mnjdr):
        raise NotImplementedError
