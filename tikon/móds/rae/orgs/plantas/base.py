from tikon.móds.rae.orgs.utils import CREC

from ..organismo import Organismo


class Planta(Organismo):

    def __init__(símismo, nombre,
                 raíz=False, palo=False, sabia=False, hoja=True, flor=False, fruta=False, semilla=False,
                 tipo_ecs=None):
        """
        Para un cultivo, tomamos una visión un poco relajada de las etapas de un Organismo, y las empleamos para
        distinguir entre las distintas partes de la planta. ¿Parece raro? No, escúchame, tenemos una razón bien
        lógica. Aunque cada 'etapa' de una planta no se convierte directamente en otra etapa (al contrario de, por
        ejemplo, una oruga), cada 'etapa' sí se come por distintos organismos (cada uno tiene su propio depredador).

        Parameters
        ----------
        nombre
        raíz
        palo
        sabia
        hoja
        flor
        fruta
        semilla
        tipo_ecs
        """

        super().__init__(nombre=nombre)

        etapas = []
        if raíz:
            etapas.append('raíz')
        if palo:
            etapas.append('palo')
        if sabia:
            etapas.append('sabia')
        if hoja:
            etapas.append('hoja')
        if flor:
            etapas.append('flor')
        if fruta:
            etapas.append('fruta')
        if semilla:
            etapas.append('semilla')

        ecs_base = dict(
            Crecimiento={'Modif': 'Ninguna', 'Ecuación': 'Logístico'},
            Depredación={'Ecuación': 'Nada'},
            Muertes={'Ecuación': 'Nada'},
            Edad={'Ecuación': 'Nada'},
            Transiciones={'Prob': 'Nada', 'Mult': 'Nada'},
            Reproducción={'Prob': 'Nada'},
        )

        for etp in etapas:
            símismo.añadir_etapa(etp)
            if etp not in tipo_ecs:
                tipo_ecs[etp] = ecs_base

        símismo.activar_ecs(tipo_ecs)

    def estim_dens(símismo, apriori, etapas=None):

        if etapas is None:
            etapas = símismo.etapas()

        símismo.activar_ec(CREC, 'Modif', 'Nada', etapas=etapas)
        símismo.activar_ec(CREC, 'Ecuación', 'Constante', etapas=etapas)

        for etp in etapas:
            símismo.espec_apriori_etp(
                etapa=etp, apriori=apriori, categ=CREC, subcateg='Ecuación', ec='Constante', prm='n',
            )


class Hojas(Planta):

    def __init__(símismo, nombre):
        ecs = dict(Crecimiento={'Modif': 'Ninguna', 'Ecuación': 'Logístico'},
                   Depredación={'Ecuación': 'Nada'},
                   Muertes={'Ecuación': 'Nada'},
                   Edad={'Ecuación': 'Nada'},
                   Transiciones={'Prob': 'Nada', 'Mult': 'Nada'},
                   Reproducción={'Prob': 'Nada'},
                   Movimiento={}
                   )

        super().__init__(nombre=nombre, tipo_ecs={'hoja': ecs})


class HojasRaices(Planta):

    def __init__(símismo, nombre):
        super().__init__(nombre=nombre, raíz=True)


class Completa(Planta):

    def __init__(símismo, nombre):
        super().__init__(
            nombre,
            raíz=True, palo=True, sabia=True, hoja=True, flor=True, fruta=True, semilla=True,
        )
