import numpy as np

import MATEMÁTICAS.NuevoIncert as Incert


# Aquí ponemos la información de los parámetros para todas las ecuaciones posibles. Cada parámetro necesita dos
# pedazos de inforamción: 1) sus límites y 2) si interactua con la estructura del modelo. Por ejemplo, si un
# parámetro de un ecuación de depredación se debe repetir por cada presa del organismo (digamos el número de presa
# comida por el depredador), tendrá que tener el valor 'presa' para su interacción para que TIKON sepa que este variable
# se tiene que repetir por cada presa presente.


ecs_orgs = {'Crecimiento': {'Modif': {None: {},

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

            'Depredación': {'Ecuación': {None: {},

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
                                                   'c': {'límites': (1, np.inf),
                                                         'inter': 'presa'}
                                                   }
                                         },
                            },

            'Muertes': {'Ecuación': {None: {},

                                     'Constante': {'q': {'límites': (0, 1),
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
                                                               }
                                     }
                        },

            'Transiciones': {'Edad': {None: {},

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

                             'Prob': {None: {},

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

            'Movimiento': {
                # 'Ecuación': {None: {},
                #            'Inversa cuadrada': {}
                #           },
                # 'Modif': {None: {},
                #          'Presas': {'p': {}
                #                   }
                #        },
                # 'Mobil': {'Constante': {'m': {}},
                #          'Temperatura': {'m': {},
                #                         't': {}
                #                       },
                #       'Radiación': {}
                #       },
                           }

            }


# Funciones necesarias para el manejo de diccionarios de ecuaciones y de parámetros
def gen_ec_inic(d_ecs, inter=None, d=None):
    """
    Esta función toma un diccionario de especificaciones de parámetros de ecuaciones y lo convierte en un diccionario
      de distribuciones iniciales.

    :param d_ecs: El diccionario de las especificaciones de parámetros para cada tipo de ecuación posible
      Por ejemplo, ecs_orgs.
    :type d_ecs: dict

    :param inter: Un diccionario, si se aplica, de las interacciones con otras partes del modelo necesarios para
      establecer las ecuaciones de manera correcta. Un ejemplo común sería el diccionario de las presas de una etapa
      para establecer las ecuaciones de depredación.
    :type inter: dict

    :param d: Parámetro que siempre se debe dejar a "None" cuando de usa esta función. Está allí para permetir las
      funcionalidades recursivas de la función (que le permite convertir diccionarios de estructura arbitraria).
    :type d: dict

    :return: Un diccionario, con la misma estructura que d_tipos_ecs pero con diccionarios de distribuciones de
      parámetros ya iniciados con distribuciones no informativas.
    :rtype: dict
    """

    # Si es la primera iteración, crear un diccionario vacío
    if d is None:
        d = {}

    # Para cada llave el en diccionario
    for ll, v in d_ecs.items():

        if type(v) is dict:
            # Si el valor es otro diccionario, crearlo en "d" también.
            d[ll] = {}

            if 'límites' in v:
                # Si llegamos a la especificación de límites del parámetro

                # Crear la distribución inicial según las interacciones, si hay. La distribución inicial siempre tiene
                # el número de identificación '0'.
                if v['inter'] is None:
                    # Si no hay interacciones, es muy fácil
                    d[ll]['0'] = Incert.límites_a_texto_apriori(v['límites'])

                else:
                    # Si hay interacciones, hay que repetir el parámetro para cada interacción.
                    d[ll] = {}

                    if inter is not None:
                        # Si se especificaron interaccciones...
                        for i in inter[v['inter']]:
                            # Crear una versión del parámetro para cada interacción
                            d[ll][i] = {}

                            # Llenar el nuevo diccionario con su distribución no informativa
                            d[ll][i]['0'] = Incert.límites_a_texto_apriori(v['límites'])
                    else:
                        # Si no se especificarion, pasar
                        pass

            else:
                # Si, en cambio, no llegamos a la especificación de límites del parámetro, llamar esta función
                # con el nuevo diccionario.
                gen_ec_inic(d_ecs=v, inter=inter, d=d[ll])

        else:
            # Si el valor no era diccionario, ignorarlo.
            pass

    # Devolver el diccionario inicializado con distribuciones no informativas.
    return d
