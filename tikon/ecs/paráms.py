import numpy as np


class MnjdrValsCoefs(object):
    def __init__(símismo, l_paráms, n_reps):
        símismo._paráms = {str(pr): pr.gen_matr_parám(n_reps) for pr in l_paráms}

    def vals_paráms(símismo):
        return [prm for matr in símismo._paráms.values() for prm in matr.vals_paráms()]

    def act_vals(símismo):
        for matr in símismo._paráms.values():
            matr.act_vals()

    def __getitem__(símismo, itema):
        return np.rollaxis(símismo._paráms[str(itema)].val(), -1)


class PlantillaMatrsParáms(object):
    def __init__(símismo, subs):
        símismo._sub_matrs = subs
        símismo._matr = np.zeros(símismo.tmñ())

    def tmñ(símismo):
        return _tmñ(símismo._sub_matrs)

    def act_vals(símismo):
        if isinstance(símismo._sub_matrs, ValsParámCoso):
            símismo._sub_matrs.act_vals()
            símismo._matr[:] = símismo._sub_matrs.val()
        else:
            if isinstance(símismo._sub_matrs, dict):
                itr = símismo._sub_matrs.items()
            else:
                itr = enumerate(símismo._sub_matrs)

            for i, sub in itr:
                sub.act_vals()
                símismo._matr[i] = sub.val()

    def val(símismo):
        return símismo._matr

    def vals_paráms(símismo):
        if isinstance(símismo._sub_matrs, ValsParámCoso):
            return [símismo._sub_matrs]
        else:
            itr = símismo._sub_matrs.values() if isinstance(símismo._sub_matrs, dict) else símismo._sub_matrs
            return [vls for mtr in itr for vls in mtr.vals_paráms()]


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
        return (símismo._tmñ_inter, *_tmñ(list(símismo._sub_matrs.values()))[1:])  # para hacer: probablemente puede ser más elegante

    def __iter__(símismo):
        for vl in símismo._sub_matrs.values():
            yield vl

    def __len__(símismo):
        return len(símismo._sub_matrs)


class ValsParámCoso(object):

    def __init__(símismo, tmñ, prm_base, inter=None):
        símismo._tmñ = (tmñ,)
        símismo._prm = prm_base
        símismo._inter = inter
        símismo._val = np.zeros(tmñ)

    def dists_disp(símismo, heredar):
        return símismo._prm.dists_disp(símismo._inter, heredar)

    def dist_base(símismo):
        return símismo._prm.calib_base()

    def llenar_de_base(símismo):
        calib = símismo.dist_base()
        símismo.poner_val(calib.obt_vals(símismo._tmñ))

    def apriori(símismo):
        return símismo._prm.a_priori()

    def llenar_de_apriori(símismo):
        calib = símismo.apriori()
        símismo.poner_val(calib.obt_vals(símismo._tmñ))

    def act_vals(símismo):
        pass  # para hacer: ¿no necesario?

    def vals_paráms(símismo):
        return [símismo]

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
            yield índs


def _tmñ(grupo):
    if isinstance(grupo, (ValsParámCoso, ValsParámCosoInter)):
        return grupo.tmñ()
    else:
        n = len(grupo)
        tmñ = grupo[0].tmñ()
        if not all(obj.tmñ() == tmñ for obj in grupo):
            raise ValueError
        return (n, *tmñ)
