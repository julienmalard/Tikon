from REDES.ORGANISMO import Organismo


class Insecto(Organismo):
    def __init__(símismo, nombre, huevo, njuvenil, pupa, adulto, tipo_ecuaciones):
        """


        :param nombre:
        :type nombre: str

        :param huevo:
        :type huevo: bool

        :param njuvenil:
        :type njuvenil: int

        :param pupa:
        :type pupa: bool

        :param adulto:
        :type adulto: bool

        :param tipo_ecuaciones:
        :type tipo_ecuaciones: dict

        """

        super().__init__(nombre=nombre)

        pos = 0
        if huevo is not None:
            símismo.añadir_etapa('huevo', posición=pos, ecuaciones=tipo_ecuaciones['huevo'])
            pos += 1

        for i in range(0, njuvenil):
            símismo.añadir_etapa('juvenil_%i' % (i+1), posición=pos, ecuaciones=tipo_ecuaciones['juvenil'])
            pos += 1

        if pupa is not None:
            símismo.añadir_etapa('pupa', posición=pos, ecuaciones=tipo_ecuaciones['pupa'])

        if adulto is not None:
            símismo.añadir_etapa('adulto', posición=pos, ecuaciones=tipo_ecuaciones['adulto'])


# Unas clases prehechas para simplificar la creación de insectos
class Sencillo(Insecto):
    def __init__(símismo, nombre, huevo=False):
        """


        :param nombre:
        :type nombre: str

        :param huevo:
        :type huevo: bool

        """

        tipo_ec = dict(Crecimiento={'Modif': 'Regular', 'Ecuación': 'Logístico presa'},
                       Depredación={'Ecuación': 'Kovai'},
                       Muertes={'Edad': None, 'Prob': None},
                       Transiciones={'Edad': None, 'Prob': None},
                       Movimiento={}
                       )

        super().__init__(nombre=nombre, huevo=huevo, njuvenil=0, pupa=False, adulto=True,
                         tipo_ecuaciones=dict(adulto=tipo_ec))


class MetamCompleta(Insecto):
    def __init__(símismo, nombre, huevo=True, njuvenil=1, adulto=True):
        """

        :param nombre:
        :param huevo:
        :param njuvenil:
        :param adulto:
        :return:
        """

        tipo_ec = {}
        if huevo:
            tipo_ec['huevo'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                    Depredación={'Ecuación': None},
                                    Muertes={'Edad': None, 'Prob': None},
                                    Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                    Movimiento={}
                                    )

        tipo_ec['juvenil'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                  Depredación={'Ecuación': 'Kovai'},
                                  Muertes={'Edad': None, 'Prob': None},
                                  Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                  Movimiento={}
                                  )

        tipo_ec['pupa'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                               Depredación={'Ecuación': None},
                               Muertes={'Edad': None, 'Prob': None},
                               Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                               Movimiento={}
                               )

        if adulto:
            tipo_ec['adulto'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                     Depredación={'Ecuación': 'Kovai'},
                                     Muertes={'Edad': 'Días', 'Prob': 'Proporcional'},
                                     Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                     Movimiento={}
                                     )

        super().__init__(nombre=nombre, huevo=huevo, njuvenil=njuvenil, pupa=True, adulto=adulto,
                         tipo_ecuaciones=tipo_ec)


class MetamIncompleta(Insecto):
    def __init__(símismo, nombre, huevo=True, njuvenil=1, adulto=True):
        """

        :param nombre:
        :param huevo:
        :param njuvenil:
        :param adulto:
        :return:
        """

        tipo_ec = {}
        if huevo:
            tipo_ec['huevo'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                    Depredación={'Ecuación': None},
                                    Muertes={'Edad': None, 'Prob': None},
                                    Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                    Movimiento={}
                                    )

        tipo_ec['juvenil'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                  Depredación={'Ecuación': 'Kovai'},
                                  Muertes={'Edad': None, 'Prob': None},
                                  Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                  Movimiento={}
                                  )

        if adulto:
            tipo_ec['adulto'] = dict(Crecimiento={'Modif': None, 'Ecuación': None},
                                     Depredación={'Ecuación': 'Kovai'},
                                     Muertes={'Edad': 'Días', 'Prob': 'Proporcional'},
                                     Transiciones={'Edad': 'Días', 'Prob': 'Constante'},
                                     Movimiento={}
                                     )

        super().__init__(nombre=nombre,  huevo=huevo, njuvenil=njuvenil, pupa=False, adulto=adulto,
                         tipo_ecuaciones=tipo_ec)
