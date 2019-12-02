from scipy.stats import expon
from tikon.ecs.aprioris import APrioriDist
from tikon.ecs.árb_mód import Parám
from tikon.móds.rae.orgs.ecs.mov._plntll import PlantillaEcDifusión
from tikon.utils import EJE_PARC, EJE_DEST


class D(Parám):
    nombre = 'd'
    líms = (0, None)
    unids = 'm2/día'
    apriori = APrioriDist(expon(scale=1000))


class DifusiónAleatoria(PlantillaEcDifusión):
    nombre = 'Difusión Aleatoria'
    cls_ramas = [D]

    def calc_atr(símismo, paso, sim):
        superficies = símismo.obt_valor_control(sim, 'superficies')
        pobs = símismo.pobs(sim)
        ratio = pobs / superficies
        return ratio / ratio.rename({EJE_PARC: EJE_DEST})
