import numpy as np
from tikon.ecs.árb_mód import Ecuación, Parám


class L50(Parám):
    """Dósis de letalidad 50% en un día"""
    nombre = 'l50'
    líms = (0, None)
    unids = 'kg / ha'
    inter = 'etapa'


class B(Parám):
    nombre = 'b'
    líms = (0, None)
    unids = None


class Logística(Ecuación):
    nombre = 'Mortalidad logística'
    cls_ramas = [L50]
    inter = 'etapa'

    def eval(símismo, paso, sim):
        cf = símismo.cf
        conc = símismo.obt_valor_res(sim)

        return 1 / (1 + np.exp(-cf['b'] * (conc - cf['a'])))
