from tikon.RAE.Organismo import Organismo


class Planta(Organismo):
    """
    Esta clase representa plantas o cultivos. Se puede contectar con un modelo de cultivo del módulo Cultivo.
    """

    ext = '.plt'

    # La extensión para plantas
    def __init__(símismo, nombre, raíz=False, palo=False, sabia=False, hoja=True, flor=False, fruta=False,
                 semilla=False, tipo_ecs=None,
                 proyecto=None, fuente=None):
        """
        Para un cultivo, tomamos una visión un poco relajada de las etapas de un Organismo, y las empleamos para
        distinguir entre las distintas partes de la planta. ¿Parece raro? No, escúchame, tenemos una razón bien
        lógica. Aunque cada 'etapa' de una planta no se convierte directamente en otra etapa (al contrario de, por
        ejemplo, una oruga), cada 'etapa' sí se come por distintos organismos (cada uno tiene su propio depredador).

        :param nombre:
        :type nombre: str
        :param raíz:
        :type raíz: bool
        :param palo:
        :type palo: bool
        :param sabia:
        :type sabia: bool
        :param hoja:
        :type hoja: bool
        :param flor:
        :type flor: bool
        :param fruta:
        :type fruta: bool
        :param semilla:
        :type semilla: bool
        :param tipo_ecs:
        :type tipo_ecs: dict
        :param proyecto:
        :type proyecto: str
        :param fuente:
        :type fuente: str

        """

        super().__init__(nombre=nombre, proyecto=proyecto, fuente=fuente)

        if fuente is None:
            if raíz:
                símismo.añadir_etapa(nombre='raíz', posición=0, ecuaciones=tipo_ecs['raíz'])
            if palo:
                símismo.añadir_etapa(nombre='palo', posición=0, ecuaciones=tipo_ecs['palo'])
            if sabia:
                símismo.añadir_etapa(nombre='sabia', posición=0, ecuaciones=tipo_ecs['sabia'])
            if hoja:
                símismo.añadir_etapa(nombre='hoja', posición=0, ecuaciones=tipo_ecs['hoja'])
            if flor:
                símismo.añadir_etapa(nombre='flor', posición=0, ecuaciones=tipo_ecs['flor'])
            if fruta:
                símismo.añadir_etapa(nombre='fruta', posición=0, ecuaciones=tipo_ecs['fruta'])
            if semilla:
                símismo.añadir_etapa(nombre='semilla', posición=0, ecuaciones=tipo_ecs['semilla'])

    def fijar_densidad(símismo, densidad, parte='hoja'):
        """
        Esta función fija la densidad de la planta.

        :param densidad: La densidad de la planta
        :type densidad: int | float

        :param parte:
        :type parte:

        """

        ecs = dict(Crecimiento={'Modif': 'Nada', 'Ecuación': 'Constante'},
                   Depredación={'Ecuación': 'Nada'},
                   Muertes={'Ecuación': 'Nada'},
                   Transiciones={'Edad': 'Nada', 'Prob': 'Nada', 'Mult': 'Nada'},
                   Reproducción={'Edad': 'Nada', 'Prob': 'Nada'},
                   Movimiento={}
                   )

        símismo.aplicar_ecuación(etapa=parte, tipo_ec=ecs)

        símismo.especificar_apriori(etapa=parte, ubic_parám=['Crecimiento', 'Ecuación', 'Constante', 'n'],
                                    rango=(densidad, densidad), certidumbre=1)

    def estimar_densidad(símismo, rango, certidumbre, parte='hoja'):
        """

        :param rango:
        :type rango:
        :param certidumbre:
        :type certidumbre:
        :param parte:
        :type parte:

        """

        ecs = dict(Crecimiento={'Modif': 'Nada', 'Ecuación': 'Constante'},
                   Depredación={'Ecuación': 'Nada'},
                   Muertes={'Ecuación': 'Nada'},
                   Transiciones={'Edad': 'Nada', 'Prob': 'Nada', 'Mult': 'Nada'},
                   Reproducción={'Edad': 'Nada', 'Prob': 'Nada'},
                   Movimiento={}
                   )

        símismo.aplicar_ecuación(etapa=parte, tipo_ec=ecs)

        símismo.especificar_apriori(etapa=parte, ubic_parám=['Crecimiento', 'Ecuación', 'Constante', 'n'],
                                    rango=rango, certidumbre=certidumbre)

    def externalizar(símismo):
        """


        """

        # Un diccionario de las ecuaciones necesarias para un cultivo externo.
        ecs_extrn = dict(Crecimiento={'Modif': 'Nada', 'Ecuación': 'Externo Cultivo'},
                         Depredación={'Ecuación': 'Nada'},
                         Muertes={'Ecuación': 'Nada'},
                         Transiciones={'Edad': 'Nada', 'Prob': 'Nada', 'Mult': 'Nada'},
                         Reproducción={'Edad': 'Nada', 'Prob': 'Nada'},
                         Movimiento={}
                         )

        # Aplicar las ecuaciones de parámetros externos a todas las etapas del organismo.
        for etp in símismo.etapas:
            símismo.aplicar_ecuación(etapa=etp, tipo_ec=ecs_extrn)


class Hojas(Planta):
    """
    Una planta muy sencilla, con crecimiento logístico. Puede ser util para plantas vivaces y pruebas de modelos.
    """

    def __init__(símismo, nombre, proyecto=None, fuente=None):
        """
        Una planta Sencilla tiene una única parte de la planta, llamada "planta".

        :type nombre: str
        :type proyecto: str
        :type fuente: str
        """

        ecs = dict(Crecimiento={'Modif': 'Ninguna', 'Ecuación': 'Logístico'},
                   Depredación={'Ecuación': 'Nada'},
                   Muertes={'Ecuación': 'Nada'},
                   Transiciones={'Edad': 'Nada', 'Prob': 'Nada', 'Mult': 'Nada'},
                   Reproducción={'Edad': 'Nada', 'Prob': 'Nada'},
                   Movimiento={}
                   )

        super().__init__(nombre=nombre, tipo_ecs={'hoja': ecs}, proyecto=proyecto, fuente=fuente)


class Completa(Planta):
    """
    Esta clase por sí misma no puede predecir el crecimiento de cada una de sus partes, y requiere el uso de un
      modelo de cultivo (o la especificación de un valor fijo).
    """

    def __init__(símismo, nombre, proyecto=None, fuente=None):
        """

        :type nombre: str
        :type proyecto: str
        :type fuente: str
        """

        ecs = dict(Crecimiento={'Modif': 'Ninguna', 'Ecuación': 'Logístico'},
                   Depredación={'Ecuación': 'Nada'},
                   Muertes={'Ecuación': 'Nada'},
                   Transiciones={'Edad': 'Nada', 'Prob': 'Nada', 'Mult': 'Nada'},
                   Reproducción={'Edad': 'Nada', 'Prob': 'Nada'},
                   Movimiento={}
                   )

        dic_ecs = {}

        for etp in ['raíz', 'palo', 'sabia', 'hoja', 'flor', 'fruta', 'semilla']:
            dic_ecs[etp] = ecs

        super().__init__(nombre=nombre, raíz=True, palo=True, sabia=True, hoja=True, flor=True, fruta=True,
                         semilla=True, tipo_ecs=dic_ecs,
                         proyecto=proyecto, fuente=fuente)
