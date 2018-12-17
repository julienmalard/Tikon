from tikon.ecs.árb_mód import Ecuación, Parám


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class B(Parám):
    nombre = 'b'
    líms = (None, None)


class AsimptóticoHumedad(Ecuación):
    """
    M. P. Lepage, G. Bourgeois, J. Brodeur, G. Boivin. 2012. Effect of Soil Temperature and Moisture on
    Survival of Eggs and First-Instar Larvae of Delia radicum. Environmental Entomology 41(1): 159-165.
    """

    nombre = 'Asimptótico Humedad'
    cls_ramas = [A, B]

    def eval(símismo, paso):
        sobrevivencia = np.maximum(0, np.subtract(1, np.exp(-cf['a'] * (mnjdr_móds['clima.humedad'] - cf['b']))))
        return np.multiply(pob_etp, (1 - sobrevivencia))