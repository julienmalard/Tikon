from CULTIVO.CULTIVO import Cultivo
from RAE.Organismo import Organismo


class Planta(Organismo):
    """
    Esta clase representa plantas o cultivos. Se puede contectar con un modelo de cultivo del módulo CULTIVO.
    """

    # La extensión para plantas
    ext = '.plt'

    def __init__(símismo, nombre, etps, proyecto=None, fuente=None):
        """

        Para un cultivo, tomamos una visión un poco relajada de las etapas de un Organismo, y las empleamos para
          distinguir entre las distintas partes de la planta. ¿Parece raro? No, escúchame, tenemos una razón bien
          lógica. Aunque cada 'etapa' de una planta no se convierte directamente en otra etapa (al contrario de, por
          ejemplo, una oruga), cada 'etapa' sí se come por distintos organismos (cada uno tiene su propio depredador).

        :type nombre: str

        :param etps: La lista de partes de la planta (tallo, raíz, etc.)
        :type etps: list

        :type fuente: str
        """

        super().__init__(nombre=nombre, proyecto=proyecto, fuente=fuente)

        # El diccionario de la densidad de distintas partes de la planta
        símismo.densidad = {}

        for etp in etps:
            símismo.densidad[etp] = 0


class Sencilla(Planta):
    """
    Una planta muy sencilla, con crecimiento logístico. Puede ser util para plantas vivaces y pruebas de modelos.
    """

    def __init__(símismo, nombre, fuente=None):
        """
        Una planta Sencilla tiene una única parte de la planta, llamada "planta".

        :type nombre: str
        :type fuente: str
        """

        etps = ['planta']
        super().__init__(nombre=nombre, fuente=fuente, etps=etps)

        ecs = dict(Crecimiento={'Modif': 'Ninguna', 'Ecuación': 'Logístico'},
                   Depredación={'Ecuación': 'Nada'},
                   Muertes={'Ecuación': 'Nada'},
                   Transiciones={'Edad': 'Nada', 'Prob': 'Nada'},
                   Movimiento={}
                   )

        símismo.añadir_etapa('planta', posición=0, ecuaciones=ecs)


class Constante(Planta):
    """
    Una planta con población constante. Util para situaciones donde los insectos se quedan muy abajo de su capacidad
    de carga, o donde no hay datos sobre la planta.
    Solamente tiene una parte de la planta, nombrada "planta".
    """

    def __init__(símismo, nombre, densidad, proyecto=None, fuente=None):
        """

        :type nombre: str

        :param densidad: La densidad constante de la planta.
        :type densidad: float | int

        :type proyecto: str
        :type fuente: str
        """

        etps = ['planta']

        super().__init__(nombre=nombre, fuente=fuente, proyecto=proyecto, etps=etps)

        ecs = dict(Crecimiento={'Modif': 'Nada', 'Ecuación': 'Externa cultivo'},
                   Depredación={'Ecuación': 'Nada'},
                   Muertes={'Ecuación': 'Nada'},
                   Transiciones={'Edad': 'Nada', 'Prob': 'Nada'},
                   Movimiento={}
                   )

        símismo.añadir_etapa('planta', posición=0, ecuaciones=ecs)

        símismo.fijar_densidad(densidad)

    def fijar_densidad(símismo, densidad):
        """
        Esta función fija la densidad de la planta.

        :param densidad: La densidad de la planta
        :type densidad: int | float
        """

        símismo.densidad['planta'] = densidad


class Completa(Planta):
    """
    Esta clase por sí misma no puede predecir el crecimiento de cada una de sus partes, y requiere el uso de un
      modelo de cultivo (o la especificación de un valor fijo).
    """

    def __init__(símismo, nombre, fuente=None):
        """

        :type nombre: str
        :type fuente: str
        """

        etps = ['Raíz', 'Palo', 'Sabia', 'Hoja', 'Flor', 'Fruta', 'Semilla']
        super().__init__(nombre=nombre, fuente=fuente, etps=etps)

        # Una lista de ecuaciones vaciás (ya que no vamos a utilizar las ecuaciones habituales para modelizar las
        # plantas).
        vacías = dict(Crecimiento={'Modif': 'Nada', 'Ecuación': 'Externa cultivo'},
                      Depredación={'Ecuación': 'Nada'},
                      Muertes={'Ecuación': 'Nada'},
                      Transiciones={'Edad': 'Nada', 'Prob': 'Nada'},
                      Movimiento={}
                      )

        for n, etp in enumerate(etps):
            símismo.añadir_etapa(etp, posición=n, ecuaciones=vacías)

        símismo.cultivo = None

    def conectar(símismo, cultivo):
        """
        Esta función conecta el objeto de planta al objeto de cultivo simulable.

        :param cultivo: EL objeto de cultivo (conexión con el modelo externo de cultivos).
        :type cultivo: Cultivo

        """

        # Hacemos la conexión
        símismo.cultivo = cultivo

        # Y conectamos los diccionarios
        cultivo.egresos = símismo.densidad
