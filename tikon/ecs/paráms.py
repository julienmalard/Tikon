import numpy as np
from frozendict import frozendict

from tikon.central.matriz import Datos

from tikon.utils import EJE_PARÁMS


class MnjdrValsCoefs(object):
    def __init__(símismo, modelo, mód, l_paráms, n_reps):
        símismo._paráms = {str(pr): pr.gen_matr_parám(modelo=modelo, mód=mód, n_reps=n_reps) for pr in l_paráms}

    def vals_paráms(símismo):
        return [prm for matr in símismo._paráms.values() for prm in matr.vals_paráms()]

    def act_vals(símismo):
        for matr in símismo._paráms.values():
            matr.act_vals()

    def __getitem__(símismo, itema):
        return símismo._paráms[itema].val


class MatrParám(object):
    def __init__(símismo, subs, eje, índice):
        símismo._sub_matrs = subs

        símismo.eje = eje
        símismo.índice = índice
        símismo._datos = Datos(
            0.,
            dims=list(símismo.coords),
            coords=frozendict({ll: tuple(v) if isinstance(v, list) else v for ll, v in símismo.coords.items()})
        )

    @property
    def coords(símismo):
        return {símismo.eje: [sub.índice for sub in símismo._sub_matrs], **_combin_coords(símismo._sub_matrs)}

    @property
    def val(símismo):
        return símismo._datos

    def act_vals(símismo):
        for sub in símismo._sub_matrs:
            sub.act_vals()
            símismo._datos.loc[símismo._datos.codificar_coords({símismo.eje: sub.índice})] = sub.val

    def vals_paráms(símismo):
        return [vls for mtr in símismo._sub_matrs for vls in mtr.vals_paráms()]


class ValsParámCosoInter(MatrParám):
    def __init__(símismo, vals_paráms_inter, eje, índice):
        super().__init__(vals_paráms_inter, eje=eje, índice=índice)


class ValsParámCoso(MatrParám):
    def __init__(símismo, tmñ, prm_base, índice, inter=None):
        símismo.tmñ = tmñ
        símismo.prm = prm_base
        símismo.inter = inter

        super().__init__(subs=[], eje=EJE_PARÁMS, índice=índice)

    @property
    def coords(símismo):
        return {símismo.eje: list(range(símismo.tmñ))}

    @property
    def val(símismo):
        return símismo._datos

    @val.setter
    def val(símismo, val):
        símismo._datos[:] = val

    def dists_disp(símismo, heredar):
        return símismo.prm.dists_disp(símismo.inter, heredar)

    def dist_base(símismo):
        apriori_auto = símismo.prm.apriori_auto
        if apriori_auto:
            return apriori_auto.dist(símismo.prm.líms)
        return símismo.prm.calib_base()

    def llenar_de_base(símismo):
        símismo.val = símismo.dist_base().obt_vals(símismo.tmñ)

    def apriori(símismo, heredar=True):
        return símismo.prm.apriori(inter=símismo.inter, heredar=heredar)

    def llenar_de_apriori(símismo, heredar=True):
        símismo.val = símismo.apriori(heredar).obt_vals(símismo.tmñ)

    def llenar_de_dists(símismo, dists):
        val = []

        for d, n in dists:
            if isinstance(n, (int, np.integer)):
                val.append(d.obt_vals(n))
            else:
                val.append(d.obt_vals_índ(n))

        símismo.val = np.ravel(val)

    def act_vals(símismo):
        """No necesario porque valores se establecen con las funciones `llenar_de...` o de manera externa por
        un calibrador u otro."""
        pass

    def vals_paráms(símismo):
        yield símismo

    def guardar_calibs(símismo, dist, nombre):
        símismo.prm.agregar_calib(id_cal=nombre, dist=dist, inter=símismo.inter)


class ValsParámCosoVacíos(ValsParámCoso):
    def __init__(símismo, tmñ, índice):
        super().__init__(tmñ, prm_base=None, índice=índice, inter=None)

    def vals_paráms(símismo):
        yield None


class Inter(object):
    def __init__(símismo, itemas, eje, coords):
        símismo.coords = coords
        símismo.itemas = itemas
        símismo.eje = eje

    def __iter__(símismo):
        for c in símismo.coords:
            yield c

    def __bool__(símismo):
        return len(símismo.itemas) > 0


def _combin_coords(grupo):
    coords = grupo[0].coords
    if not all(obj.coords == coords for obj in grupo):
        raise ValueError('Coordinadas deben ser iguales para cada miembro de un grupo.')
    return coords
