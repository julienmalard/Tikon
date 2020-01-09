from tikon.móds.rae.orgs.ecs.utils import ECS_CREC, ECS_DEPR, ECS_EDAD, ECS_MRTE, ECS_MOV, ECS_REPR, ECS_TRANS

from .ins import Insecto, JUVENIL
from ..organismo import Etapa


class EtapaJuvenilParasitoide(Etapa):
    ecs_activas = False


class Parasitoide(Insecto):
    """
    Parasitoides son una clase muy especial de insecto, porque sus larvas crecen adentro de los cuerpos de otros
    organismos. Después de mucho dolor de cabeza, decidimos (decidí) implementarlos así.
    """

    def __init__(símismo, nombre, pupa=False):
        símismo.pupa = pupa

        tipo_ec = {
            'juvenil': {
                ECS_CREC: {'Tasa': 'Nada', 'Ecuación': 'Nada'},
                ECS_DEPR: {'Ecuación': 'Nada'},
                ECS_MRTE: {'Ecuación': 'Constante'},
                ECS_EDAD: {'Ecuación': 'Días'},
                ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Linear', 'Deter': 'Nada'},
                ECS_REPR: {'Prob': 'Nada'},
                ECS_MOV: {'Distancia': 'Nada', 'Atracción': 'Nada'}
            }
        }

        # Depred, repr y mov se copiarán del huésped

        if pupa:
            tipo_ec['pupa'] = {
                ECS_CREC: {'Tasa': 'Nada', 'Ecuación': 'Nada'},
                ECS_DEPR: {'Ecuación': 'Nada'},
                ECS_MRTE: {'Ecuación': 'Constante'},
                ECS_EDAD: {'Ecuación': 'Días'},
                ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada'},
                ECS_REPR: {'Prob': 'Nada'},
                ECS_MOV: {'Distancia': 'Nada', 'Atracción': 'Nada'}
            }

        tipo_ec['adulto'] = {
            ECS_CREC: {'Tasa': 'Nada', 'Ecuación': 'Nada'},
            ECS_DEPR: {'Ecuación': 'Kovai'},
            ECS_MRTE: {'Ecuación': 'Nada'},
            ECS_EDAD: {'Ecuación': 'Días'},
            ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada', 'Deter': 'Nada'},
            ECS_REPR: {'Prob': 'Nada'},
            ECS_MOV: {'Distancia': 'Euclidiana', 'Atracción': 'Difusión Aleatoria'}
        }

        super().__init__(
            nombre=nombre, huevo=False, njuvenil=1, pupa=pupa, adulto=True, tipo_ecs=tipo_ec
        )

    def parasita(símismo, huésped, etps_entra, etp_emerg, etp_símismo='adulto', etp_recip=None):
        """
        Indica la relación de parasitismo.

        Parameters
        ----------
        huésped: Insecto
            El huésped.
        etps_entra: Etapa or str or list
            Etapas del huésped que pueden ser parasitadas.
        etp_emerg: Etapa or str
            La etapa de la cual emerge el parasitoide adulto.
        etp_símismo: Etapa or str
           La etapa del parasitoide que efectua el parasitismo.
        etp_recip: Etapa or str
           La etapa del parasitoide que emerge del huésped. Si no se especifica, será la primera etapa después
           de la fase juvenil.

        """

        if etp_recip is None:
            etp_recip = 'pupa' if símismo.pupa else 'adulto'
        super().parasita(
            huésped=huésped, etp_símismo=etp_símismo, etps_entra=etps_entra, etp_emerg=etp_emerg, etp_recip=etp_recip
        )

    def _gen_etapa(símismo, etp):
        if etp == JUVENIL:
            return EtapaJuvenilParasitoide(etp, símismo)
        return super()._gen_etapa(etp)


class Esfécido(Insecto):
    """
    Los esfécidos son una familia de avispas que ponen sus huevos en los cuerpos (vivos) de sus presas. Al contrario
    de parasitoides típicos, estos paralizan y quitan su presa de la planta. Por lo mismo, se debe considerar
    su papel ecológico de manera distinta. (Se considera como depredación con reproducción basada en el éxito
    de la depredación).
    """

    def __init__(símismo, nombre):
        tipo_ec = {
            'adulto': {
                ECS_CREC: {'Tasa': 'Nada', 'Ecuación': 'Nada'},
                ECS_DEPR: {'Ecuación': 'Kovai'},
                ECS_MRTE: {'Ecuación': 'Nada'},
                ECS_EDAD: {'Ecuación': 'Días'},
                ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada', 'Deter': 'Nada'},
                ECS_REPR: {'Prob': 'Depredación'},
                ECS_MOV: {'Distancia': 'Euclidiana', 'Atracción': 'Difusión Aleatoria'}
            },

            'juvenil': {
                ECS_CREC: {'Tasa': 'Nada', 'Ecuación': 'Nada'},
                ECS_DEPR: {'Ecuación': 'Nada'},  # La comida 3 tiempos está incluida
                ECS_MRTE: {'Ecuación': 'Constante'},
                ECS_EDAD: {'Ecuación': 'Días'},
                ECS_TRANS: {'Prob': 'Normal', 'Mult': 'Nada', 'Deter': 'Nada'},
                ECS_REPR: {'Prob': 'Nada'},
                ECS_MOV: {'Distancia': 'Nada', 'Atracción': 'Nada'}  # Juveniles de esfécidos no se mueven

            }
        }

        super().__init__(
            nombre=nombre, huevo=False, njuvenil=1, pupa=False, adulto=True, tipo_ecs=tipo_ec
        )

    def captura(símismo, presa, etps_presa=None):
        """
        Establece la relación entre un Esfécido y sus presas.

        Parameters
        ----------
        presa: Insecto
            La presa.
        etps_presa: Etapa or str or list
            La(s) etapa(s) de la presa que pueden ser víctimas.
        """
        símismo.secome(presa=presa, etps_presa=etps_presa, etps_símismo='adulto')

    def nocaptura(símismo, presa, etps_presa=None):
        """
        Borra una relación entre un Esfécido y una presas.

        Parameters
        ----------
        presa: Insecto
            La presa.
        etps_presa: Etapa or str or list
            La(s) etapa(s) de la presa que ya no pueden ser víctimas.
        """
        símismo.nosecome(presa=presa, etps_presa=etps_presa, etps_símismo='adulto')
