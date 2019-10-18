from tikon.móds.rae import Insecto


class Sencillo(Insecto):
    """
    Esta clase representa insectos con ciclos de vida sencillos (para cuales sólo se incluye la etapa adulta en el
    modelo).
    """

    def __init__(símismo, nombre):
        tipo_ec = dict(
            Crecimiento={'Modif': 'Ninguna', 'Ecuación': 'Logístico Presa'},
            Depredación={'Ecuación': 'Kovai'},
            Muertes={'Ecuación': 'Nada'},
            Edad={'Ecuación': 'Nada'},
            Transiciones={'Prob': 'Nada', 'Mult': 'Nada'},
            Reproducción={'Prob': 'Nada'}
        )

        super().__init__(
            nombre=nombre, huevo=False, njuvenil=0, pupa=False, adulto=True,
            tipo_ecs={'adulto': tipo_ec}
        )


class MetamCompleta(Insecto):
    """
    Esta clase representa insectos que tienen una metamórfosis completa.
    """

    def __init__(símismo, nombre, huevo=True, njuvenil=1, adulto=True):

        tipo_ec = {}
        if huevo:
            tipo_ec['huevo'] = dict(
                Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
                Depredación={'Ecuación': 'Nada'},
                Muertes={'Ecuación': 'Constante'},
                Edad={'Ecuación': 'Días'},
                Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
                Reproducción={'Prob': 'Nada'},
            )

        tipo_ec['juvenil'] = dict(
            Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
            Depredación={'Ecuación': 'Kovai'},
            Muertes={'Ecuación': 'Constante'},
            Edad={'Ecuación': 'Días'},
            Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
            Reproducción={'Prob': 'Nada'},
        )

        tipo_ec['pupa'] = dict(
            Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
            Depredación={'Ecuación': 'Nada'},
            Muertes={'Ecuación': 'Constante'},
            Edad={'Ecuación': 'Días'},
            Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
            Reproducción={'Prob': 'Nada'},
        )

        if adulto:
            tipo_ec['adulto'] = dict(
                Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
                Depredación={'Ecuación': 'Kovai'},
                Muertes={'Ecuación': 'Nada'},
                Edad={'Ecuación': 'Días'},
                Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
                Reproducción={'Prob': 'Normal'},
            )
        else:
            tipo_ec['pupa']['Reproducción']['Prob'] = 'Constante'

        super().__init__(
            nombre=nombre, huevo=huevo, njuvenil=njuvenil, pupa=True, adulto=adulto,
            tipo_ecs=tipo_ec
        )


class MetamIncompleta(Insecto):
    """
    Esta clase representa insectos que tienen una metamórfosis incompleta.
    """

    def __init__(símismo, nombre, huevo=True, njuvenil=1, adulto=True):

        tipo_ec = {}
        if huevo:
            tipo_ec['huevo'] = dict(
                Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
                Depredación={'Ecuación': 'Nada'},
                Muertes={'Ecuación': 'Constante'},
                Edad={'Ecuación': 'Días'},
                Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
                Reproducción={'Prob': 'Nada'},
                Movimiento={}
            )

        if njuvenil:
            tipo_ec['juvenil'] = dict(
                Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
                Depredación={'Ecuación': 'Kovai'},
                Muertes={'Ecuación': 'Constante'},
                Edad={'Ecuación': 'Días'},
                Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
                Reproducción={'Prob': 'Nada'},
                Movimiento={}
            )

        if adulto:
            tipo_ec['adulto'] = dict(
                Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
                Depredación={'Ecuación': 'Kovai'},
                Muertes={'Ecuación': 'Nada'},
                Edad={'Ecuación': 'Días'},
                Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
                Reproducción={'Prob': 'Normal'},
                Movimiento={}
            )
        else:
            tipo_ec['juvenil']['Reproducción']['Prob'] = 'Constante'

        super().__init__(
            nombre=nombre, huevo=huevo, njuvenil=njuvenil, pupa=False, adulto=adulto,
            tipo_ecs=tipo_ec
        )
