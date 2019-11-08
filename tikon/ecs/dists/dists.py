_escl_inf = 1e10
_dist_mu = 1


class Dist(object):

    def obt_vals(símismo, n):
        raise NotImplementedError

    def obt_vals_índ(símismo, í):
        raise NotImplementedError

    def tmñ(símismo):
        raise NotImplementedError

    def aprox_líms(símismo, prc):
        raise NotImplementedError

    def a_dic(símismo):
        raise NotImplementedError

    @classmethod
    def de_dic(cls, dic):
        if not dic:
            return
        tipo = dic['tipo']
        for x in cls.__subclasses__():
            if x.__name__ == tipo:
                return x.de_dic(dic)

        raise ValueError(tipo)


class MnjdrDists(object):
    def __init__(símismo):
        símismo.val = None
        símismo.índs = {}

    def actualizar(símismo, dist, índs=None):
        if isinstance(índs, str):
            índs = [índs]
        elif índs is not None:
            índs = list(índs)  # generar copia

        if índs is None or not índs:
            símismo.val = dist
        else:
            í = str(índs.pop(0))

            if í not in símismo.índs:
                símismo.índs[í] = MnjdrDists()

            símismo.índs[í].actualizar(dist, índs)

    def obt_val(símismo, índs=None, heredar=True):

        if isinstance(índs, str):
            índs = [índs]
        elif índs is not None:
            índs = list(índs)  # generar copia

        if índs is None or not len(índs):
            return símismo.val

        í = str(índs.pop(0))
        if í in símismo.índs:
            return símismo.índs[í].obt_val(índs, heredar)
        if heredar:
            return símismo.val

    def __getitem__(símismo, itema):
        return símismo.índs[itema]

    def a_dic(símismo):
        return {
            'val': símismo.val.a_dic() if símismo.val else None,
            'índs': {str(ll): v.a_dic() for ll, v in símismo.índs.items()}
        }

    @classmethod
    def de_dic(cls, dic, mnjdr=None):
        if mnjdr is None:
            mnjdr = MnjdrDists()

        def act_mnjdr(mnj, d, índs_ant=None):
            val = d['val']
            índs = d['índs']
            mnj.actualizar(dist=Dist.de_dic(val), índs=índs_ant)
            for í in índs:
                act_mnjdr(mnj, d=índs[í], índs_ant=(índs_ant or []) + [í])

        act_mnjdr(mnjdr, d=dic)

        return mnjdr
