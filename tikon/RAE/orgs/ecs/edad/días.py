from tikon.ecs.árb_mód import Ecuación


class FuncDías(Ecuación):
    """
    Edad por día.
    """
    nombre = 'Días'

    def __call__(self, paso):
        return paso
