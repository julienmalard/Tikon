from tikon.rae.orgs.insectos.ins import Insecto


class Parasitoide(Insecto):
    """
    Parasitoides son una clase muy especial de insecto, porque sus larvas crecen adentro de los cuerpos de otros
    organismos. Después de mucho dolor de cabeza, decidimos (decidí) implementarlos así.
    """

    ext = '.prs'

    def __init__(símismo, nombre, pupa=False):
        símismo.pupa = pupa

        tipo_ec = {}
        if pupa:
            tipo_ec['pupa'] = dict(
                Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
                Depredación={'Ecuación': 'Nada'},
                Muertes={'Ecuación': 'Constante'},
                Edad={'Ecuación': 'Días'},
                Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
                Reproducción={'Prob': 'Nada'},
                Movimiento={}
            )

        tipo_ec['juvenil'] = dict(
            Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
            Depredación={'Ecuación': 'Nada'},
            Muertes={'Ecuación': 'Nada'},
            Edad={'Ecuación': 'Días'},
            Transiciones={'Prob': 'Normal', 'Mult': 'Linear'},
            Reproducción={'Prob': 'Nada'},
        )

        tipo_ec['adulto'] = dict(
            Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
            Depredación={'Ecuación': 'Kovai'},
            Muertes={'Ecuación': 'Nada'},
            Edad={'Ecuación': 'Días'},
            Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
            Reproducción={'Prob': 'Nada'},
        )

        super().__init__(
            nombre=nombre, huevo=False, njuvenil=1, pupa=pupa, adulto=True, tipo_ecuaciones=tipo_ec
        )

    def parasita(símismo, huésped, etps_entra, etp_emerg, etp_símismo='adulto', etp_recip=None):
        if etp_recip is None:
            etp_recip = 'pupa' if símismo.pupa else 'adulto'
        super().parasita(
            huésped=huésped, etp_símismo=etp_símismo, etps_entra=etps_entra, etp_emerg=etp_emerg, etp_recip=etp_recip
        )


class Esfécido(Insecto):
    """
    Los esfécidos son una familia de avispas que ponen sus huevos en los cuerpos (vivos) de sus presas. Al contrario
    de parasitoides típicos, estos paralizan y quitan su presa de la planta. Por lo mismo, se debe considerar
    su papel ecológico de manera distinta. (Se considera como depredación con reproducción basada en el éxito
    de la depredación).
    """

    ext = '.esf'

    def __init__(símismo, nombre):
        tipo_ec = {'adulto': dict(
            Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
            Depredación={'Ecuación': 'Kovai'},
            Muertes={'Ecuación': 'Nada'},
            Edad={'Ecuación': 'Días'},
            Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
            Reproducción={'Prob': 'Depredación'},
        ),

            'juvenil': dict(
                Crecimiento={'Modif': 'Nada', 'Ecuación': 'Nada'},
                Depredación={'Ecuación': 'Kovai'},
                Muertes={'Ecuación': 'Nada'},
                Edad={'Ecuación': 'Días'},
                Transiciones={'Prob': 'Normal', 'Mult': 'Nada'},
                Reproducción={'Prob': 'Nsda'},
            )
        }

        super().__init__(
            nombre=nombre, huevo=False, njuvenil=1, pupa=False, adulto=True, tipo_ecuaciones=tipo_ec
        )

    def captura(símismo, presa, etps_presa=None):

        símismo.secome(presa=presa, etps_presa=etps_presa, etps_símismo='adulto')

    def nocaptura(símismo, presa, etps_presa=None):

        símismo.nosecome(presa=presa, etps_presa=etps_presa, etps_símismo='adulto')