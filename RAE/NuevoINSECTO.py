from RAE.Organismo import Organismo


class Insecto(Organismo):

    """
    Esta clase representa insectos. En general no se llama directamente, sino a través de una de sus subclasses.
    """

    ext = '.ins'

    def __init__(símismo, nombre, huevo=False, njuvenil=0, pupa=False, adulto=True, tipo_ecuaciones=None, fuente=None):
        """
        La funciôn de inicializaciôn crea un objeto Organismo y después crea las etapas apropiadas.

        :param nombre: El nombre del insecto
        :type nombre: str

        :param huevo: Si incluimos la etapa del huevo en el modelo o no.
        :type huevo: bool

        :param njuvenil: Cuantas fases juveniles incluimos en el modelo (puede ser 0).
        :type njuvenil: int

        :param pupa: Si incluimos la etapa de la pupa en el modelo o no.
        :type pupa: bool

        :param adulto: Si incluimos la etapa del adulto en el modelo o no.
        :type adulto: bool

        :param tipo_ecuaciones: Un diccionario con los tipos de ecuaciones para cada etapa. (Siempre se puede cambiar
          más tarde con la función usar_ecuación()).
          Tiene el formato: {Etapa_1: {Categoría_1: {subcategoría_1: tipo_de_ecuacion, ...}, Categoría_2: {...} },
           Etapa_2: {Categoría_1: {subcategoría...}, ...}, ...}
        :type tipo_ecuaciones: dict

        """

        super().__init__(nombre=nombre, fuente=fuente)

        # Únicamente añadir las etapas si estamos creando un nuevo Insecto (sin cargarlo de un archivo existente)
        if fuente is None:
            pos = 0
            if huevo:
                símismo.añadir_etapa('huevo', posición=pos, ecuaciones=tipo_ecuaciones['huevo'])
                pos += 1

            assert(type(njuvenil) is int and njuvenil >= 0)
            for i in range(0, njuvenil):
                símismo.añadir_etapa('juvenil_%i' % (i+1), posición=pos, ecuaciones=tipo_ecuaciones['juvenil'])
                pos += 1

            if pupa:
                símismo.añadir_etapa('pupa', posición=pos, ecuaciones=tipo_ecuaciones['pupa'])

            if adulto:
                símismo.añadir_etapa('adulto', posición=pos, ecuaciones=tipo_ecuaciones['adulto'])

    def secome(símismo, presa, etps_presa=None, etps_depred=None):
        """
        Estabelce relaciones de depredador y presa.

        :param presa:
        :type presa: Organismo

        :param etps_presa:
        :type etps_presa:

        :param etps_depred:
        :type etps_depred:

        """

        símismo.victimiza(víctima=presa, etps_símismo=etps_depred, etps_víctima=etps_presa, método='presa')

    def nosecome(símismo, presa, etps_presa=None, etps_depred=None):
        """
        Para quitar una relación de depredador y presa.

        :param presa:
        :type presa: Organismo

        :param etps_presa:
        :type etps_presa:

        :param etps_depred:
        :type etps_depred:

        """

        símismo.novictimiza(víctima=presa, etps_símismo=etps_depred, etps_víctima=etps_presa, método='presa')


# Unas clases prehechas para simplificar la creación de insectos
class Sencillo(Insecto):
    def __init__(símismo, nombre):
        """
        Esta clase representa insectos con ciclos de vida sencillos (para cuales sólo se incluye la etapa adulta en el
          modelo).

        :param nombre: El nombre del insecto
        :type nombre: str
        """

        tipo_ec = dict(Crecimiento={'Modif': 'Ninguna', 'Ecuación': 'Logístico Presa'},
                       Depredación={'Ecuación': 'Kovai'},
                       Muertes={'Ecuación': None},
                       Transiciones={'Edad': None, 'Prob': None},
                       Movimiento={}
                       )

        super().__init__(nombre=nombre, huevo=False, njuvenil=0, pupa=False, adulto=True,
                         tipo_ecuaciones=dict(adulto=tipo_ec))


class MetamCompleta(Insecto):
    """
    Esta clase representa insectos que tienen una metamórfosis completa.
    """

    def __init__(símismo, nombre, huevo=True, njuvenil=1, adulto=True):
        """

        :param nombre: El nombre del insecto
        :type nombre: str

        :param huevo: Si incluimos la etapa del huevo en el modelo o no.
        :type huevo: bool

        :param njuvenil: Cuantas fases juveniles incluimos en el modelo.
        :type njuvenil: int

        :param adulto: Si incluimos la etapa del adulto en el modelo o no.
        :type adulto: bool

        """

        tipo_ec = {}
        if huevo:
            tipo_ec['huevo'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                    Depredación={'Ecuación': None},
                                    Muertes={'Ecuación': None},
                                    Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                    Movimiento={}
                                    )

        tipo_ec['juvenil'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                  Depredación={'Ecuación': 'Kovai'},
                                  Muertes={'Ecuación': None},
                                  Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                  Movimiento={}
                                  )

        tipo_ec['pupa'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                               Depredación={'Ecuación': None},
                               Muertes={'Ecuación': None},
                               Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                               Movimiento={}
                               )

        if adulto:
            tipo_ec['adulto'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                     Depredación={'Ecuación': 'Kovai'},
                                     Muertes={'Ecuación': None},
                                     Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                     Movimiento={}
                                     )

        super().__init__(nombre=nombre, huevo=huevo, njuvenil=njuvenil, pupa=True, adulto=adulto,
                         tipo_ecuaciones=tipo_ec)


class MetamIncompleta(Insecto):
    """
    Esta clase representa insectos que tienen una metamórfosis incompleta.
    """

    def __init__(símismo, nombre, huevo=True, njuvenil=1, adulto=True):
        """

        :param nombre: El nombre del insecto
        :type nombre: str

        :param huevo: Si incluimos la etapa del huevo en el modelo o no.
        :type huevo: bool

        :param njuvenil: Cuantas etapas juveniles incluimos en el modelo.
        :type njuvenil: int

        :param adulto: Si incluimos la etapa del adulto en el modelo o no.
        :type adulto: bool

        """

        tipo_ec = {}
        if huevo:
            tipo_ec['huevo'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                    Depredación={'Ecuación': None},
                                    Muertes={'Ecuación': 'Constante'},
                                    Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                    Movimiento={}
                                    )

        tipo_ec['juvenil'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                  Depredación={'Ecuación': 'Kovai'},
                                  Muertes={'Ecuación': 'Constante'},
                                  Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                  Movimiento={}
                                  )

        if adulto:
            tipo_ec['adulto'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                     Depredación={'Ecuación': 'Kovai'},
                                     Muertes={'Ecuación': None},
                                     Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                     Movimiento={}
                                     )

        super().__init__(nombre=nombre,  huevo=huevo, njuvenil=njuvenil, pupa=False, adulto=adulto,
                         tipo_ecuaciones=tipo_ec)


class Parasitoide(Insecto):

    ext = '.ptd'

    def __init__(símismo, nombre, pupa=False, fuente=None):

        tipo_ec = {}

        if pupa:
            tipo_ec['pupa'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                   Depredación={'Ecuación': None},
                                   Muertes={'Ecuación': 'Constante'},
                                   Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                   Movimiento={}
                                   )

        tipo_ec['adulto'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                 Depredación={'Ecuación': 'Kovai'},
                                 Muertes={'Ecuación': None},
                                 Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                 Movimiento={}
                                 )

        super().__init__(nombre=nombre, huevo=False, njuvenil=0, pupa=pupa, adulto=True,
                         tipo_ecuaciones=tipo_ec, fuente=fuente)

    def parasita(símismo, víctima, etps_infec, etp_sale):

        """

        :param víctima: El objeto del otro insecto que este parasitoide puede parasitar.
        :type víctima: Insecto

        :param etps_infec:
        :type etps_infec: list | str

        """

        símismo.victimiza(víctima=víctima, etps_símismo='adulto', etps_víctima=etps_infec, método='huésped')

    def noparasita(símismo, víctima, etps_infec=None):

        """

        :param víctima:
        :type víctima: Organismo

        :param etps_infec:
        :type etps_infec: list | str

        """

        símismo.novictimiza(víctima=víctima, etps_símismo='adulto', etps_víctima=etps_infec)


class Esfécido(Insecto):

    ext = '.esf'

    def __init__(símismo, nombre, fuente=None):

        tipo_ec = {'adulto': dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                  Depredación={'Ecuación': 'Kovai'},
                                  Muertes={'Ecuación': None},
                                  Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                  Movimiento={}
                                  )}

        super().__init__(nombre=nombre, huevo=False, njuvenil=0, pupa=False, adulto=True,
                         tipo_ecuaciones=tipo_ec, fuente=fuente)

    def ataca(símismo, víctima, etps_víc):
        """

        :param víctima: El objeto del otro insecto que este parasitoide puede parasitar.
        :type víctima: Insecto

        """

        símismo.victimiza(víctima=víctima, etps_símismo='adulto', etps_víctima=etps_víc, método='presa')

    def noataca(símismo, víctima, etps_víc):

        símismo.novictimiza(víctima=víctima, etps_símismo='adulto', etps_víctima=etps_víc, método='presa')
