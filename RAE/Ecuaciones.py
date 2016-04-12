import numpy as np

# Aquí ponemos la información de los parámetros para todas las ecuaciones posibles. Cada parámetro necesita dos
# pedazos de inforamción: 1) sus límites y 2) si interactua con la estructura de la red. Por ejemplo, si un
# parámetro de un ecuación de depredación se debe repetir por cada presa del organismo (digamos el número de presa
# comida por el depredador), tendrá que tener el valor 'presa' para su interacción para que TIKON sepa que este variable
# se tiene que repetir por cada presa presente.


ecuaciones = dict(Crecimiento={'Modif': {None: None,

                                         'Ninguna': {'r': {'límites': (0, np.inf),
                                                           'inter': None}},
                                         'Log Normal Temperatura': {'t': {'límites': (0, np.inf),
                                                                          'inter': None},
                                                                    'p': {'límites': (0, np.inf),
                                                                          'inter': None}}
                                         },
                               'Ecuación': {'Exponencial': {},  # El exponencial no tiene parámetros a parte de r
                                            'Logístico': {'K': {'límites': (0, np.inf),
                                                                'inter': None}},
                                            'Logístico Presa': {'K': {'límites': (0, np.inf),
                                                                'inter': 'presa'}}
                                            }
                               },

                  Depredación={'Ecuación': {None: None,

                                            'Tipo I_Dependiente presa': {'a': {'límites': (0, np.inf),
                                                                               'inter': 'presa'}
                                                                         },

                                            'Tipo II_Dependiente presa': {'a': {'límites': (0, np.inf),
                                                                                'inter': 'presa'},
                                                                          'b': {'límites': (0, np.inf),
                                                                                'inter': 'presa'}
                                                                          },

                                            'Tipo III_Dependiente presa': {'a': {'límites': (0, np.inf),
                                                                                 'inter': 'presa'},
                                                                           'b': {'límites': (0, np.inf),
                                                                                 'inter': 'presa'}
                                                                           },

                                            'Tipo I_Dependiente ratio': {'a': {'límites': (0, np.inf),
                                                                               'inter': 'presa'}
                                                                         },

                                            'Tipo II_Dependiente ratio': {'a': {'límites': (0, np.inf),
                                                                                'inter': 'presa'},
                                                                          'b': {'límites': (0, np.inf),
                                                                                'inter': 'presa'}
                                                                          },

                                            'Tipo III_Dependiente ratio': {'a': {'límites': (0, np.inf),
                                                                                 'inter': 'presa'},
                                                                           'b': {'límites': (0, np.inf),
                                                                                 'inter': 'presa'}
                                                                           },

                                            'Beddington-DeAngelis': {'a': {'límites': (0, np.inf),
                                                                           'inter': 'presa'},
                                                                     'b': {'límites': (0, np.inf),
                                                                           'inter': 'presa'},
                                                                     'c': {'límites': (0, np.inf),
                                                                           'inter': 'presa'}
                                                                     },

                                            'Tipo I_Hassell-Varley': {'a': {'límites': (0, np.inf),
                                                                            'inter': 'presa'},
                                                                      'm': {'límites': (0, np.inf),
                                                                            'inter': 'presa'}
                                                                      },

                                            'Tipo II_Hassell-Varley': {'a': {'límites': (0, np.inf),
                                                                             'inter': 'presa'},
                                                                       'b': {'límites': (0, np.inf),
                                                                             'inter': 'presa'},
                                                                       'm': {'límites': (0, np.inf),
                                                                             'inter': 'presa'}
                                                                       },

                                            'Tipo III_Hassell-Varley': {'a': {'límites': (0, np.inf),
                                                                              'inter': 'presa'},
                                                                        'b': {'límites': (0, np.inf),
                                                                              'inter': 'presa'},
                                                                        'm': {'límites': (0, np.inf),
                                                                              'inter': 'presa'}
                                                                        },

                                            'Kovai': {'a': {'límites': (0, np.inf),
                                                            'inter': 'presa'},
                                                      'b': {'límites': (0, np.inf),
                                                            'inter': 'presa'},
                                                      'c': {'límites': (0, np.inf),
                                                            'inter': 'presa'}
                                                      }
                                            },
                               },

                  Muertes={'Ecuación': {'Constante': {'q': {'límites': (0, 1),
                                                            'inter': None}
                                                      },

                                        'Log Normal Temperatura': {'t': {'límites': (-np.inf, np.inf),
                                                                         'inter': None},
                                                                   'p': {'límites': (0, np.inf),
                                                                         'inter': None}
                                                                   },

                                        'Asimptótico Humedad': {'a': {'límites': (0, np.inf),
                                                                      'inter': None},
                                                                'b': {'límites': (-np.inf, np.inf),
                                                                      'inter': None}
                                                                },
                                        'Sigmoidal Temperatura': {'a': {'límites': (-np.inf, np.inf),
                                                                        'inter': None},
                                                                  'b': {'límites': (0, np.inf),
                                                                        'inter': None}
                                                                  },
                                        },
                           },

                  Transiciones={'Edad': {None: None,

                                         'Días': {},  # No se necesitan coeficientes en este caso

                                         'Días grados': {'mín': {'límites': (-np.inf, np.inf),
                                                                 'inter': None},
                                                         'máx': {'límites': (-np.inf, np.inf),
                                                                 'inter': None}
                                                         },
                                         'Brière Temperatura': {'t_dev_mín': {'límites': (-np.inf, np.inf),
                                                                              'inter': None},
                                                                't_letal': {'límites': (-np.inf, np.inf),
                                                                            'inter': None}
                                                                },
                                         'Logan Temperatura': {'rho': {'límites': (0, 1),
                                                                       'inter': None},
                                                               'delta': {'límites': (0, 1),
                                                                         'inter': None},
                                                               't_letal': {'límites': (-np.inf, np.inf),
                                                                           'inter': None}
                                                               },
                                         'Brière No Linear Temperatura': {'t_dev_mín': {'límites': (-np.inf, np.inf),
                                                                                        'inter': None},
                                                                          't_letal': {'límites': (-np.inf, np.inf),
                                                                                      'inter': None},
                                                                          'm': {'límites': (0, np.inf),
                                                                                'inter': None}
                                                                          },
                                         },

                                'Prob': {None: None,

                                         'Constante': {'a': {'límites': (0, np.inf),
                                                             'inter': None}
                                                       },

                                         'Normal': {'mu': {'límites': (0, np.inf),
                                                           'inter': None},
                                                    'sigma': {'límites': (0, np.inf),
                                                              'inter': None}
                                                    },
                                         'Triang': {'a': {'límites': (0, np.inf),
                                                          'inter': None},
                                                    'b': {'límites': (0, np.inf),
                                                          'inter': None},
                                                    'c': {'límites': (0, np.inf),
                                                          'inter': None}
                                                    },
                                         'Cauchy': {'u': {'límites': (0, np.inf),
                                                          'inter': None},
                                                    'f': {'límites': (0, np.inf),
                                                          'inter': None}
                                                    },
                                         'Gamma': {'u': {'límites': (0, np.inf),
                                                         'inter': None},
                                                   'f': {'límites': (0, np.inf),
                                                         'inter': None},
                                                   'a': {'límites': (0, np.inf),
                                                         'inter': None}
                                                   },
                                         'Logística': {'u': {'límites': (0, np.inf),
                                                             'inter': None},
                                                       'f': {'límites': (0, np.inf),
                                                             'inter': None},
                                                       },
                                         'T': {'k': {'límites': (0, np.inf),
                                                     'inter': None},
                                               'mu': {'límites': (0, np.inf),
                                                      'inter': None},
                                               'sigma': {'límites': (0, np.inf),
                                                         'inter': None}
                                               }
                                         },
                                },

                  Movimiento={}

                  )


# Funciones necesarias para el manejo de diccionarios de ecuaciones y de parámetros
def gen_ec_inic(dic_ecs, inter=None, d=None):
    """
    Esta función toma un diccionario de especificaciones de parámetros de ecuaciones y lo convierte en un diccionario
      de distribuciones iniciales.

    :param d: Parámetro que siempre se debe dejar a "None" cuando de usa esta función. Está allí para permetir las
      funcionalidades recursivas de la función (que le permite convertir diccionarios de estructura arbitraria).
    :type d: dict

    :param inter: Un diccionario, si se aplica, de las interacciones con otros organismos necesarios para establecer
      las ecuaciones de manera correcta. Un ejemplo común sería el diccionario de las presas de una etapa
      para establecer las ecuaciones de depredación.
    :type inter: dict

    :param dic_ecs: El diccionario de las especificaciones de parámetros para cada tipo de ecuación posible
    :type dic_ecs: dict

    :return: d
    :rtype: dict
    """

    # Si es la primera iteración, crear un diccionario vacío
    if d is None:
        d = {}

    # Para cada llave el en diccionario
    for ll, v in dic_ecs.items():
        # Si v también es un diccionario, crear el diccionario correspondiente en d
        if type(v) is dict:
            d[ll] = {}
            gen_ec_inic(v, inter, d)  # y llamar esta función de nuevo

        elif ll == 'límites':  # Si llegamos a la especificación de límites del parámetro

            d[ll] = {}  # Crear el diccionario para contener las calibraciones
            d[ll]['0'] = límites_a_dist(v)  # La distribución inicial siempre tiene el número de identificación '0'.

        else:
            pass

    return d


def límites_a_dist(límites, cont=True):
    """
    Esta función toma un "tuple" de límites para un parámetro de una función y devuelve una descripción de una
      destribución a priori no informativa (espero) para los límites dados. Se usa en la inicialización de las
      distribuciones de los parámetros de ecuaciones.

    :param límites: Las límites para los valores posibles del parámetro. Para límites infinitas, usar np.inf y
      -np.inf. Ejemplos: (0, np.inf), (-10, 10), (-np.inf, np.inf). No se pueden especificar límites en el rango
      (-np.inf, R), donde R es un número real. En ese caso, usar las límites (R, np.inf) y tomar el negativo del
      variable en las ecuaciones que lo utilisan.
    :type límites: tuple

    :param cont: Determina si el variable es continuo o discreto
    :type cont: bool

    :return: Descripción de la destribución no informativa que conforme a las límites especificadas. Devuelve una
      cadena de carácteres, que facilita guardar las distribuciones de los parámetros. Otras funciones la convertirán
      en distribución de scipy o de pymc donde necesario.
    :rtype: str
    """

    # Sacar el mínimo y máximo de los límites.
    mín = límites[0]
    máx = límites[1]

    # Verificar que máx > mín
    if máx <= mín:
        raise ValueError('El valor máximo debe ser superior al valor máximo.')

    # Pasar a través de todos los casos posibles
    if mín == -np.inf:
        if máx == np.inf:  # El caso (-np.inf, np.inf)
            if cont:
                dist = 'Normal~(0, 1e10)'
            else:
                dist = 'DiscrUnif~(1e-10, 1e10)'

        else:  # El caso (-np.inf, R)
            raise ValueError('Tikón no tiene funcionalidades de distribuciones a priori en intervalos (-inf, R). Puedes'
                             'crear un variable en el intervalo (R, inf) y utilisar su valor negativo en las '
                             'ecuaciones.')

    else:
        if máx == np.inf:  # El caso (R, np.inf)
            if cont:
                dist = 'Gamma~({}, 0.0001, 0.0001)'.format(mín)
            else:
                loc = mín - 1
                dist = 'Geom~(1e-8, {})'.format(loc)

        else:  # El caso (R, R)
            if cont:
                dist = 'Unif~({}, {})'.format(mín, máx)
            else:
                dist = 'DiscrUnif~({}, {})'.format(mín, mín+1)

    return dist


