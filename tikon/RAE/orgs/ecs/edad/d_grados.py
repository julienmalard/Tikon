from tikon.RAE.red_ae.utils import días_grados
from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import Ecuación


class PrMínDG(Parám):
    nombre = 'mín'
    líms = (None, None)


class PrMáxDG(Parám):
    nombre = 'máx'
    líms = (None, None)


class FuncDíasGrados(Ecuación):
    """
    Edad calculada por días grados.
    """
    nombre = 'Días grados'
    _cls_ramas = [PrMínDG, PrMáxDG]

    def __call__(símismo, paso):
        mnjdr_móds = símismo.mnjdr_móds
        cf = símismo.cf

        return días_grados(
            mnjdr_móds['clima.temp_máx'], mnjdr_móds['clima.temp_mín'],
            umbrales=(cf['mín'], cf['máx'])
        ) * paso
