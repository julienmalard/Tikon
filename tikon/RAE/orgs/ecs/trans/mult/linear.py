from tikon.ecs.árb_mód import Ecuación, Parám


class A(Parám):
    nombre = 'a'
    líms = (0, None)


class Linear(Ecuación):
    nombre = 'Linear'
    _cls_ramas = [A]
