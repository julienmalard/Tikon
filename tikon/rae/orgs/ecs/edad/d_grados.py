from tikon.rae.red_ae.utils import días_grados
from tikon.ecs.árb_mód import Parám
from .._plntll_ec import EcuaciónOrg


class PrMínDG(Parám):
    nombre = 'mín'
    líms = (None, None)


class PrMáxDG(Parám):
    nombre = 'máx'
    líms = (None, None)


class FuncDíasGrados(EcuaciónOrg):
    """
    Edad calculada por días grados.
    """
    nombre = 'Días grados'
    cls_ramas = [PrMínDG, PrMáxDG]

    def eval(símismo, paso):
        mnjdr_móds = símismo.mnjdr_móds
        cf = símismo.cf

        return días_grados(
            mnjdr_móds['clima.temp_máx'], mnjdr_móds['clima.temp_mín'],
            umbrales=(cf['mín'], cf['máx'])
        ) * paso
