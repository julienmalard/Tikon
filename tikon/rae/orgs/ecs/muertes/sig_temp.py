from tikon.ecs.árb_mód import Ecuación, Parám


class A(Parám):
    nombre = 'a'
    líms = (None, None)


class B(Parám):
    nombre = 'b'
    líms = (0, None)


class SigmoidalTemperatura(Ecuación):
    nombre = 'Sigmoidal Temperatura'
    cls_ramas = [A, B]

    def eval(símismo, paso):
        sobrevivencia = 1 / (1 + np.exp((mnjdr_móds['clima.temp_máx'] - cf['a']) / cf['b']))
        return np.multiply(pob_etp, (1 - sobrevivencia))
