from tikon.móds.rae.orgs.ecs.mov._plntll import PlantillaEcDifusión
from tikon.utils import EJE_PARC, EJE_DEST


class DifusiónAleatoria(PlantillaEcDifusión):
    nombre = 'Difusión Aleatoria'

    def calc_atr(símismo, paso, sim):
        superficies = símismo.obt_valor_control(sim, 'superficies')
        pobs = símismo.pobs(sim)
        ratio = pobs / superficies
        return ratio / ratio.renombrar({EJE_PARC: EJE_DEST})
