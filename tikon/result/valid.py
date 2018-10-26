

class Validación(object):
    def __init__(símismo, mods):
        símismo._mods = mods

    def _validar(símismo):
        vld = {}
        for nmb, m in símismo._mods.items():
            vld[nmb] = m.valid()
        return vld
