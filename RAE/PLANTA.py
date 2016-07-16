from RAE.Organismo import Organismo


class Planta(Organismo):
    """
    Esta clase representa plantas o cultivos. Se puede contectar con un modelo de cultivo del módulo CULTIVO.
    """

    # La extensión para plantas
    ext = '.plt'

    def __init__(símismo, nombre, fuente=None):
        """

        # Para un cultivo, tomamos una visión un poco relajada de las etapas de un Organismo, y las empleamos para
        # distinguir entre las distintas partes de la planta. ¿Parece raro? No, escúchame, tenemos una razón bien
        # lógica. Aunque cada 'etapa' de una planta no se convierte directamente en otra etapa (al contrario de, por
        # ejemplo, una oruga), cada 'etapa' sí se come por distintos organismos (cada uno tiene su propio depredador).

        :param nombre:
        :type nombre:
        :param fuente:
        :type fuente:
        """

        super().__init__(nombre=nombre, fuente=fuente)

        símismo.ecs_regulares = None


class Sencilla(Planta):
    def __init__(símismo, nombre, fuente=None):

        super().__init__(nombre=nombre, fuente=fuente)

        ecs = dict(Crecimiento={'Modif': 'Ninguna', 'Ecuación': 'Logístico'},
                   Depredación={'Ecuación': None},
                   Muertes={'Ecuación': None},
                   Transiciones={'Edad': None, 'Prob': None},
                   Movimiento={}
                   )

        símismo.añadir_etapa('planta', posición=0, ecuaciones=ecs)


class Constante(Planta):

    def __init__(símismo, nombre, densidad, fuente=None):
        super().__init__(nombre=nombre, fuente=fuente)

        ecs = dict(Crecimiento={'Modif': 'Ninguna', 'Ecuación': 'Población Constante'},
                   Depredación={'Ecuación': None},
                   Muertes={'Ecuación': None},
                   Transiciones={'Edad': None, 'Prob': None},
                   Movimiento={}
                   )

        símismo.añadir_etapa('planta', posición=0, ecuaciones=ecs)

        símismo.fijar_densidad(densidad)

    def fijar_densidad(símismo, pob):
        símismo.especificar_apriori(etapa='planta',
                                    ubic_parám=['Crecimiento', 'Ecuación', 'Población Constante', 'p'],
                                    rango=(pob, pob), certidumbre=1)
        print()


class Completa(Planta):

    def __init__(símismo, nombre, fuente=None):

        super().__init__(nombre=nombre, fuente=fuente)

        # Esta clase por sí misma no puede predecir el crecimiento de cada una de sus partes,
        # y requiere el uso de un modelo de cultivo (o la especificación de un valor fijo).
        lista_etps = ['Raíz', 'Palo', 'Sabia', 'Hoja', 'Flor', 'Fruta', 'Semilla']

        # Una lista de ecuaciones vaciás (ya que no vamos a utilizar las ecuaciones habituales para modelizar las
        # plantas).
        vacías = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                      Depredación={'Ecuación': None},
                      Muertes={'Ecuación': None},
                      Transiciones={'Edad': None, 'Prob': None},
                      Movimiento={}
                      )

        for n, etp in enumerate(lista_etps):
            símismo.añadir_etapa(etp, posición=n, ecuaciones=vacías)
