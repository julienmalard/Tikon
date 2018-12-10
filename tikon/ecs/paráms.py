class MnjdrParáms(object):
    def __init__(símismo, cosos, paráms):
        símismo._paráms = {str(pr): NotImplemented for pr in paráms}
        símismo._cosos = cosos

    def __getitem__(símismo, itema):
        return símismo._paráms[str(itema)]
