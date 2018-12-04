class Parám(object):
    nombre = NotImplemented
    líms = (None, None)
    unids = None
    inter = None

    def __str__(símismo):
        return símismo.nombre


class MnjdrParáms(object):
    def __init__(símismo, cosos, paráms):
        símismo._paráms = {str(pr): pr for pr in paráms}

    def __getitem__(símismo, itema):
        return símismo._paráms[str(itema)]

