from tikon.ecs.árb_mód import Ecuación


class FuncDías(Ecuación):
    """
    Edad por día.
    """
    nombre = 'Días'

    def eval(self, paso):
        return paso
