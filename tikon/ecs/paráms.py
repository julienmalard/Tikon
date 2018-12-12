import numpy as np


class MnjdrValsCoefs(object):
    def __init__(símismo, l_paráms, n_reps):
        símismo._paráms = {str(pr): pr.gen_matr_parám(n_reps) for pr in l_paráms}

    def vals_paráms(símismo):
        pass

    def __getitem__(símismo, itema):
        return símismo._paráms[str(itema)].val()


class PlantillaMatrsParáms(object):
    def __init__(símismo, subs):
        símismo._sub_matrs = subs
        símismo._matr = np.zeros(símismo.tmñ())

    def tmñ(símismo):
        return _tmñ(símismo._sub_matrs)

    def llenar(símismo):
        if isinstance(símismo._sub_matrs, dict):
            itr = símismo._sub_matrs.items()
        else:
            itr = enumerate(símismo._sub_matrs)

        for i, sub in itr:
            sub.llenar()
            símismo._matr[i] = sub.val()

    def val(símismo):
        return símismo._matr

    def vals_paráms(símismo):
        return [vls for mtr in símismo._sub_matrs for vls in mtr.vals_paráms()]


class MatrParám(PlantillaMatrsParáms):
    def __init__(símismo, matrs_cosos):
        super().__init__(matrs_cosos)


class MatrParámCoso(PlantillaMatrsParáms):
    def __init__(símismo, vals):
        super().__init__(vals)


class ValsParámCosoInter(PlantillaMatrsParáms):
    def __init__(símismo, matrs_vals_inter, tmñ_inter):
        símismo._tmñ_inter = tmñ_inter
        super().__init__(matrs_vals_inter)

    def tmñ(símismo):
        return

    def vals_paráms(símismo):
        return list(símismo._sub_matrs.values())


class ValsParámCoso(object):

    def __init__(símismo, tmñ, prm_base, inter=None):
        símismo._tmñ = tmñ
        símismo._prm = prm_base
        símismo._inter = inter
        símismo._val = np.zeros(tmñ)

    def tmñ(símismo):
        return símismo._tmñ

    def val(símismo):
        return símismo._val

    def poner_val(símismo, val):
        símismo._val[:] = val


class Inter(object):
    def __init__(símismo, tmñ, índices):
        símismo.tmñ = tmñ
        símismo.índices = índices

    def __iter__(símismo):
        for índs in símismo.índices.items():
            return índs


def _tmñ(grupo):
    n = len(grupo)
    tmñ = grupo[0].tmñ()
    if not all(obj.tmñ() == tmñ for obj in grupo):
        raise ValueError
    return (n, *tmñ)
