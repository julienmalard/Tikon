import numpy as np


# Aquí ponemos la información de los parámetros para todas las ecuaciones posibles. Cada parámetro necesita dos
# pedazos de inforamción: 1) sus límites y 2) si interactua con la estructura de la red. Por ejemplo, si un
# parámetro de un ecuación de depredación se debe repetir por cada presa del organismo (digamos el número de presa
# comida por el depredador), tendrá que tener el valor 'presa' para su interacción para que TIKON sepa que este variable
# se tiene que repetir por cada presa presente.


ecuaciones = dict(Crecimiento={'Modif': {None: None,

                                         'Regular': {'r': {'límites': (0, np.inf),
                                                           'inter': None}},
                                         'Log Normal Temperatura': {'t': {'límites': (0, np.inf),
                                                                          'inter': None},
                                                                    'p': {'límites': (0, np.inf),
                                                                          'inter': None}}
                                         },
                               'Ecuación': {None: None,
                                            'Exponencial': {},  # El exponencial no tiene parámetros a parte de r
                                            'Logístico': {'K': {'límites': (0, np.inf),
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

                                            'Asíntota Doble': {'a': {'límites': (0, np.inf),
                                                                     'inter': 'presa'},
                                                               'b': {'límites': (0, np.inf),
                                                                     'inter': 'presa'},
                                                               'c': {'límites': (0, np.inf),
                                                                     'inter': 'presa'}
                                                               }
                                            },
                               },

                  Muertes={'Edad': {None: None,

                                    'Días': {},

                                    'Días grados': {'mín': {'límites': (-np.inf, np.inf),
                                                            'inter': None},
                                                    'máx': {'límites': (-np.inf, np.inf),
                                                            'inter': None}
                                                    },
                                    },

                           'Prob': {None: None,

                                    'Constante': {'a': {'límites': (0, np.inf),
                                                        'inter': None}
                                                  },

                                    'Log Normal Temperatura': {'t': {'límites': (-np.inf, np.inf),
                                                                     'inter': None},
                                                               'p': {'límites': (),
                                                                     'inter': None}
                                                               },

                                    'Proporcional': {'q': {'límites': (0, 1),
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
                                         'Linear': {'m': {'límites': (0, np.inf),
                                                          'inter': None},
                                                    'b': {'límites': (0, np.inf),
                                                          'inter': None}
                                                    },
                                         'Cauchy': {'a': {'límites': (0, np.inf),
                                                          'inter': None},
                                                    'b': {'límites': (0, np.inf),
                                                          'inter': None}
                                                    },
                                         'Gamma': {'a': {'límites': (0, np.inf),
                                                         'inter': None},
                                                   'b': {'límites': (0, np.inf),
                                                         'inter': None}
                                                   },
                                         'T': {'k': {'límites': (0, np.inf),
                                                     'inter': None}
                                               }
                                         }
                                },

                  Movimiento={}

                  )
