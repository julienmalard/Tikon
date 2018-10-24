import numpy as np

from .calibs import ÁrbolEcs, CategEc, SubCategEc, Ecuación, Parám

inf = np.inf

ecs_orgs = ÁrbolEcs(
    'organismo',
    categs={
        CategEc(
            'Crecimiento',
            subs={
                SubCategEc(
                    'Modif',
                    ecs={
                        Ecuación('Nada'),
                        Ecuación(
                            'Ninguna',
                            paráms={
                                Parám('r', (0, inf))
                            }
                        ),
                        Ecuación(
                            'Log Normal Temperatura',
                            paráms={
                                Parám('t', (0, inf)),
                                Parám('p', (0, inf))
                            }
                        )
                    }
                ),
                SubCategEc(
                    'Ecuación',
                    ecs={
                        Ecuación('Nada'),
                        Ecuación('Exponencial'),  # El exponencial no tiene parámetros a parte de r
                        Ecuación(
                            'Logístico',
                            paráms={
                                Parám('K', (0, inf)),

                            }
                        ),
                        Ecuación(
                            'Logístico Presa',
                            paráms={
                                Parám('K', (0, inf), inter='presa')
                            }
                        ),
                        Ecuación(
                            'Logístico Depredación',
                            paráms={
                                Parám('K', (0, inf), inter='presa')
                            }
                        ),
                        Ecuación(
                            'Constante',
                            paráms={
                                Parám('n', (0, inf))
                            }
                        )
                    }
                )
            }
        ),
        CategEc(
            'Depredación',
            subs={
                SubCategEc(
                    'Ecuación',
                    ecs={
                        Ecuación('Nada'),
                        Ecuación(
                            'Tipo I_Dependiente presa',
                            paráms={
                                Parám('a', (0, 1), inter=['presa', 'huésped'])
                            }
                        ),
                        Ecuación(
                            'Tipo II_Dependiente presa',
                            paráms={
                                Parám('a', (0, 1), inter=['presa', 'huésped']),
                                Parám('b', (0, inf), inter=['presa', 'huésped'])
                            }
                        ),
                        Ecuación(
                            'Tipo III_Dependiente presa',
                            paráms={
                                Parám('a', (0, 1), inter=['presa', 'huésped']),
                                Parám('b', (0, inf), inter=['presa', 'huésped'])
                            }
                        ),
                        Ecuación(
                            'Tipo I_Dependiente ratio',
                            paráms={
                                Parám('a', (0, 1), inter=['presa', 'huésped'])
                            }
                        ),
                        Ecuación(
                            'Tipo II_Dependiente ratio',
                            paráms={
                                Parám('a', (0, 1), inter=['presa', 'huésped']),
                                Parám('b', (0, inf), inter=['presa', 'huésped'])
                            }
                        ),
                        Ecuación(
                            'Tipo III_Dependiente ratio',
                            paráms={
                                Parám('a', (0, 1), inter=['presa', 'huésped']),
                                Parám('b', (0, inf), inter=['presa', 'huésped'])
                            }
                        ),
                        Ecuación(
                            'Beddington-DeAngelis',
                            paráms={
                                Parám('a', (0, 1), inter=['presa', 'huésped']),
                                Parám('b', (0, inf), inter=['presa', 'huésped']),
                                Parám('c', (0, inf), inter=['presa', 'huésped'])
                            }
                        ),
                    }
                )
            }
        )
    }
)

'Tipo I_Hassell-Varley': {'a': {'límites': (0, inf),
                                'inter': ['presa', 'huésped']},
                          'm': {'límites': (0, inf),
                                'inter': ['presa', 'huésped']}
                          },

'Tipo II_Hassell-Varley': {'a': {'límites': (0, inf),
                                 'inter': ['presa', 'huésped']},
                           'b': {'límites': (0, inf),
                                 'inter': ['presa', 'huésped']},
                           'm': {'límites': (0, inf),
                                 'inter': ['presa', 'huésped']}
                           },

'Tipo III_Hassell-Varley': {'a': {'límites': (0, inf),
                                  'inter': ['presa', 'huésped']},
                            'b': {'límites': (0, inf),
                                  'inter': ['presa', 'huésped']},
                            'm': {'límites': (0, inf),
                                  'inter': ['presa', 'huésped']}
                            },

'Kovai': {'a': {'límites': (0, inf),
                'inter': ['presa', 'huésped']},
          'b': {'límites': (0, inf),
                'inter': ['presa', 'huésped']},
          }
},
},

'Muertes': {'Ecuación': {'Nada': {},

'Constante': {'q': {'límites': (0, 1),
                    'inter': None}
              },

'Log Normal Temperatura': {'t': {'límites': (-inf, inf),
                                 'inter': None},
                           'p': {'límites': (0, inf),
                                 'inter': None}
                           },

'Asimptótico Humedad': {'a': {'límites': (0, inf),
                              'inter': None},
                        'b': {'límites': (-inf, inf),
                              'inter': None}
                        },
'Sigmoidal Temperatura': {'a': {'límites': (-inf, inf),
                                'inter': None},
                          'b': {'límites': (0, inf),
                                'inter': None}
                          }
}
},

'Edad': {'Ecuación': {'Nada': {},

'Días': {},  # No se necesitan coeficientes en este caso

'Días grados': {'mín': {'límites': (-inf, inf),
                        'inter': None},
                'máx': {'límites': (-inf, inf),
                        'inter': None}
                },
'Brière Temperatura': {'t_dev_mín': {'límites': (-inf, inf),
                                     'inter': None},
                       't_letal': {'límites': (-inf, inf),
                                   'inter': None}
                       },
'Logan Temperatura': {'rho': {'límites': (0, 1),
                              'inter': None},
                      'delta': {'límites': (0, 1),
                                'inter': None},
                      't_letal': {'límites': (-inf, inf),
                                  'inter': None}
                      },
'Brière No Linear Temperatura': {'t_dev_mín': {'límites': (-inf, inf),
                                               'inter': None},
                                 't_letal': {'límites': (-inf, inf),
                                             'inter': None},
                                 'm': {'límites': (0, inf),
                                       'inter': None}
                                 },
},
},

'Transiciones': {
    'Prob': {'Nada': {},

'Constante': {'q': {'límites': (0, 1),
                    'inter': None}
              },

'Normal': {'mu': {'límites': (0, inf),
                  'inter': None},
           'sigma': {'límites': (0, inf),
                     'inter': None}
           },
'Triang': {'a': {'límites': (0, inf),
                 'inter': None},
           'b': {'límites': (0, inf),
                 'inter': None},
           'c': {'límites': (0, inf),
                 'inter': None}
           },
'Cauchy': {'u': {'límites': (0, inf),
                 'inter': None},
           'f': {'límites': (0, inf),
                 'inter': None}
           },
'Gamma': {'u': {'límites': (0, inf),
                'inter': None},
          'f': {'límites': (0, inf),
                'inter': None},
          'a': {'límites': (0, inf),
                'inter': None}
          },
'Logística': {'u': {'límites': (0, inf),
                    'inter': None},
              'f': {'límites': (0, inf),
                    'inter': None},
              },
'T': {'k': {'límites': (0, inf),
            'inter': None},
      'mu': {'límites': (0, inf),
             'inter': None},
      'sigma': {'límites': (0, inf),
                'inter': None}
      }
},

'Mult': {'Nada': {},

'Linear': {'a': {'límites': (0, inf),
                 'inter': None}
           }
}
},

'Reproducción': {
    'Prob': {'Nada': {},

'Constante': {'a': {'límites': (0, inf),
                    'inter': None},
              },
'Depredación': {'n': {'límites': (0, inf),
                      'inter': ['presa']}
                },
'Normal': {'n': {'límites': (0, inf),
                 'inter': None},
           'mu': {'límites': (0, inf),
                  'inter': None},
           'sigma': {'límites': (0, inf),
                     'inter': None}
           },
'Triang': {'n': {'límites': (0, inf),
                 'inter': None},
           'a': {'límites': (0, inf),
                 'inter': None},
           'b': {'límites': (0, inf),
                 'inter': None},
           'c': {'límites': (0, inf),
                 'inter': None}
           },
'Cauchy': {'n': {'límites': (0, inf),
                 'inter': None},
           'u': {'límites': (0, inf),
                 'inter': None},
           'f': {'límites': (0, inf),
                 'inter': None}
           },
'Gamma': {'n': {'límites': (0, inf),
                'inter': None},
          'u': {'límites': (0, inf),
                'inter': None},
          'f': {'límites': (0, inf),
                'inter': None},
          'a': {'límites': (0, inf),
                'inter': None}
          },
'Logística': {'n': {'límites': (0, inf),
                    'inter': None},
              'u': {'límites': (0, inf),
                    'inter': None},
              'f': {'límites': (0, inf),
                    'inter': None},
              },
'T': {'n': {'límites': (0, inf),
            'inter': None},
      'k': {'límites': (0, inf),
            'inter': None},
      'mu': {'límites': (0, inf),
             'inter': None},
      'sigma': {'límites': (0, inf),
                'inter': None}
      }
}
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
},

'Estoc': {
    'Dist': {
'Normal': {'sigma': {'límites': (0, 1),
                     'inter': None}
           }
}
}

}
