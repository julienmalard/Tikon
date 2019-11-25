from tikon.ecs.árb_mód import Parám

from .utils import días_grados
from .._plntll import EcuaciónOrg


class PrMínDG(Parám):
    nombre = 'mín'
    líms = (None, None)
    unids = 'C'


class PrDifDG(Parám):
    nombre = 'dif'
    líms = (0, None)
    unids = 'C'


class PlantillaFuncDíasGrados(EcuaciónOrg):
    """
    Edad calculada por días grados.
    """
    cls_ramas = [PrMínDG, PrDifDG]

    def eval(símismo, paso, sim):
        cf = símismo.cf
        temp_máx = símismo.obt_valor_extern(sim, 'clima.temp_máx')
        temp_mín = símismo.obt_valor_extern(sim, 'clima.temp_mín')
        return días_grados(temp_máx, temp_mín, umbrales=(cf['mín'], cf['mín'] + cf['dif']), **símismo._args()) * paso

    @classmethod
    def requísitos(cls, controles=False):
        if not controles:
            return {'clima.temp_máx', 'clima.temp_mín'}

    @property
    def nombre(símismo):
        raise NotImplementedError

    def _args(símismo):
        raise NotImplementedError


class FuncDíasGradosTH(PlantillaFuncDíasGrados):
    """
    Edad calculada por días grados, método triangular y corte horizontal.

    Ver :func:`~tikon.rae.orgs.ecs.edad.días_grados`.
    """
    nombre = 'Días grados TH'

    def _args(símismo):
        return {'método': 'triangular', 'corte': 'horizontal'}


class FuncDíasGradosSH(PlantillaFuncDíasGrados):
    """
    Edad calculada por días grados, método sinusoidal y corte horizontal.

    Ver :func:`~tikon.rae.orgs.ecs.edad.días_grados`.
    """
    nombre = 'Días grados SH'

    def _args(símismo):
        return {'método': 'sinusoidal', 'corte': 'horizontal'}


class FuncDíasGradosTI(PlantillaFuncDíasGrados):
    """
    Edad calculada por días grados, método triangular y corte intermediario.

    Ver :func:`~tikon.rae.orgs.ecs.edad.días_grados`.
    """
    nombre = 'Días grados TI'

    def _args(símismo):
        return {'método': 'triangular', 'corte': 'intermediario'}


class FuncDíasGradosSI(PlantillaFuncDíasGrados):
    """
    Edad calculada por días grados, método sinusoidal y corte intermediario.

    Ver :func:`~tikon.rae.orgs.ecs.edad.días_grados`.
    """
    nombre = 'Días grados SI'

    def _args(símismo):
        return {'método': 'sinusoidal', 'corte': 'horizontal'}


class FuncDíasGradosTV(PlantillaFuncDíasGrados):
    """
    Edad calculada por días grados, método triangular y corte vertical.

    Ver :func:`~tikon.rae.orgs.ecs.edad.días_grados`.
    """
    nombre = 'Días grados TV'

    def _args(símismo):
        return {'método': 'triangular', 'corte': 'vertical'}


class FuncDíasGradosSV(PlantillaFuncDíasGrados):
    """
    Edad calculada por días grados, método sinusoidal y corte vertical.

    Ver :func:`~tikon.rae.orgs.ecs.edad.días_grados`.
    """
    nombre = 'Días grados SV'

    def _args(símismo):
        return {'método': 'sinusoidal', 'corte': 'vertical'}


class FuncDíasGradosTN(PlantillaFuncDíasGrados):
    """
    Edad calculada por días grados, método triangular y sin corte.

    Ver :func:`~tikon.rae.orgs.ecs.edad.días_grados`.
    """
    nombre = 'Días grados TN'

    def _args(símismo):
        return {'método': 'triangular', 'corte': 'ninguno'}


class FuncDíasGradosSN(PlantillaFuncDíasGrados):
    """
    Edad calculada por días grados, método sinusoidal y sin corte.

    Ver :func:`~tikon.rae.orgs.ecs.edad.días_grados`.
    """
    nombre = 'Días grados SN'

    def _args(símismo):
        return {'método': 'sinusoidal', 'corte': 'ninguno'}
