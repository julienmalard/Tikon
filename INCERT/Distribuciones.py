import math as mat
import numpy as np
import scipy.stats as estad
from pymc import Beta, Cauchy, Chi2, Exponential, Exponweib, Gamma, HalfCauchy, HalfNormal, InverseGamma, Laplace, \
    Logistic, Lognormal, NoncentralT, Normal, Pareto, T, TruncatedNormal, Uniform, VonMises, Bernoulli, Binomial, \
    Geometric, Hypergeometric, NegativeBinomial, Poisson, DiscreteUniform


dists = {'cont': {'Alpha': {'scipy': estad.alpha,
                            'pymc': None,
                            'límites': (0, np.inf)
                            },
                  'Anglit': {'scipy': estad.anglit,
                             'pymc': None,
                             'límites': (-mat.pi/4, mat.pi/4)
                             },
                  'Arcsen': {'scipy': estad.arcsine,
                             'pymc': None,
                             'límites': (0, 1)
                             },
                  'Beta': {'scipy': estad.beta,
                           'pymc': Beta,
                           'límites': (0, 1)
                           },
                  'BetaPrima': {'scipy': estad.betaprime,
                                'pymc': None,
                                'límites': (0, np.inf)
                                },
                  'Bradford': {'scipy': estad.bradford,
                               'pymc': None,
                               'límites': (0, 1)
                               },
                  'Burr': {'scipy': estad.burr,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  'Cauchy': {'scipy': estad.cauchy,
                             'pymc': Cauchy,
                             'límites': (-np.inf, np.inf)
                             },
                  'Chi': {'scipy': estad.chi,
                          'pymc': None,
                          'límites': (0, np.inf)
                          },
                  'ChiCuadrado': {'scipy': estad.chi2,
                                  'pymc': Chi2,
                                  'límites': (0, np.inf)
                                  },
                  'Cosine': {'scipy': estad.cosine,
                             'pymc': None,
                             'límites': (-mat.pi, mat.pi)
                             },
                  'DobleGamma': {'scipy': estad.dgamma,
                                 'pymc': None,
                                 'límites': (0, np.inf)
                                 },
                  'DobleWeibull': {'scipy': estad.dweibull,
                                   'pymc': None,
                                   'límites': (0, np.inf)
                                   },
                  'Erlang': {'scipy': estad.erlang,
                             'pymc': None,
                             'límites': (0, np.inf)
                             },
                  'Exponencial': {'scipy': estad.arcsine,
                                  'pymc': Exponential,
                                  'límites': (0, np.inf)
                                  },
                  'NormalExponencial': {'scipy': estad.arcsine,
                                        'pymc': None,
                                        'límites': (-np.inf, np.inf)
                                        },
                  'WeibullExponencial': {'scipy': estad.arcsine,
                                         'pymc': Exponweib,
                                         'límites': (0, np.inf)
                                         },
                  'PotencialExponencial': {'scipy': estad.exponpow,
                                           'pymc': None,
                                           'límites': (0, np.inf)
                                           },
                  'F': {'scipy': estad.f,
                        'pymc': None,
                        'límites': (0, np.inf)
                        },
                  'BirnbaumSaunders': {'scipy': estad.fatiguelife,
                                       'pymc': None,
                                       'límites': (0, np.inf)
                                       },
                  'Fisk': {'scipy': estad.fisk,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  'CauchyDoblada': {'scipy': estad.foldcauchy,
                                    'pymc': None,
                                    'límites': (0, np.inf)
                                    },
                  'NormalDoblada': {'scipy': estad.foldnorm,
                                    'pymc': None,
                                    'límites': (0, np.inf)
                                    },
                  'FrechetDerecha': {'scipy': estad.frechet_r,
                                     'pymc': None,
                                     'límites': (0, np.inf)
                                     },
                  # 'FrechetIzquierda': {'scipy': estad.frechet_l,
                  #               'pymc': None,
                  #               'límites': (-np.inf, 0)
                  #               },
                  'LogísticaGeneral': {'scipy': estad.genlogistic,
                                       'pymc': None,
                                       'límites': (0, np.inf)
                                       },
                  'NormalGeneral': {'scipy': estad.gennorm,
                                    'pymc': None,
                                    'límites': (-np.inf, np.inf)
                                    },
                  'ParetoGeneral': {'scipy': estad.genpareto,
                                    'pymc': None,
                                    'límites': (0, np.inf)
                                    },
                  'ExponencialGeneral': {'scipy': estad.genexpon,
                                         'pymc': None,
                                         'límites': (0, np.inf)
                                         },
                  'ExtremaGeneral': {'scipy': estad.genextreme,
                                     'pymc': None,
                                     'límites': (-np.inf, np.inf)
                                     },
                  'HyperGauss': {'scipy': estad.gausshyper,
                                 'pymc': None,
                                 'límites': (0, 1)
                                 },
                  'Gamma': {'scipy': estad.gamma,
                            'pymc': Gamma,
                            'límites': (0, np.inf)
                            },
                  'GammaGeneral': {'scipy': estad.gengamma,
                                   'pymc': None,
                                   'límites': (0, np.inf)
                                   },
                  'MitadLogísticaGeneral': {'scipy': estad.genhalflogistic,
                                            'pymc': None,
                                            'límites': (0, 1)  # El límite es (0, 1/c)
                                            },
                  'Gilbrat': {'scipy': estad.gilbrat,
                              'pymc': None,
                              'límites': (0, np.inf)
                              },
                  'Gompertz': {'scipy': estad.gompertz,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'GumbelDerecho': {'scipy': estad.gumbel_r,
                                    'pymc': None,
                                    'límites': (-np.inf, np.inf)
                                    },
                  'GumbelIzquierda': {'scipy': estad.gumbel_l,
                                      'pymc': None,
                                      'límites': (-np.inf, np.inf)
                                      },
                  'MitadCauchy': {'scipy': estad.halfcauchy,
                                  'pymc': HalfCauchy,
                                  'límites': (0, np.inf)
                                  },
                  'MitadLogística': {'scipy': estad.halflogistic,
                                     'pymc': None,
                                     'límites': (0, np.inf)
                                     },
                  'MitadNormal': {'scipy': estad.halfnorm,
                                  'pymc': HalfNormal,
                                  'límites': (0, np.inf)
                                  },
                  'MitadNormalGeneral': {'scipy': estad.halfgennorm,
                                         'pymc': None,
                                         'límites': (0, np.inf)
                                         },
                  'HyperSecante': {'scipy': estad.hypsecant,
                                   'pymc': None,
                                   'límites': (-np.inf, np.inf)
                                   },
                  'GammaInversa': {'scipy': estad.invgamma,
                                   'pymc': InverseGamma,
                                   'límites': (0, np.inf)
                                   },
                  'GaussInversa': {'scipy': estad.invgauss,
                                   'pymc': None,
                                   'límites': (0, np.inf)
                                   },
                  'WeibullInversa': {'scipy': estad.invweibull,
                                     'pymc': None,
                                     'límites': (0, np.inf)
                                     },
                  'JohnsonSB': {'scipy': estad.johnsonsb,
                                'pymc': None,
                                'límites': (0, 1)
                                },
                  'JohnsonSU': {'scipy': estad.johnsonsu,
                                'pymc': None,
                                'límites': (0, np.inf)
                                },
                  'KSUno': {'scipy': estad.ksone,
                            'pymc': None,
                            'límites': (0, np.inf)
                            },
                  'KSDosNLargo': {'scipy': estad.kstwobign,
                                  'pymc': None,
                                  'límites': (0, np.inf)
                                  },
                  'Laplace': {'scipy': estad.laplace,
                              'pymc': Laplace,
                              'límites': (-np.inf, np.inf)
                              },
                  'Levy': {'scipy': estad.levy,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  # 'LevyIzquierda': {'scipy': estad.levy_l,
                  #            'pymc': None,
                  #            'límites': (-np.inf, 0)
                  #            },
                  'LevyEstable': {'scipy': estad.levy_stable,
                                  'pymc': None,
                                  'límites': (0, np.inf)
                                  },
                  'Logística': {'scipy': estad.logistic,
                                'pymc': Logistic,
                                'límites': (-np.inf, np.inf)
                                },
                  'LogGamma': {'scipy': estad.loggamma,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'LogLaplace': {'scipy': estad.loglaplace,
                                 'pymc': None,
                                 'límites': (0, np.inf)
                                 },
                  'LogNormal': {'scipy': estad.lognorm,
                                'pymc': Lognormal,
                                'límites': (0, np.inf)
                                },
                  'Lomax': {'scipy': estad.lomax,
                            'pymc': None,
                            'límites': (0, np.inf)
                            },
                  'Maxwell': {'scipy': estad.maxwell,
                              'pymc': None,
                              'límites': (0, np.inf)
                              },
                  'Mielke': {'scipy': estad.mielke,
                             'pymc': None,
                             'límites': (0, np.inf)
                             },
                  'Nakagami': {'scipy': estad.nakagami,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'Chi2NoCentral': {'scipy': estad.ncx2,
                                    'pymc': None,
                                    'límites': (0, np.inf)
                                    },
                  'FNoCentral': {'scipy': estad.ncf,
                                 'pymc': None,
                                 'límites': (0, np.inf)
                                 },
                  'TNoCentral': {'scipy': estad.nct,
                                 'pymc': NoncentralT,
                                 'límites': (-np.inf, np.inf)
                                 },
                  'Normal': {'scipy': estad.norm,
                             'pymc': Normal,
                             'límites': (-np.inf, np.inf)
                             },
                  'Pareto': {'scipy': estad.pareto,
                             'pymc': Pareto,
                             'límites': (1, np.inf)
                             },
                  'Pearson3': {'scipy': estad.pearson3,
                               'pymc': None,
                               'límites': (-np.inf, np.inf)
                               },
                  'Potencial': {'scipy': estad.powerlaw,
                                'pymc': None,
                                'límites': (0, 1)
                                },
                  'PotencialLogNormal': {'scipy': estad.powerlognorm,
                                         'pymc': None,
                                         'límites': (0, np.inf)
                                         },
                  'PotencialNormal': {'scipy': estad.powernorm,
                                      'pymc': None,
                                      'límites': (0, np.inf)
                                      },
                  'R': {'scipy': estad.rdist,
                        'pymc': None,
                        'límites': (-1, 1)
                        },
                  'Recíproco': {'scipy': estad.reciprocal,
                                'pymc': None,
                                'límites': (0, 1)  # El límite es (a, b)
                                },
                  'Rayleigh': {'scipy': estad.rayleigh,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'Rice': {'scipy': estad.rice,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  'GaussInversaRecíproco': {'scipy': estad.recipinvgauss,
                                            'pymc': None,
                                            'límites': (0, np.inf)
                                            },
                  'Semicircular': {'scipy': estad.semicircular,
                                   'pymc': None,
                                   'límites': (-1, 1)
                                   },
                  'T': {'scipy': estad.t,
                        'pymc': T,
                        'límites': (-np.inf, np.inf)
                        },
                  'Triang': {'scipy': estad.triang,
                             'pymc': None,
                             'límites': (0, 1)  # El límite es (a, b)
                             },
                  'ExponencialTrunc': {'scipy': estad.truncexpon,
                                       'pymc': None,
                                       'límites': (0, 1)  # El límite es (0, b)
                                       },
                  'NormalTrunc': {'scipy': estad.truncnorm,
                                  'pymc': TruncatedNormal,
                                  'límites': (0, 1)  # El límite es (a, b)
                                  },
                  'TukeyLambda': {'scipy': estad.tukeylambda,
                                  'pymc': None,
                                  'límites': (-np.inf, np.inf)
                                  },
                  'Uniforme': {'scipy': estad.uniform,
                               'pymc': Uniform,
                               'límites': (0, 1)  # El límite es (a, b)
                               },
                  'VonMises': {'scipy': estad.vonmises,
                               'pymc': VonMises,
                               'límites': (-mat.pi, mat.pi)
                               },
                  'VonMisesLín': {'scipy': estad.vonmises_line,
                                  'pymc': None,
                                  'límites': (-mat.pi, mat.pi)
                                  },
                  'Wald': {'scipy': estad.wald,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  'WeibullMínimo': {'scipy': estad.weibull_min,
                                    'pymc': None,
                                    'límites': (0, np.inf)
                                    },
                  'WeibullMáximo': {'scipy': estad.weibull_max,
                                    'pymc': None,
                                    'límites': (0, np.inf)
                                    },
                  'CauchyEnvuelto': {'scipy': estad.wrapcauchy,
                                     'pymc': None,
                                     'límites': (0, 2*mat.pi)
                                     }
                  },

         'disc': {'Bernoulli': {'scipy': estad.bernoulli,
                                'pymc': Bernoulli,
                                'límites': (0, 1)
                                },
                  'Binomial': {'scipy': estad.binom,
                               'pymc': Binomial,
                               'límites': (0, 1)  # Límite es de (0, N)
                               },
                  'Boltzmann': {'scipy': estad.boltzmann,
                                'pymc': None,
                                'límites': (0, 1)  # Límite es de (0, N-1)
                                },
                  'LaplaceDiscreta': {'scipy': estad.dlaplace,
                                      'pymc': None,
                                      'límites': (-np.inf, np.inf)
                                      },
                  'Geométrica': {'scipy': estad.geom,
                                 'pymc': Geometric,
                                 'límites': (1, np.inf)
                                 },
                  'Hypergeométrica': {'scipy': estad.hypergeom,
                                      'pymc': Hypergeometric,
                                      'límites': (0, 1)  # El límite es (0, N)
                                      },
                  'Logarítmico': {'scipy': estad.logser,
                                  'pymc': None,
                                  'límites': (1, np.inf)
                                  },
                  'BinomialNegativo': {'scipy': estad.nbinom,
                                       'pymc': NegativeBinomial,
                                       'límites': (0, np.inf)
                                       },
                  'Planck': {'scipy': estad.planck,
                             'pymc': None,
                             'límites': (0, np.inf)
                             },
                  'Poisson': {'scipy': estad.poisson,
                              'pymc': Poisson,
                              'límites': (0, np.inf)
                              },
                  'EnteroAleatorio': {'scipy': estad.randint,
                                      'pymc': DiscreteUniform,
                                      'límites': (0, 1)  # Límite es de (a, b)
                                      },
                  'Skellam': {'scipy': estad.skellam,
                              'pymc': None,
                              'límites': (-np.inf, np.inf)
                              },
                  'Zipf': {'scipy': estad.zipf,
                           'pymc': None,
                           'límites': (1, np.inf)
                           }
                  }
         }


def texto_a_distscipy(texto):
    """

    :type texto: str
    """
    nombre, paráms = texto.split('~')

    for categ_dist in dists:
        for ll, dic_dist in dists[categ_dist].items():
            if ll == nombre:
                dist = dic_dist['scipy'](paráms)
                return dist

    raise ValueError('No se pudo decodar la distribución "%s".' % texto)


def ajustar_dist(datos, límites, cont, pymc=False, nombre=None):
    """
    Esta función, tomando las límites teoréticas de una distribución y una serie de datos proveniendo de dicha
      distribución, escoge la distribución de Scipy o PyMC la más apropriada y ajusta sus parámetros. Al momento
      únicamente puede generar distribuciones continuas.

    :param datos: Lista de parámetros
    :type datos: list

    :param nombre:
    :type nombre: str

    :param cont:
    :type cont: bool

    :param pymc:
    :type pymc: bool

    :param límites: Las límites teoréticas de la distribucion (p. ej., (0, np.inf), (-np.inf, np.inf), etc.)
    :type límites: tuple

    :return: Distribución PyMC y su ajuste (p)
    :rtype: (pymc.Stochastic, float)
    """

    if cont:
        categ_dist = 'cont'
    else:
        categ_dist = 'discr'

    mín_dist_datos, máx_dist_datos = límites

    mejor_ajuste = dict(dist=None, p=0)

    for dist, dic_dist in dists[categ_dist].items():
        if pymc is False or dic_dist['pymc'] is not None:

            mín_dist, máx_dist = dic_dist['límites']

            lím_igual = (mín_dist == mín_dist_datos == np.inf) or \
                        (not np.isinf(mín_dist) and not np.isinf(mín_dist_datos)) and \
                        ((máx_dist == máx_dist_datos == np.inf) or
                         (not np.isinf(máx_dist) and not np.isinf(máx_dist_datos)))

            if lím_igual:
                args = dic_dist['scipy'].fit(datos)
                p = estad.kstest(datos, dist, args=args)[1]
                if p < mejor_ajuste['p']:
                    mejor_ajuste['p'] = p
                    if pymc:
                        mejor_ajuste['dist'] = dic_dist['pymc'](nombre, *args)
                    else:
                        mejor_ajuste['dist'] = dic_dist['scipy'](*args)

    if mejor_ajuste['p'] <= 0.10:
        raise Warning('El ajuste de la mejor distribución quedó muy mala (p = %f).' % round(mejor_ajuste['p'], 4))

    return mejor_ajuste['dist'], mejor_ajuste['p']
