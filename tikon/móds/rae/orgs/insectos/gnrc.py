from tikon.móds.rae.orgs.ecs.utils import ECS_CREC, ECS_DEPR, ECS_EDAD, ECS_REPR, ECS_TRANS, ECS_MRTE, ECS_MOV
from tikon.móds.rae.orgs.insectos.ins import Insecto


class Sencillo(Insecto):
    """
    Esta clase representa insectos con ciclos de vida sencillos (para cuales sólo se incluye la etapa adulta en el
    modelo).
    """

    def __init__(símismo, nombre):
        tipo_ec = {
            ECS_CREC: {'Modif': 'Ninguna', 'Ecuación': 'Logístico Presa'},
            ECS_DEPR: {'Ecuación': 'Kovai'},
            ECS_MRTE: {'Ecuación': 'Nada'},
            ECS_EDAD: {'Ecuación': 'Nada'},
            ECS_TRANS: {'Prob': 'Nada', 'Mult': 'Nada'},
            ECS_REPR: {'Prob': 'Nada'},
            ECS_MOV: {'Distancia': 'Euclidiana', 'Atracción': 'Decaimiento Exponencial'}
        }

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
            tipo_ec['huevo'] = {
                ECS_CREC: {'Modif': 'Nada', 'Ecuación': 'Nada'},
                ECS_DEPR: {'Ecuación': 'Nada'},
                ECS_MRTE: {'Ecuación': 'Constante'},
                ECS_EDAD: {'Ecuación': 'Días'},
                ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada'},
                ECS_REPR: {'Prob': 'Nada'},
                ECS_MOV: {'Distancia': 'Nada', 'Atracción': 'Nada'}
            }

        tipo_ec['juvenil'] = {
            ECS_CREC: {'Modif': 'Nada', 'Ecuación': 'Nada'},
            ECS_DEPR: {'Ecuación': 'Kovai'},
            ECS_MRTE: {'Ecuación': 'Constante'},
            ECS_EDAD: {'Ecuación': 'Días'},
            ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada'},
            ECS_REPR: {'Prob': 'Nada'},
            ECS_MOV: {'Distancia': 'Euclidiana', 'Atracción': 'Decaimiento Exponencial'}
        }

        tipo_ec['pupa'] = {
            ECS_CREC: {'Modif': 'Nada', 'Ecuación': 'Nada'},
            ECS_DEPR: {'Ecuación': 'Nada'},
            ECS_MRTE: {'Ecuación': 'Constante'},
            ECS_EDAD: {'Ecuación': 'Días'},
            ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada'},
            ECS_REPR: {'Prob': 'Nada'},
            ECS_MOV: {'Distancia': 'Nada', 'Atracción': 'Nada'}
        }

        if adulto:
            tipo_ec['adulto'] = {
                ECS_CREC: {'Modif': 'Nada', 'Ecuación': 'Nada'},
                ECS_DEPR: {'Ecuación': 'Kovai'},
                ECS_MRTE: {'Ecuación': 'Nada'},
                ECS_EDAD: {'Ecuación': 'Días'},
                ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada'},
                ECS_REPR: {'Prob': 'Normal'},
                ECS_MOV: {'Distancia': 'Euclidiana', 'Atracción': 'Decaimiento Exponencial'}
            }
        else:
            tipo_ec['pupa'][ECS_REPR]['Prob'] = 'Normal'

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
            tipo_ec['huevo'] = {
                ECS_CREC: {'Modif': 'Nada', 'Ecuación': 'Nada'},
                ECS_DEPR: {'Ecuación': 'Nada'},
                ECS_MRTE: {'Ecuación': 'Constante'},
                ECS_EDAD: {'Ecuación': 'Días'},
                ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada'},
                ECS_REPR: {'Prob': 'Nada'},
                ECS_MOV: {'Distancia': 'Nada', 'Atracción': 'Nada'}
            }

        if njuvenil:
            tipo_ec['juvenil'] = {
                ECS_CREC: {'Modif': 'Nada', 'Ecuación': 'Nada'},
                ECS_DEPR: {'Ecuación': 'Kovai'},
                ECS_MRTE: {'Ecuación': 'Constante'},
                ECS_EDAD: {'Ecuación': 'Días'},
                ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada'},
                ECS_REPR: {'Prob': 'Nada'},
                ECS_MOV: {'Distancia': 'Euclidiana', 'Atracción': 'Decaimiento Exponencial'}
            }

        if adulto:
            tipo_ec['adulto'] = {
                ECS_CREC: {'Modif': 'Nada', 'Ecuación': 'Nada'},
                ECS_DEPR: {'Ecuación': 'Kovai'},
                ECS_MRTE: {'Ecuación': 'Nada'},
                ECS_EDAD: {'Ecuación': 'Días'},
                ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada'},
                ECS_REPR: {'Prob': 'Normal'},
                ECS_MOV: {'Distancia': 'Euclidiana', 'Atracción': 'Decaimiento Exponencial'}
            }
        else:
            tipo_ec['juvenil']['Reproducción']['Prob'] = 'Constante'

        super().__init__(
            nombre=nombre, huevo=huevo, njuvenil=njuvenil, pupa=False, adulto=adulto,
            tipo_ecs=tipo_ec
        )
