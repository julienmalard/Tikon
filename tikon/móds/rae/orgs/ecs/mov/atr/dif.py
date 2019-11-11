from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.mov._plntll import PlantillaEcDifusión
from tikon.result import EJE_PARC, EJE_DEST


class D(Parám):
    nombre = 'd'
    líms = (None, None)
    unids = 'm2/día'


class DifusiónAleatoria(PlantillaEcDifusión):
    nombre = 'Difusión Aleatoria'
    cls_ramas = [D]

    def calc_atr(símismo, paso, sim):
        superficies = símismo.obt_valor_control(sim, 'superficies')
        pobs = símismo.pobs(sim)
        ratio = pobs / superficies
        return ratio / ratio.rename({EJE_PARC: EJE_DEST})
