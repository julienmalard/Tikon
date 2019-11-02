from tikon.móds.rae.orgs.ecs.utils import ECS_CREC, ECS_DEPR, ECS_EDAD, ECS_MOV, ECS_MRTE, ECS_TRANS, ECS_REPR

from ..organismo import Organismo


class Planta(Organismo):

    def __init__(símismo, nombre, raíz, palo, sabia, hoja, flor, fruta, semilla, variedad=None, tipo_ecs=None):
        """
        Para un cultivo, tomamos una visión un poco relajada de las etapas de un Organismo, y las empleamos para
        distinguir entre las distintas partes de la planta.

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

        símismo.variedad = variedad
        super().__init__(nombre=nombre)

        etapas = []
        if raíz:
            etapas.append('raíz')  # kg
        if palo:
            etapas.append('palo')  # kg
        if sabia:
            etapas.append('sabia')  # kg
        if hoja:
            etapas.append('hoja')  # m2
        if flor:
            etapas.append('flor')  # kg
        if fruta:
            etapas.append('fruta')  # kg
        if semilla:
            etapas.append('semilla')  # kg

        ecs_base = {
            ECS_CREC: {'Modif': 'Ninguna', 'Ecuación': 'Logístico'},
            ECS_DEPR: {'Ecuación': 'Nada'},
            ECS_MRTE: {'Ecuación': 'Nada'},
            ECS_EDAD: {'Ecuación': 'Nada'},
            ECS_TRANS: {'Prob': 'Nada', 'Mult': 'Nada'},
            ECS_REPR: {'Prob': 'Nada'},
            ECS_MOV: {'Distancia': 'Nada', 'Atracción': 'Nada'}
        }

        for etp in etapas:
            símismo.añadir_etapa(etp)
            if etp not in tipo_ecs:
                tipo_ecs[etp] = ecs_base

        símismo.activar_ecs(tipo_ecs)

    def fijar_dens(símismo, apriori, etapas=None):

        if etapas is None:
            etapas = símismo.etapas()

        símismo.activar_ec(ECS_CREC, 'Modif', 'Nada', etapas=etapas)
        símismo.activar_ec(ECS_CREC, 'Ecuación', 'Constante', etapas=etapas)

        for etp in etapas:
            símismo.espec_apriori_etp(
                etapa=etp, apriori=apriori, categ=ECS_CREC, subcateg='Ecuación', ec='Constante', prm='n',
            )

    def __str__(símismo):
        if símismo.variedad:
            return "{} {}".format(símismo.nombre, símismo.variedad)
        return símismo.nombre


class Hojas(Planta):

    def __init__(símismo, nombre):
        super().__init__(
            nombre=nombre, raíz=False, palo=False, sabia=False, hoja=True, flor=False, fruta=False, semilla=False,
        )


class HojasRaices(Planta):

    def __init__(símismo, nombre):
        super().__init__(
            nombre=nombre, raíz=True, palo=False, sabia=False, hoja=True, flor=False, fruta=False, semilla=False
        )


class Completa(Planta):

    def __init__(símismo, nombre):
        super().__init__(
            nombre,
            raíz=True, palo=True, sabia=True, hoja=True, flor=True, fruta=True, semilla=True,
        )
