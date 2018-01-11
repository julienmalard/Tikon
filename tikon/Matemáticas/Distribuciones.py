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
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'Anglit': {'scipy': estad.anglit,
                    'límites': (-pi / 4, pi / 4),
                    'tipo': 'cont'
                    },
         'Arcsen': {'scipy': estad.arcsine,
                    'límites': (0, 1),
                    'tipo': 'cont'
                    },
         'Beta': {'scipy': estad.beta,
                  'límites': (0, 1),
                  'tipo': 'cont'
                  },
         'BetaPrima': {'scipy': estad.betaprime,
                       'límites': (0, inf),
                       'tipo': 'cont'
                       },
         'Bradford': {'scipy': estad.bradford,
                      'límites': (0, 1),
                      'tipo': 'cont'
                      },
         'Burr': {'scipy': estad.burr,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Cauchy': {'scipy': estad.cauchy,
                    'límites': (-inf, inf),
                    'tipo': 'cont'
                    },
         'Chi': {'scipy': estad.chi,
                 'límites': (0, inf),
                 'tipo': 'cont'
                 },
         'Chi2': {'scipy': estad.chi2,
                  'pymc3': True,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Cosine': {'scipy': estad.cosine,
                    'límites': (-pi, pi),
                    'tipo': 'cont'
                    },
         'DobleGamma': {'scipy': estad.dgamma,
                        'límites': (0, inf),
                        'tipo': 'cont'
                        },
         'DobleWeibull': {'scipy': estad.dweibull,
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'Erlang': {'scipy': estad.erlang,
                    'límites': (0, inf),
                    'tipo': 'cont'
                    },
         'Exponencial': {'scipy': estad.expon,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'NormalExponencial': {'scipy': estad.exponnorm,
                               'límites': (-inf, inf),
                               'tipo': 'cont'
                               },
         'WeibullExponencial': {'scipy': estad.exponweib,
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'PotencialExponencial': {'scipy': estad.exponpow,
                                  'límites': (0, inf),
                                  'tipo': 'cont'
                                  },
         'F': {'scipy': estad.f,
               'límites': (0, inf),
               'tipo': 'cont'
               },

         'BirnbaumSaunders': {'scipy': estad.fatiguelife,
                              'límites': (0, inf),
                              'tipo': 'cont'
                              },
         'Fisk': {'scipy': estad.fisk,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'CauchyDoblada': {'scipy': estad.foldcauchy,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'NormalDoblada': {'scipy': estad.foldnorm,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'FrechetDerecha': {'scipy': estad.frechet_r,
                            'límites': (0, inf),
                            'tipo': 'cont'
                            },
         # 'FrechetIzquierda': {'scipy': estad.frechet_l,
         #               'pymc': None,
         #               'límites': (-inf, 0)
         #               },
         'LogísticaGeneral': {'scipy': estad.genlogistic,
                              'límites': (0, inf),
                              'tipo': 'cont'
                              },
         'NormalGeneral': {'scipy': estad.gennorm,
                           'límites': (-inf, inf),
                           'tipo': 'cont'
                           },
         'ParetoGeneral': {'scipy': estad.genpareto,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'ExponencialGeneral': {'scipy': estad.genexpon,
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'ExtremaGeneral': {'scipy': estad.genextreme,
                            'límites': (-inf, inf),
                            'tipo': 'cont'
                            },
         'HyperGauss': {'scipy': estad.gausshyper,
                        'límites': (0, 1),
                        'tipo': 'cont'
                        },
         'Gamma': {'scipy': estad.gamma,
                   'pymc3': True,
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'GammaGeneral': {'scipy': estad.gengamma,
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'MitadLogísticaGeneral': {'scipy': estad.genhalflogistic,
                                   'límites': (0, 1),  # El límite es (0, 1/c)
                                   'tipo': 'cont'
                                   },
         'Gilbrat': {'scipy': estad.gilbrat,
                     'límites': (0, inf),
                     'tipo': 'cont'
                     },
         'Gompertz': {'scipy': estad.gompertz,
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'GumbelDerecho': {'scipy': estad.gumbel_r,
                           'límites': (-inf, inf),
                           'tipo': 'cont'
                           },
         'GumbelIzquierda': {'scipy': estad.gumbel_l,
                             'límites': (-inf, inf),
                             'tipo': 'cont'
                             },
         'MitadCauchy': {'scipy': estad.halfcauchy,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'MitadLogística': {'scipy': estad.halflogistic,
                            'límites': (0, inf),
                            'tipo': 'cont'
                            },
         'MitadNormal': {'scipy': estad.halfnorm,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'MitadNormalGeneral': {'scipy': estad.halfgennorm,
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'HyperSecante': {'scipy': estad.hypsecant,
                          'límites': (-inf, inf),
                          'tipo': 'cont'
                          },
         'GammaInversa': {'scipy': estad.invgamma,
                          'pymc3': True,
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'GaussInversa': {'scipy': estad.invgauss,
                          'límites': (0, inf),
                          'tipo': 'cont'
                          },
         'WeibullInversa': {'scipy': estad.invweibull,
                            'límites': (0, inf),
                            'tipo': 'cont'
                            },
         'JohnsonSB': {'scipy': estad.johnsonsb,
                       'límites': (0, 1),
                       'tipo': 'cont'
                       },
         'JohnsonSU': {'scipy': estad.johnsonsu,
                       'límites': (0, inf),
                       'tipo': 'cont'
                       },
         'KSUno': {'scipy': estad.ksone,
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'KSDosNLargo': {'scipy': estad.kstwobign,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'Laplace': {'scipy': estad.laplace,
                     'pymc3': True,
                     'límites': (-inf, inf),
                     'tipo': 'cont'
                     },
         'Levy': {'scipy': estad.levy,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         # 'LevyIzquierda': {'scipy': estad.levy_l,
         #            'pymc': None,
         #            'límites': (-inf, 0)
         #            },
         'LevyEstable': {'scipy': estad.levy_stable,
                         'límites': (0, inf),
                         'tipo': 'cont'
                         },
         'Logística': {'scipy': estad.logistic,
                       'límites': (-inf, inf),
                       'tipo': 'cont'
                       },
         'LogGamma': {'scipy': estad.loggamma,
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'LogLaplace': {'scipy': estad.loglaplace,
                        'límites': (0, inf),
                        'tipo': 'cont'
                        },
         'LogNormal': {'scipy': estad.lognorm,
                       'límites': (0, inf),
                       'tipo': 'cont'
                       },
         'Lomax': {'scipy': estad.lomax,
                   'límites': (0, inf),
                   'tipo': 'cont'
                   },
         'Maxwell': {'scipy': estad.maxwell,
                     'límites': (0, inf),
                     'tipo': 'cont'
                     },
         'Mielke': {'scipy': estad.mielke,
                    'límites': (0, inf),
                    'tipo': 'cont'
                    },
         'Nakagami': {'scipy': estad.nakagami,
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'Chi2NoCentral': {'scipy': estad.ncx2,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'FNoCentral': {'scipy': estad.ncf,
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
                    'límites': (-inf, inf),
                    'tipo': 'cont'
                    },
         'Pareto': {'scipy': estad.pareto,
                    'límites': (1, inf),
                    'tipo': 'cont'
                    },
         'Pearson3': {'scipy': estad.pearson3,
                      'límites': (-inf, inf),
                      'tipo': 'cont'
                      },
         'Potencial': {'scipy': estad.powerlaw,
                       'límites': (0, 1),
                       'tipo': 'cont'
                       },
         'PotencialLogNormal': {'scipy': estad.powerlognorm,
                                'límites': (0, inf),
                                'tipo': 'cont'
                                },
         'PotencialNormal': {'scipy': estad.powernorm,
                             'límites': (0, inf),
                             'tipo': 'cont'
                             },
         'R': {'scipy': estad.rdist,
               'límites': (-1, 1),
               'tipo': 'cont'
               },
         'Recíproco': {'scipy': estad.reciprocal,
                       'límites': (0, 1),  # El límite es (a, b)

                       'tipo': 'cont'
                       },
         'Rayleigh': {'scipy': estad.rayleigh,
                      'límites': (0, inf),
                      'tipo': 'cont'
                      },
         'Rice': {'scipy': estad.rice,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'GaussInversaRecíproco': {'scipy': estad.recipinvgauss,
                                   'límites': (0, inf),
                                   'tipo': 'cont'
                                   },
         'Semicircular': {'scipy': estad.semicircular,
                          'límites': (-1, 1),
                          'tipo': 'cont'
                          },

         'NormalSesgada': {'scipy': estad.skewnorm,
                           'límites': (-inf, inf),
                           'tipo': 'cont'
                           },

         'T': {'scipy': estad.t,
               'límites': (-inf, inf),
               'tipo': 'cont'
               },

         'Triang': {'scipy': estad.triang,
                    'límites': (0, 1),  # El límite es (a, b)
                    'tipo': 'cont'
                    },

         'ExponencialTrunc': {'scipy': estad.truncexpon,
                              'límites': (0, 1),  # El límite es (0, b)
                              'tipo': 'cont'
                              },

         'NormalTrunc': {'scipy': estad.truncnorm,
                         'límites': (0, 1),
                         'tipo': 'cont'
                         },

         'TukeyLambda': {'scipy': estad.tukeylambda,
                         'límites': (-inf, inf),
                         'tipo': 'cont'
                         },
         'Uniforme': {'scipy': estad.uniform,
                      'pymc3': True,
                      'límites': (0, 1),  # El límite es (a, b)
                      'tipo': 'cont'
                      },

         'VonMises': {'scipy': estad.vonmises,
                      'pymc3': True,
                      'límites': (-pi, pi),
                      'tipo': 'cont'
                      },

         'VonMisesLín': {'scipy': estad.vonmises_line,
                         'límites': (-pi, pi),
                         'tipo': 'cont'
                         },
         'Wald': {'scipy': estad.wald,
                  'límites': (0, inf),
                  'tipo': 'cont'
                  },
         'Weibull': {'scipy': estad.weibull_min,
                     'límites': (0, inf),
                     'tipo': 'cont'
                     },
         'WeibullMáximo': {'scipy': estad.weibull_max,
                           'límites': (0, inf),
                           'tipo': 'cont'
                           },
         'CauchyEnvuelto': {'scipy': estad.wrapcauchy,
                            'límites': (0, 2 * pi),
                            'tipo': 'cont'
                            },

         # Distribuciones discretas

         'Bernoulli': {'scipy': estad.bernoulli,
                       'límites': (0, 1),
                       'tipo': 'discr'
                       },
         'Binomial': {'scipy': estad.binom,
                      'límites': (0, 1),  # Límite es de (0, N)
                      'tipo': 'discr'
                      },
         'Boltzmann': {'scipy': estad.boltzmann,
                       'límites': (0, 1),  # Límite es de (0, N-1)
                       'tipo': 'discr'
                       },
         'LaplaceDiscreta': {'scipy': estad.dlaplace,
                             'límites': (-inf, inf),
                             'tipo': 'discr'
                             },
         'Geométrica': {'scipy': estad.geom,
                        'límites': (1, inf),
                        'tipo': 'discr'
                        },
         'Hypergeométrica': {'scipy': estad.hypergeom,
                             'límites': (0, 1),  # El límite es (0, N)
                             'tipo': 'discr'
                             },
         'Logarítmico': {'scipy': estad.logser,
                         'límites': (1, inf),
                         'tipo': 'discr'
                         },
         'BinomialNegativo': {'scipy': estad.nbinom,
                              'pymc3': True,
                              'límites': (0, inf),
                              'tipo': 'discr'
                              },
         'Planck': {'scipy': estad.planck,
                    'límites': (0, inf),
                    'tipo': 'discr'
                    },
         'Poisson': {'scipy': estad.poisson,
                     'límites': (0, inf),
                     'tipo': 'discr'
                     },
         'Skellam': {'scipy': estad.skellam,
                     'límites': (-inf, inf),
                     'tipo': 'discr'
                     },
         'UnifDiscr': {'scipy': estad.randint,
                       'límites': (0, 1),  # Límite es de (a, b)
                       'tipo': 'discr'
                       },
         'Zipf': {'scipy': estad.zipf,
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
