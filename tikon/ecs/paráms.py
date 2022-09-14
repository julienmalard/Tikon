import typing
from typing import Iterable, Sequence, Optional

import numpy as np
from frozendict import frozendict
from numpy.typing import ArrayLike

from tikon.central.matriz import Datos
from tikon.ecs.dists import Dist
from tikon.ecs.árb_coso import ParámCoso
from tikon.tipos import Tipo_Valor_Numérico_Entero, Tipo_Matriz_Núm_Entero
from tikon.utils import EJE_PARÁMS

if typing.TYPE_CHECKING:
    from tikon.central import Modelo, Módulo, Coso
    from tikon.ecs import Parám


class MnjdrValsCoefs(object):
    def __init__(símismo, modelo: "Modelo", mód: "Módulo", paráms: Iterable["Parám"], n_reps: Tipo_Valor_Numérico_Entero):
        símismo._paráms = {str(pr): pr.gen_matr_parám(modelo=modelo, mód=mód, n_reps=n_reps) for pr in paráms}

    def vals_paráms(símismo) -> list["ValsParámCoso"]:
        return [prm for matr in símismo._paráms.values() for prm in matr.vals_paráms()]

    def act_vals(símismo) -> None:
        for matr in símismo._paráms.values():
            matr.act_vals()

    def __getitem__(símismo, itema) -> Datos:
        return símismo._paráms[itema].val


class MatrParám(object):
    def __init__(símismo, subs: Sequence["MatrParám"], eje: str, índice: Optional["Coso"]):
        símismo._sub_matrs = subs

        símismo.eje = eje
        símismo.índice = índice
        símismo._datos = Datos(
            0.,
            dims=list(símismo.coords),
            coords=frozendict({ll: tuple(v) if isinstance(v, list) else v for ll, v in símismo.coords.items()})
        )

    @property
    def coords(símismo) -> dict[str, list["Coso"]]:
        return {símismo.eje: [sub.índice for sub in símismo._sub_matrs], **_combin_coords(símismo._sub_matrs)}

    @property
    def val(símismo) -> Datos:
        return símismo._datos

    def act_vals(símismo) -> None:
        for sub in símismo._sub_matrs:
            sub.act_vals()
            símismo._datos.loc[símismo._datos.codificar_coords({símismo.eje: sub.índice})] = sub.val

    def vals_paráms(símismo) -> list["ValsParámCoso"]:
        return [vls for mtr in símismo._sub_matrs for vls in mtr.vals_paráms()]


class ValsParámCosoInter(MatrParám):
    def __init__(símismo, vals_paráms_inter: list["ValsParámCoso"], eje: str, índice: Optional["Coso"]):
        super().__init__(vals_paráms_inter, eje=eje, índice=índice)


class ValsParámCoso(MatrParám):
    def __init__(
            símismo,
            tmñ: Tipo_Valor_Numérico_Entero,
            prm_base: Optional["ParámCoso"],
            índice: Optional["Coso"],
            inter: Optional["Coso"] = None
    ):
        símismo.tmñ = tmñ
        símismo.prm = prm_base
        símismo.inter = inter

        super().__init__(subs=[], eje=EJE_PARÁMS, índice=índice)

    @property
    def coords(símismo) -> dict[str, list[int]]:
        return {símismo.eje: list(range(símismo.tmñ))}

    @property
    def val(símismo) -> Datos:
        return símismo._datos

    @val.setter
    def val(símismo, val: ArrayLike) -> None:
        símismo._datos[:] = val

    def dists_disp(símismo, heredar: bool):
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

    def llenar_de_dists(símismo, dists: list[tuple[Dist, Tipo_Valor_Numérico_Entero | Tipo_Matriz_Núm_Entero]]):
        val = []

        for d, n in dists:
            if isinstance(n, (int, np.integer)):
                val.append(d.obt_vals(n))
            else:
                val.append(d.obt_vals_índ(n))

        símismo.val = np.ravel(np.array(val))

    def act_vals(símismo):
        """No necesario porque valores se establecen con las funciones `llenar_de...` o de manera externa por
        un calibrador u otro."""
        pass

    def vals_paráms(símismo):
        yield símismo

    def guardar_calibs(símismo, dist, nombre):
        símismo.prm.agregar_calib(id_cal=nombre, dist=dist, inter=símismo.inter)


class ValsParámCosoVacíos(ValsParámCoso):
    def __init__(símismo, tmñ: Tipo_Valor_Numérico_Entero, índice):
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


def _combin_coords(grupo: Sequence["MatrParám"]) -> dict[str, list["Coso"]]:
    coords = grupo[0].coords
    if not all(obj.coords == coords for obj in grupo):
        raise ValueError('Coordinadas deben ser iguales para cada miembro de un grupo.')
    return coords
