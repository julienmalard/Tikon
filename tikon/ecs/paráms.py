import numpy as np
import xarray as xr
from tikon.central.utils import EJE_PARÁMS


class MnjdrValsCoefs(object):
    def __init__(símismo, modelo, mód, l_paráms, n_reps):
        símismo._paráms = {str(pr): pr.gen_matr_parám(modelo=modelo, mód=mód, n_reps=n_reps) for pr in l_paráms}

    def vals_paráms(símismo):
        return [prm for matr in símismo._paráms.values() for prm in matr.vals_paráms()]

    def act_vals(símismo):
        for matr in símismo._paráms.values():
            matr.act_vals()

    def __getitem__(símismo, itema):
        return símismo._paráms[itema].val()


class PlantillaMatrsParáms(object):
    def __init__(símismo, subs, eje, índice):
        símismo._sub_matrs = subs

        símismo.eje = eje
        símismo.índice = índice
        símismo._datos = xr.DataArray(0., coords=símismo.coords, dims=list(símismo.coords))

    @property
    def coords(símismo):
        return {símismo.eje: [sub.índice for sub in símismo._sub_matrs], **_combin_coords(símismo._sub_matrs)}

    def act_vals(símismo):
        for sub in símismo._sub_matrs:
            sub.act_vals()
            símismo._datos.loc[{símismo.eje: sub.índice}] = sub.val

    def val(símismo):
        return símismo._datos

    def vals_paráms(símismo):
        return [vls for mtr in símismo._sub_matrs for vls in mtr.vals_paráms()]


class MatrParám(PlantillaMatrsParáms):
    def __init__(símismo, matrs_cosos, eje, índice):
        super().__init__(matrs_cosos, eje=eje, índice=índice)


class ValsParámCosoInter(PlantillaMatrsParáms):
    def __init__(símismo, vals_paráms_inter, eje, índice):
        super().__init__(vals_paráms_inter, eje=eje, índice=índice)


class ValsParámCoso(PlantillaMatrsParáms):

    def __init__(símismo, tmñ, prm_base, índice, inter=None):
        símismo.tmñ = tmñ
        símismo._prm = prm_base
        símismo._inter = inter

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
        return símismo._prm.dists_disp(símismo._inter, heredar)

    def dist_base(símismo):
        apriori_auto = símismo._prm.cls_pariente.apriori
        if apriori_auto:
            return apriori_auto.dist(símismo._prm.líms)
        return símismo._prm.calib_base()

    def llenar_de_base(símismo):
        símismo.val = símismo.dist_base().obt_vals(símismo.tmñ)

    def apriori(símismo):
        return símismo._prm.apriori(símismo._inter)

    def llenar_de_apriori(símismo):
        símismo.val = símismo.apriori().obt_vals(símismo.tmñ)

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

    def guardar_calib(símismo, dist, nombre):
        símismo._prm.agregar_calib(id_cal=nombre, dist=dist, inter=símismo._inter)

    def __eq__(símismo, otro):
        return símismo._prm is otro._prm and símismo._inter == otro._inter


class Inter(object):
    def __init__(símismo, itemas, eje):
        símismo.itemas = itemas
        símismo.eje = eje

    def __iter__(símismo):
        for i in símismo.itemas:
            yield i

    def __bool__(símismo):
        return len(símismo.itemas) > 0


def _combin_coords(grupo):
    coords = grupo[0].coords
    if not all(obj.coords == coords for obj in grupo):
        raise ValueError('Coordinadas deben ser iguales para cada miembro de un grupo.')
    return coords
