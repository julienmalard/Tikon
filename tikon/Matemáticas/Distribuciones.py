import math as mat

import numpy as np

try:
    import pymc3 as pm3
except ImportError:
    pm3 = None

import scipy.stats as estad

# Par asimplificar el código (un poquitísimo)
inf = np.inf
pi = mat.pi

# Un diccionario de las distribuciones y de sus objetos de SciPy y de PyMC correspondientes.
dists = {'Alpha': {'scipy': estad.alpha,
                   'paráms': ['a', 'ubic', 'escl'],
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'Anglit': {'scipy': estad.anglit,
                    'paráms': ['ubic', 'escl'],
                    'límites': (-pi / 4, pi / 4),
                    'tipo': 'cont'
                    },
         'Arcsen': {'scipy': estad.arcsine,
                    'paráms': ['ubic', 'escl'],
                    'límites': (0, 1),
                    'tipo': 'cont'
                    },
         'Beta': {'scipy': estad.beta,
                  'paráms': ['a', 'b', 'ubic', 'escl'],
                  'límites': (0, 1),
                  'tipo': 'cont'
                  },
         'BetaPrima': {'scipy': estad.betaprime,
                       'paráms': ['a', 'b', 'ubic', 'escl'],
                       'límites': (0, inf),
                       'tipo': 'cont'
                       },
         'Bradford': {'scipy': estad.bradford,
                      'paráms': ['c', 'ubic', 'escl'],
                      'límites': (0, 1),
                      'tipo': 'cont'
                      },
         'Burr': {'scipy': estad.burr,
                  'paráms': ['c', 'd', 'ubic', 'escl'],
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Cauchy': {'scipy': estad.cauchy,
                    'paráms': ['ubic', 'escl'],
                    'límites': (-inf, inf),
                    'tipo': 'cont'
                    },
         'Chi': {'scipy': estad.chi,
                 'paráms': ['df', 'ubic', 'escl'],
                 'límites': (0, inf),
                 'tipo': 'cont'
                 },
         'Chi2': {'scipy': estad.chi2,
                  'paráms': ['df', 'ubic', 'escl'],
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Cosine': {'scipy': estad.cosine,
                    'paráms': ['ubic', 'escl'],
                    'límites': (-pi, pi),
                    'tipo': 'cont'
                    },
         'DobleGamma': {'scipy': estad.dgamma,
                        'paráms': ['a', 'ubic', 'escl'],
                        'límites': (0, inf),
                        'tipo': 'cont'
                        },
         'DobleWeibull': {'scipy': estad.dweibull,
                          'paráms': ['c', 'ubic', 'escl'],
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'Exponencial': {'scipy': estad.expon,
                         'paráms': ['ubic', 'escl'],
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'NormalExponencial': {'scipy': estad.exponnorm,
                               'paráms': ['K', 'ubic', 'escl'],
                               'límites': (-inf, inf),
                               'tipo': 'cont'
                               },
         'WeibullExponencial': {'scipy': estad.exponweib,
                                'paráms': ['a', 'c', 'ubic', 'escl'],
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'PotencialExponencial': {'scipy': estad.exponpow,
                                  'paráms': ['b', 'ubic', 'escl'],
                                  'límites': (0, inf),
                                  'tipo': 'cont'
                                  },
         'F': {'scipy': estad.f,
               'paráms': ['dfn', 'dfd', 'ubic', 'escl'],
               'límites': (0, inf),
               'tipo': 'cont'
               },

         'BirnbaumSaunders': {'scipy': estad.fatiguelife,
                              'paráms': ['c', 'ubic', 'escl'],
                              'límites': (0, inf),
                              'tipo': 'cont'
                              },
         'Fisk': {'scipy': estad.fisk,
                  'paráms': ['c', 'ubic', 'escl'],
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'CauchyDoblada': {'scipy': estad.foldcauchy,
                           'paráms': ['c', 'ubic', 'escl'],
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'NormalDoblada': {'scipy': estad.foldnorm,
                           'paráms': ['c', 'ubic', 'escl'],
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'FrechetDerecha': {'scipy': estad.frechet_r,
                            'paráms': ['c', 'ubic', 'escl'],
                            'límites': (0, inf),
                            'tipo': 'cont'
                            },
         # 'FrechetIzquierda': {'scipy': estad.frechet_l,
         #               'pymc': None,
         #               'límites': (-inf, 0)
         #               },
         'LogísticaGeneral': {'scipy': estad.genlogistic,
                              'paráms': ['c', 'ubic', 'escl'],
                              'límites': (0, inf),
                              'tipo': 'cont'
                              },
         'NormalGeneral': {'scipy': estad.gennorm,
                           'paráms': ['beta', 'ubic', 'escl'],
                           'límites': (-inf, inf),
                           'tipo': 'cont'
                           },
         'ParetoGeneral': {'scipy': estad.genpareto,
                           'paráms': ['c', 'ubic', 'escl'],
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'ExponencialGeneral': {'scipy': estad.genexpon,
                                'paráms': ['a', 'b', 'c', 'ubic', 'escl'],
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'ExtremaGeneral': {'scipy': estad.genextreme,
                            'paráms': ['c', 'ubic', 'escl'],
                            'límites': (-inf, inf),
                            'tipo': 'cont'
                            },
         'HyperGauss': {'scipy': estad.gausshyper,
                        'paráms': ['a', 'b', 'c', 'z', 'ubic', 'escl'],
                        'límites': (0, 1),
                        'tipo': 'cont'
                        },
         'Gamma': {'scipy': estad.gamma,
                   'paráms': ['a', 'ubic', 'escl'],
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'GammaGeneral': {'scipy': estad.gengamma,
                          'paráms': ['a', 'c', 'ubic', 'escl'],
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         # 'MitadLogísticaGeneral': {'scipy': estad.genhalflogistic,
         #            'paráms': [],
         #                           'límites': (0, 1),  # El límite es (0, 1/'c')
         #                           'tipo': 'cont'
         #                           },
         'Gilbrat': {'scipy': estad.gilbrat,
                     'paráms': ['ubic', 'escl'],
                     'límites': (0, inf),
                     'tipo': 'cont'
                     },
         'Gompertz': {'scipy': estad.gompertz,
                      'paráms': ['c', 'ubic', 'escl'],
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'GumbelDerecho': {'scipy': estad.gumbel_r,
                           'paráms': ['ubic', 'escl'],
                           'límites': (-inf, inf),
                           'tipo': 'cont'
                           },
         'GumbelIzquierda': {'scipy': estad.gumbel_l,
                             'paráms': ['ubic', 'escl'],
                             'límites': (-inf, inf),
                             'tipo': 'cont'
                             },
         'MitadCauchy': {'scipy': estad.halfcauchy,
                         'paráms': ['ubic', 'escl'],
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'MitadLogística': {'scipy': estad.halflogistic,
                            'paráms': ['ubic', 'escl'],
                            'límites': (0, inf),
                            'tipo': 'cont'
                            },
         'MitadNormal': {'scipy': estad.halfnorm,
                         'paráms': ['ubic', 'escl'],
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'MitadNormalGeneral': {'scipy': estad.halfgennorm,
                                'paráms': ['beta', 'ubic', 'escl'],
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'HyperSecante': {'scipy': estad.hypsecant,
                          'paráms': ['ubic', 'escl'],
                          'límites': (-inf, inf),
                          'tipo': 'cont'
                          },
         'GammaInversa': {'scipy': estad.invgamma,
                          'paráms': ['a', 'ubic', 'escl'],
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'GaussInversa': {'scipy': estad.invgauss,
                          'paráms': ['mu', 'ubic', 'escl'],
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'WeibullInversa': {'scipy': estad.invweibull,
                            'paráms': ['c', 'ubic', 'escl'],
                            'límites': (0, inf),
                            'tipo': 'cont'
                            },
         'JohnsonSB': {'scipy': estad.johnsonsb,
                       'paráms': ['a', 'b', 'ubic', 'escl'],
                       'límites': (0, 1),
                       'tipo': 'cont'
                       },
         'JohnsonSU': {'scipy': estad.johnsonsu,
                       'paráms': ['a', 'b', 'ubic', 'escl'],
                       'límites': (0, inf),
                       'tipo': 'cont'
                       },
         'KSUno': {'scipy': estad.ksone,
                   'paráms': ['n', 'ubic', 'escl'],
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'KSDosNLargo': {'scipy': estad.kstwobign,
                         'paráms': ['ubic', 'escl'],
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'Laplace': {'scipy': estad.laplace,
                     'paráms': ['ubic', 'escl'],
                     'límites': (-inf, inf),
                     'tipo': 'cont'
                     },
         'Levy': {'scipy': estad.levy,
                  'paráms': ['ubic', 'escl'],
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Logística': {'scipy': estad.logistic,
                       'paráms': ['ubic', 'escl'],
                       'límites': (-inf, inf),
                       'tipo': 'cont'
                       },
         'LogGamma': {'scipy': estad.loggamma,
                      'paráms': ['c', 'ubic', 'escl'],
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'LogLaplace': {'scipy': estad.loglaplace,
                        'paráms': ['c', 'ubic', 'escl'],
                        'límites': (0, inf),
                        'tipo': 'cont'
                        },
         'LogNormal': {'scipy': estad.lognorm,
                       'paráms': ['s', 'ubic', 'escl'],
                       'límites': (0, inf),
                       'tipo': 'cont'
                       },
         'Lomax': {'scipy': estad.lomax,
                   'paráms': ['c', 'ubic', 'escl'],
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'Maxwell': {'scipy': estad.maxwell,
                     'paráms': ['ubic', 'escl'],
                     'límites': (0, inf),
                     'tipo': 'cont'
                     },
         'Mielke': {'scipy': estad.mielke,
                    'paráms': ['k', 's', 'ubic', 'escl'],
                    'límites': (0, inf),
                    'tipo': 'cont'
                    },
         'Nakagami': {'scipy': estad.nakagami,
                      'paráms': ['nu', 'ubic', 'escl'],
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'Chi2NoCentral': {'scipy': estad.ncx2,
                           'paráms': ['df', 'nc', 'ubic', 'escl'],
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'FNoCentral': {'scipy': estad.ncf,
                        'paráms': ['dfn', 'dfd', 'nc', 'ubic', 'escl'],
                        'límites': (0, inf),
                        'tipo': 'cont'
                        },

         # Desactivada por complicación de conversión PyMC-SciPy
         #
         # 'TNoCentral': {'scipy': estad.nct,
         #                'paráms': ['df', 'nc', 'ubic', 'escl'],
         #                'pymc': NoncentralT,
         #                'límites': (-inf, inf),
         #                'tipo': 'cont'
         #                },

         'Normal': {'scipy': estad.norm,
                    'paráms': ['ubic', 'escl'],
                    'límites': (-inf, inf),
                    'tipo': 'cont'
                    },
         'Pareto': {'scipy': estad.pareto,
                    'paráms': ['b', 'ubic', 'escl'],
                    'límites': (1, inf),
                    'tipo': 'cont'
                    },
         'Pearson3': {'scipy': estad.pearson3,
                      'paráms': ['skew', 'ubic', 'escl'],
                      'límites': (-inf, inf),
                      'tipo': 'cont'
                      },
         'Potencial': {'scipy': estad.powerlaw,
                       'paráms': ['a', 'ubic', 'escl'],
                       'límites': (0, 1),
                       'tipo': 'cont'
                       },
         'PotencialLogNormal': {'scipy': estad.powerlognorm,
                                'paráms': ['c', 's', 'ubic', 'escl'],
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'PotencialNormal': {'scipy': estad.powernorm,
                             'paráms': ['c', 'ubic', 'escl'],
                             'límites': (0, inf),
                             'tipo': 'cont'
                             },
         'R': {'scipy': estad.rdist,
               'paráms': ['c', 'ubic', 'escl'],
               'límites': (-1, 1),
               'tipo': 'cont'
               },
         'Recíproco': {'scipy': estad.reciprocal,
                       'paráms': ['a', 'b', 'ubic', 'escl'],
                       'límites': (0, 1),  # El límite es ('a', 'b')
                       'tipo': 'cont'
                       },
         'Rayleigh': {'scipy': estad.rayleigh,
                      'paráms': ['ubic', 'escl'],
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'Rice': {'scipy': estad.rice,
                  'paráms': ['b', 'ubic', 'escl'],
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'GaussInversaRecíproco': {'scipy': estad.recipinvgauss,
                                   'paráms': ['mu', 'ubic', 'escl'],
                                   'límites': (0, inf),
                                   'tipo': 'cont'
                                   },
         'Semicircular': {'scipy': estad.semicircular,
                          'paráms': ['ubic', 'escl'],
                          'límites': (-1, 1),
                          'tipo': 'cont'
                          },

         'NormalSesgada': {'scipy': estad.skewnorm,
                           'paráms': ['a', 'ubic', 'escl'],
                           'límites': (-inf, inf),
                           'tipo': 'cont'
                           },

         'T': {'scipy': estad.t,
               'paráms': ['df', 'ubic', 'escl'],
               'límites': (-inf, inf),
               'tipo': 'cont'
               },

         'Triang': {'scipy': estad.triang,
                    'paráms': ['c', 'ubic', 'escl'],
                    'límites': (0, 1),  # El límite es ('a', 'b')
                    'tipo': 'cont'
                    },

         'ExponencialTrunc': {'scipy': estad.truncexpon,
                              'paráms': ['b', 'ubic', 'escl'],
                              'límites': (0, 1),  # El límite es (0, 'b')
                              'tipo': 'cont'
                              },

         'NormalTrunc': {'scipy': estad.truncnorm,
                         'paráms': ['a', 'b', 'ubic', 'escl'],
                         'límites': (0, 1),
                         'tipo': 'cont'
                         },

         'TukeyLambda': {'scipy': estad.tukeylambda,
                         'paráms': ['lam', 'ubic', 'escl'],
                         'límites': (-inf, inf),
                         'tipo': 'cont'
                         },
         'Uniforme': {'scipy': estad.uniform,
                      'paráms': ['ubic', 'escl'],
                      'pymc3': True,
                      'límites': (0, 1),  # El límite es ('a', 'b')
                      'tipo': 'cont'
                      },

         'VonMises': {'scipy': estad.vonmises,
                      'paráms': ['kappa', 'ubic', 'escl'],
                      'pymc3': True,
                      'límites': (-pi, pi),
                      'tipo': 'cont'
                      },
         'Wald': {'scipy': estad.wald,
                  'paráms': ['ubic', 'escl'],
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Weibull': {'scipy': estad.weibull_min,
                     'paráms': ['c', 'ubic', 'escl'],
                     'límites': (0, inf),
                     'tipo': 'cont'
                     },
         'WeibullMáximo': {'scipy': estad.weibull_max,
                           'paráms': ['c', 'ubic', 'escl'],
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'CauchyEnvuelto': {'scipy': estad.wrapcauchy,
                            'paráms': ['c', 'ubic', 'escl'],
                            'límites': (0, 2 * pi),
                            'tipo': 'cont'
                            },

         # Distribuciones discretas

         'Bernoulli': {'scipy': estad.bernoulli,
                       'paráms': ['p', 'ubic'],
                       'límites': (0, 1),
                       'tipo': 'discr'
                       },
         'Binomial': {'scipy': estad.binom,
                      'paráms': ['n', 'p', 'ubic'],
                      'límites': (0, 1),  # Límite es de (0, N)
                      'tipo': 'discr'
                      },
         'Boltzmann': {'scipy': estad.boltzmann,
                       'paráms': ['lambda_', 'N', 'ubic'],
                       'límites': (0, 1),  # Límite es de (0, N-1)
                       'tipo': 'discr'
                       },
         'LaplaceDiscreta': {'scipy': estad.dlaplace,
                             'paráms': ['a', 'ubic'],
                             'límites': (-inf, inf),
                             'tipo': 'discr'
                             },
         'Geométrica': {'scipy': estad.geom,
                        'paráms': ['p', 'ubic'],
                        'límites': (1, inf),
                        'tipo': 'discr'
                        },
         'Hypergeométrica': {'scipy': estad.hypergeom,
                             'paráms': ['M', 'n', 'N', 'ubic'],
                             'límites': (0, 1),  # El límite es (0, N)
                             'tipo': 'discr'
                             },
         'Logarítmico': {'scipy': estad.logser,
                         'paráms': ['p', 'ubic'],
                         'límites': (1, inf),
                         'tipo': 'discr'
                         },
         'BinomialNegativo': {'scipy': estad.nbinom,
                              'paráms': ['n', 'p', 'ubic'],
                              'límites': (0, inf),
                              'tipo': 'discr'
                              },
         'Planck': {'scipy': estad.planck,
                    'paráms': ['lambda_', 'ubic'],
                    'límites': (0, inf),
                    'tipo': 'discr'
                    },
         'Poisson': {'scipy': estad.poisson,
                     'paráms': ['mu', 'ubic'],
                     'límites': (0, inf),
                     'tipo': 'discr'
                     },
         'Skellam': {'scipy': estad.skellam,
                     'paráms': ['mu1', 'mu2', 'ubic'],
                     'límites': (-inf, inf),
                     'tipo': 'discr'
                     },
         'UnifDiscr': {'scipy': estad.randint,
                       'paráms': ['low', 'high', 'ubic'],
                       'límites': (0, 1),  # Límite es de ('a', 'b')
                       'tipo': 'discr'
                       },
         'Zipf': {'scipy': estad.zipf,
                  'paráms': ['a', 'ubic'],
                  'límites': (1, inf),
                  'tipo': 'discr'
                  }
         }
