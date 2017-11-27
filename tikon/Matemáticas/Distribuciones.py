import math as mat

import numpy as np
try:
    import pymc3 as pm3
except ImportError:
    pm3 = None

import scipy.stats as estad
from pymc import Beta, Cauchy, Chi2, Degenerate, Exponential, Exponweib, Gamma, HalfCauchy, HalfNormal, InverseGamma, \
    Laplace, Logistic, Lognormal, Normal, Pareto, T, Uniform, VonMises, \
    Bernoulli, Binomial, Geometric, Hypergeometric, NegativeBinomial, Poisson, DiscreteUniform, TruncatedNormal, \
    Weibull


# Par asimplificar el código (un poquitísimo)
inf = np.inf
pi = mat.pi

# Un diccionario de las distribuciones y de sus objetos de SciPy y de PyMC correspondientes.
dists = {'Alpha': {'scipy': estad.alpha,
                   'pymc': None,
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'Anglit': {'scipy': estad.anglit,
                    'pymc': None,
                    'límites': (-pi / 4, pi / 4),
                    'tipo': 'cont'
                    },
         'Arcsen': {'scipy': estad.arcsine,
                    'pymc': None,
                    'límites': (0, 1),
                    'tipo': 'cont'
                    },
         'Beta': {'scipy': estad.beta,
                  'pymc': Beta,
                  'pymc3': True,
                  'límites': (0, 1),
                  'tipo': 'cont'
                  },
         'BetaPrima': {'scipy': estad.betaprime,
                       'pymc': None,
                       'límites': (0, inf),
                       'tipo': 'cont'
                       },
         'Bradford': {'scipy': estad.bradford,
                      'pymc': None,
                      'límites': (0, 1),
                      'tipo': 'cont'
                      },
         'Burr': {'scipy': estad.burr,
                  'pymc': None,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Cauchy': {'scipy': estad.cauchy,
                    'pymc': Cauchy,
                    'pymc3': True,
                    'límites': (-inf, inf),
                    'tipo': 'cont'
                    },
         'Chi': {'scipy': estad.chi,
                 'pymc': None,
                 'límites': (0, inf),
                 'tipo': 'cont'
                 },
         'Chi2': {'scipy': estad.chi2,
                  'pymc': Chi2,
                  'pymc3': True,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Cosine': {'scipy': estad.cosine,
                    'pymc': None,
                    'límites': (-pi, pi),
                    'tipo': 'cont'
                    },
         'Degenerada': {'scipy': None,
                        'pymc': Degenerate,
                        'límites': None,
                        'tipo': 'cont'},
         'DobleGamma': {'scipy': estad.dgamma,
                        'pymc': None,
                        'límites': (0, inf),
                        'tipo': 'cont'
                        },
         'DobleWeibull': {'scipy': estad.dweibull,
                          'pymc': None,
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'Erlang': {'scipy': estad.erlang,
                    'pymc': None,
                    'límites': (0, inf),
                    'tipo': 'cont'
                    },
         'Exponencial': {'scipy': estad.expon,
                         'pymc': Exponential,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'NormalExponencial': {'scipy': estad.exponnorm,
                               'pymc': None,
                               'pymc3': True,
                               'límites': (-inf, inf),
                               'tipo': 'cont'
                               },
         'WeibullExponencial': {'scipy': estad.exponweib,
                                'pymc': Exponweib,
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'PotencialExponencial': {'scipy': estad.exponpow,
                                  'pymc': None,
                                  'límites': (0, inf),
                                  'tipo': 'cont'
                                  },
         'F': {'scipy': estad.f,
               'pymc': None,
               'límites': (0, inf),
               'tipo': 'cont'
               },

         'BirnbaumSaunders': {'scipy': estad.fatiguelife,
                              'pymc': None,
                              'límites': (0, inf),
                              'tipo': 'cont'
                              },
         'Fisk': {'scipy': estad.fisk,
                  'pymc': None,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'CauchyDoblada': {'scipy': estad.foldcauchy,
                           'pymc': None,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'NormalDoblada': {'scipy': estad.foldnorm,
                           'pymc': None,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'FrechetDerecha': {'scipy': estad.frechet_r,
                            'pymc': None,
                            'límites': (0, inf),
                            'tipo': 'cont'
                            },
         # 'FrechetIzquierda': {'scipy': estad.frechet_l,
         #               'pymc': None,
         #               'límites': (-inf, 0)
         #               },
         'LogísticaGeneral': {'scipy': estad.genlogistic,
                              'pymc': None,
                              'límites': (0, inf),
                              'tipo': 'cont'
                              },
         'NormalGeneral': {'scipy': estad.gennorm,
                           'pymc': None,
                           'límites': (-inf, inf),
                           'tipo': 'cont'
                           },
         'ParetoGeneral': {'scipy': estad.genpareto,
                           'pymc': None,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'ExponencialGeneral': {'scipy': estad.genexpon,
                                'pymc': None,
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'ExtremaGeneral': {'scipy': estad.genextreme,
                            'pymc': None,
                            'límites': (-inf, inf),
                            'tipo': 'cont'
                            },
         'HyperGauss': {'scipy': estad.gausshyper,
                        'pymc': None,
                        'límites': (0, 1),
                        'tipo': 'cont'
                        },
         'Gamma': {'scipy': estad.gamma,
                   'pymc': Gamma,
                   'pymc3': True,
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'GammaGeneral': {'scipy': estad.gengamma,
                          'pymc': None,
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'MitadLogísticaGeneral': {'scipy': estad.genhalflogistic,
                                   'pymc': None,
                                   'límites': (0, 1),  # El límite es (0, 1/c)
                                   'tipo': 'cont'
                                   },
         'Gilbrat': {'scipy': estad.gilbrat,
                     'pymc': None,
                     'límites': (0, inf),
                     'tipo': 'cont'
                     },
         'Gompertz': {'scipy': estad.gompertz,
                      'pymc': None,
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'GumbelDerecho': {'scipy': estad.gumbel_r,
                           'pymc': None,
                           'límites': (-inf, inf),
                           'tipo': 'cont'
                           },
         'GumbelIzquierda': {'scipy': estad.gumbel_l,
                             'pymc': None,
                             'límites': (-inf, inf),
                             'tipo': 'cont'
                             },
         'MitadCauchy': {'scipy': estad.halfcauchy,
                         'pymc': HalfCauchy,
                         'pymc3': True,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'MitadLogística': {'scipy': estad.halflogistic,
                            'pymc': None,
                            'límites': (0, inf),
                            'tipo': 'cont'
                            },
         'MitadNormal': {'scipy': estad.halfnorm,
                         'pymc': HalfNormal,
                         'pymc3': True,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'MitadNormalGeneral': {'scipy': estad.halfgennorm,
                                'pymc': None,
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'HyperSecante': {'scipy': estad.hypsecant,
                          'pymc': None,
                          'límites': (-inf, inf),
                          'tipo': 'cont'
                          },
         'GammaInversa': {'scipy': estad.invgamma,
                          'pymc': InverseGamma,
                          'pymc3': True,
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'GaussInversa': {'scipy': estad.invgauss,
                          'pymc': None,
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'WeibullInversa': {'scipy': estad.invweibull,
                            'pymc': None,
                            'límites': (0, inf),
                            'tipo': 'cont'
                            },
         'JohnsonSB': {'scipy': estad.johnsonsb,
                       'pymc': None,
                       'límites': (0, 1),
                       'tipo': 'cont'
                       },
         'JohnsonSU': {'scipy': estad.johnsonsu,
                       'pymc': None,
                       'límites': (0, inf),
                       'tipo': 'cont'
                       },
         'KSUno': {'scipy': estad.ksone,
                   'pymc': None,
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'KSDosNLargo': {'scipy': estad.kstwobign,
                         'pymc': None,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'Laplace': {'scipy': estad.laplace,
                     'pymc': Laplace,
                     'pymc3': True,
                     'límites': (-inf, inf),
                     'tipo': 'cont'
                     },
         'Levy': {'scipy': estad.levy,
                  'pymc': None,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         # 'LevyIzquierda': {'scipy': estad.levy_l,
         #            'pymc': None,
         #            'límites': (-inf, 0)
         #            },
         'LevyEstable': {'scipy': estad.levy_stable,
                         'pymc': None,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'Logística': {'scipy': estad.logistic,
                       'pymc': Logistic,
                       'límites': (-inf, inf),
                       'tipo': 'cont'
                       },
         'LogGamma': {'scipy': estad.loggamma,
                      'pymc': None,
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'LogLaplace': {'scipy': estad.loglaplace,
                        'pymc': None,
                        'límites': (0, inf),
                        'tipo': 'cont'
                        },
         'LogNormal': {'scipy': estad.lognorm,
                       'pymc': Lognormal,
                       'pymc3': True,
                       'límites': (0, inf),
                       'tipo': 'cont'
                       },
         'Lomax': {'scipy': estad.lomax,
                   'pymc': None,
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'Maxwell': {'scipy': estad.maxwell,
                     'pymc': None,
                     'límites': (0, inf),
                     'tipo': 'cont'
                     },
         'Mielke': {'scipy': estad.mielke,
                    'pymc': None,
                    'límites': (0, inf),
                    'tipo': 'cont'
                    },
         'Nakagami': {'scipy': estad.nakagami,
                      'pymc': None,
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'Chi2NoCentral': {'scipy': estad.ncx2,
                           'pymc': None,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'FNoCentral': {'scipy': estad.ncf,
                        'pymc': None,
                        'límites': (0, inf),
                        'tipo': 'cont'
                        },

         # Desactivada por complicación de conversión PyMC-SciPy
         #
         # 'TNoCentral': {'scipy': estad.nct,
         #                'pymc': NoncentralT,
         #                'límites': (-inf, inf),
         #                'tipo': 'cont'
         #                },

         'Normal': {'scipy': estad.norm,
                    'pymc': Normal,
                    'pymc3': True,
                    'límites': (-inf, inf),
                    'tipo': 'cont'
                    },
         'Pareto': {'scipy': estad.pareto,
                    'pymc': Pareto,
                    'pymc3': True,
                    'límites': (1, inf),
                    'tipo': 'cont'
                    },
         'Pearson3': {'scipy': estad.pearson3,
                      'pymc': None,
                      'límites': (-inf, inf),
                      'tipo': 'cont'
                      },
         'Potencial': {'scipy': estad.powerlaw,
                       'pymc': None,
                       'límites': (0, 1),
                       'tipo': 'cont'
                       },
         'PotencialLogNormal': {'scipy': estad.powerlognorm,
                                'pymc': None,
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'PotencialNormal': {'scipy': estad.powernorm,
                             'pymc': None,
                             'límites': (0, inf),
                             'tipo': 'cont'
                             },
         'R': {'scipy': estad.rdist,
               'pymc': None,
               'límites': (-1, 1),
               'tipo': 'cont'
               },
         'Recíproco': {'scipy': estad.reciprocal,
                       'pymc': None,
                       'límites': (0, 1),  # El límite es (a, b)

                       'tipo': 'cont'
                       },
         'Rayleigh': {'scipy': estad.rayleigh,
                      'pymc': None,
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'Rice': {'scipy': estad.rice,
                  'pymc': None,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'GaussInversaRecíproco': {'scipy': estad.recipinvgauss,
                                   'pymc': None,
                                   'límites': (0, inf),
                                   'tipo': 'cont'
                                   },
         'Semicircular': {'scipy': estad.semicircular,
                          'pymc': None,
                          'límites': (-1, 1),
                          'tipo': 'cont'
                          },

         'NormalSesgada': {'scipy': estad.skewnorm,
                           'pymc': None,
                           'pymc3': True,
                           'límites': (-inf, inf),
                           'tipo': 'cont'
                           },

         'T': {'scipy': estad.t,
               'pymc': T,
               'pymc3': True,
               'límites': (-inf, inf),
               'tipo': 'cont'
               },

         'Triang': {'scipy': estad.triang,
                    'pymc': None,
                    'límites': (0, 1),  # El límite es (a, b)
                    'tipo': 'cont'
                    },

         'ExponencialTrunc': {'scipy': estad.truncexpon,
                              'pymc': None,
                              'límites': (0, 1),  # El límite es (0, b)
                              'tipo': 'cont'
                              },

         'NormalTrunc': {'scipy': estad.truncnorm,
                         'pymc': TruncatedNormal,
                         'límites': (0, 1),
                         'tipo': 'cont'
                         },

         'TukeyLambda': {'scipy': estad.tukeylambda,
                         'pymc': None,
                         'límites': (-inf, inf),
                         'tipo': 'cont'
                         },
         'Uniforme': {'scipy': estad.uniform,
                      'pymc': Uniform,
                      'pymc3': True,
                      'límites': (0, 1),  # El límite es (a, b)
                      'tipo': 'cont'
                      },

         'VonMises': {'scipy': estad.vonmises,
                      'pymc': VonMises,
                      'pymc3': True,
                      'límites': (-pi, pi),
                      'tipo': 'cont'
                      },

         'VonMisesLín': {'scipy': estad.vonmises_line,
                         'pymc': None,
                         'límites': (-pi, pi),
                         'tipo': 'cont'
                         },
         'Wald': {'scipy': estad.wald,
                  'pymc': None,
                  'pymc3': True,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Weibull': {'scipy': estad.weibull_min,
                     'pymc': Weibull,
                     'pymc3': True,
                     'límites': (0, inf),
                     'tipo': 'cont'
                     },
         'WeibullMáximo': {'scipy': estad.weibull_max,
                           'pymc': None,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'CauchyEnvuelto': {'scipy': estad.wrapcauchy,
                            'pymc': None,
                            'límites': (0, 2 * pi),
                            'tipo': 'cont'
                            },

         # Distribuciones discretas

         'Bernoulli': {'scipy': estad.bernoulli,
                       'pymc': Bernoulli,
                       'pymc3': True,
                       'límites': (0, 1),
                       'tipo': 'discr'
                       },
         'Binomial': {'scipy': estad.binom,
                      'pymc': Binomial,
                      'pymc3': True,
                      'límites': (0, 1),  # Límite es de (0, N)
                      'tipo': 'discr'
                      },
         'Boltzmann': {'scipy': estad.boltzmann,
                       'pymc': None,
                       'límites': (0, 1),  # Límite es de (0, N-1)
                       'tipo': 'discr'
                       },
         'LaplaceDiscreta': {'scipy': estad.dlaplace,
                             'pymc': None,
                             'límites': (-inf, inf),
                             'tipo': 'discr'
                             },
         'Geométrica': {'scipy': estad.geom,
                        'pymc': Geometric,
                        'pymc3': True,
                        'límites': (1, inf),
                        'tipo': 'discr'
                        },
         'Hypergeométrica': {'scipy': estad.hypergeom,
                             'pymc': Hypergeometric,
                             'límites': (0, 1),  # El límite es (0, N)
                             'tipo': 'discr'
                             },
         'Logarítmico': {'scipy': estad.logser,
                         'pymc': None,
                         'límites': (1, inf),
                         'tipo': 'discr'
                         },
         'BinomialNegativo': {'scipy': estad.nbinom,
                              'pymc': NegativeBinomial,
                              'pymc3': True,
                              'límites': (0, inf),
                              'tipo': 'discr'
                              },
         'Planck': {'scipy': estad.planck,
                    'pymc': None,
                    'límites': (0, inf),
                    'tipo': 'discr'
                    },
         'Poisson': {'scipy': estad.poisson,
                     'pymc': Poisson,
                     'pymc3': True,
                     'límites': (0, inf),
                     'tipo': 'discr'
                     },
         'Skellam': {'scipy': estad.skellam,
                     'pymc': None,
                     'límites': (-inf, inf),
                     'tipo': 'discr'
                     },
         'UnifDiscr': {'scipy': estad.randint,
                       'pymc': DiscreteUniform,
                       'pymc3': True,
                       'límites': (0, 1),  # Límite es de (a, b)
                       'tipo': 'discr'
                       },
         'Zipf': {'scipy': estad.zipf,
                  'pymc': None,
                  'límites': (1, inf),
                  'tipo': 'discr'
                  }
         }


def obt_dist(dist, tipo):
    try:
        dic_dist = dists[dist]
    except KeyError:
        raise ValueError('La distribución "{}" todavía no exite en Tiko\'n.'.format(dist))

    mens_error_tipo = 'La distribución "{}" no tiene la propiedad "{}".'.format(dist, tipo)
    try:
        obj_dist = dic_dist[tipo]
    except KeyError:
        raise ValueError(mens_error_tipo)

    if obj_dist:
        return obj_dist
    else:
        raise ValueError(mens_error_tipo)
