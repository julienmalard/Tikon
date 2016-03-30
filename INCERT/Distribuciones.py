import math as mat
import numpy as np
import scipy.stats as estad
from pymc import Beta, Cauchy, Chi2, Exponential, Exponweib, Gamma, HalfCauchy, HalfNormal, InverseGamma, Laplace, \
    Logistic, Lognormal, NoncentralT, Normal, Pareto, T, TruncatedNormal, Uniform, VonMises, Bernoulli, Binomial, \
    Geometric, Hypergeometric, NegativeBinomial, Poisson, DiscreteUniform


dists = {'cont': {'alpha': {'scipy': estad.alpha,
                            'pymc': None,
                            'límites': (0, np.inf)
                            },
                  'anglit': {'scipy': estad.anglit,
                             'pymc': None,
                             'límites': (-mat.pi/4, mat.pi/4)
                             },
                  'arcsine': {'scipy': estad.arcsine,
                              'pymc': None,
                              'límites': (0, 1)
                              },
                  'beta': {'scipy': estad.beta,
                           'pymc': Beta,
                           'límites': (0, 1)
                           },
                  'betaprime': {'scipy': estad.betaprime,
                                'pymc': None,
                                'límites': (0, np.inf)
                                },
                  'bradford': {'scipy': estad.bradford,
                               'pymc': None,
                               'límites': (0, 1)
                               },
                  'burr': {'scipy': estad.burr,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  'cauchy': {'scipy': estad.cauchy,
                             'pymc': Cauchy,
                             'límites': (-np.inf, np.inf)
                             },
                  'chi': {'scipy': estad.chi,
                          'pymc': None,
                          'límites': (0, np.inf)
                          },
                  'chi2': {'scipy': estad.chi2,
                           'pymc': Chi2,
                           'límites': (0, np.inf)
                           },
                  'cosine': {'scipy': estad.cosine,
                             'pymc': None,
                             'límites': (-mat.pi, mat.pi)
                             },
                  'dgamma': {'scipy': estad.dgamma,
                             'pymc': None,
                             'límites': (0, np.inf)
                             },
                  'dweibull': {'scipy': estad.dweibull,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'erlang': {'scipy': estad.erlang,
                             'pymc': None,
                             'límites': (0, np.inf)
                             },
                  'expon': {'scipy': estad.arcsine,
                            'pymc': Exponential,
                            'límites': (0, np.inf)
                            },
                  'exponnorm': {'scipy': estad.arcsine,
                                'pymc': None,
                                'límites': (-np.inf, np.inf)
                                },
                  'exponweib': {'scipy': estad.arcsine,
                                'pymc': Exponweib,
                                'límites': (0, np.inf)
                                },
                  'exponpow': {'scipy': estad.exponpow,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'f': {'scipy': estad.f,
                        'pymc': None,
                        'límites': (0, np.inf)
                        },
                  'fatiguelife': {'scipy': estad.fatiguelife,
                                  'pymc': None,
                                  'límites': (0, np.inf)
                                  },
                  'fisk': {'scipy': estad.fisk,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  'foldcauchy': {'scipy': estad.foldcauchy,
                                 'pymc': None,
                                 'límites': (0, np.inf)
                                 },
                  'foldnorm': {'scipy': estad.foldnorm,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'frechet_r': {'scipy': estad.frechet_r,
                                'pymc': None,
                                'límites': (0, np.inf)
                                },
                  # 'frechet_l': {'scipy': estad.frechet_l,
                  #               'pymc': None,
                  #               'límites': (-np.inf, 0)
                  #               },
                  'genlogistic': {'scipy': estad.genlogistic,
                                  'pymc': None,
                                  'límites': (0, np.inf)
                                  },
                  'gennorm': {'scipy': estad.gennorm,
                              'pymc': None,
                              'límites': (-np.inf, np.inf)
                              },
                  'genpareto': {'scipy': estad.genpareto,
                                'pymc': None,
                                'límites': (0, np.inf)
                                },
                  'genexpon': {'scipy': estad.genexpon,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'genextreme': {'scipy': estad.genextreme,
                                 'pymc': None,
                                 'límites': (-np.inf, np.inf)
                                 },
                  'gausshyper': {'scipy': estad.gausshyper,
                                 'pymc': None,
                                 'límites': (0, 1)
                                 },
                  'gamma': {'scipy': estad.gamma,
                            'pymc': Gamma,
                            'límites': (0, np.inf)
                            },
                  'gengamma': {'scipy': estad.gengamma,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'genhalflogistic': {'scipy': estad.genhalflogistic,
                                      'pymc': None,
                                      'límites': (0, 1)  # El límite es (0, 1/c)
                                      },
                  'gilbrat': {'scipy': estad.gilbrat,
                              'pymc': None,
                              'límites': (0, np.inf)
                              },
                  'gompertz': {'scipy': estad.gompertz,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'gumbel_r': {'scipy': estad.gumbel_r,
                               'pymc': None,
                               'límites': (-np.inf, np.inf)
                               },
                  'gumbel_l': {'scipy': estad.gumbel_l,
                               'pymc': None,
                               'límites': (-np.inf, np.inf)
                               },
                  'halfcauchy': {'scipy': estad.halfcauchy,
                                 'pymc': HalfCauchy,
                                 'límites': (0, np.inf)
                                 },
                  'halflogistic': {'scipy': estad.halflogistic,
                                   'pymc': None,
                                   'límites': (0, np.inf)
                                   },
                  'halfnorm': {'scipy': estad.halfnorm,
                               'pymc': HalfNormal,
                               'límites': (0, np.inf)
                               },
                  'halfgennorm': {'scipy': estad.halfgennorm,
                                  'pymc': None,
                                  'límites': (0, np.inf)
                                  },
                  'hypsecant': {'scipy': estad.hypsecant,
                                'pymc': None,
                                'límites': (-np.inf, np.inf)
                                },
                  'invgamma': {'scipy': estad.invgamma,
                               'pymc': InverseGamma,
                               'límites': (0, np.inf)
                               },
                  'invgauss': {'scipy': estad.invgauss,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'invweibull': {'scipy': estad.invweibull,
                                 'pymc': None,
                                 'límites': (0, np.inf)
                                 },
                  'johnsonsb': {'scipy': estad.johnsonsb,
                                'pymc': None,
                                'límites': (0, 1)
                                },
                  'johnsonsu': {'scipy': estad.johnsonsu,
                                'pymc': None,
                                'límites': (0, np.inf)
                                },
                  'ksone': {'scipy': estad.ksone,
                            'pymc': None,
                            'límites': (0, np.inf)
                            },
                  'kstwobign': {'scipy': estad.kstwobign,
                                'pymc': None,
                                'límites': (0, np.inf)
                                },
                  'laplace': {'scipy': estad.laplace,
                              'pymc': Laplace,
                              'límites': (-np.inf, np.inf)
                              },
                  'levy': {'scipy': estad.levy,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  # 'levy_l': {'scipy': estad.levy_l,
                  #            'pymc': None,
                  #            'límites': (-np.inf, 0)
                  #            },
                  'levy_stable': {'scipy': estad.levy_stable,
                                  'pymc': None,
                                  'límites': (0, np.inf)
                                  },
                  'logistic': {'scipy': estad.logistic,
                               'pymc': Logistic,
                               'límites': (-np.inf, np.inf)
                               },
                  'loggamma': {'scipy': estad.loggamma,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'loglaplace': {'scipy': estad.loglaplace,
                                 'pymc': None,
                                 'límites': (0, np.inf)
                                 },
                  'lognorm': {'scipy': estad.lognorm,
                              'pymc': Lognormal,
                              'límites': (0, np.inf)
                              },
                  'lomax': {'scipy': estad.lomax,
                            'pymc': None,
                            'límites': (0, np.inf)
                            },
                  'maxwell': {'scipy': estad.maxwell,
                              'pymc': None,
                              'límites': (0, np.inf)
                              },
                  'mielke': {'scipy': estad.mielke,
                             'pymc': None,
                             'límites': (0, np.inf)
                             },
                  'nakagami': {'scipy': estad.nakagami,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'ncx2': {'scipy': estad.ncx2,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  'ncf': {'scipy': estad.ncf,
                          'pymc': None,
                          'límites': (0, np.inf)
                          },
                  'nct': {'scipy': estad.nct,
                          'pymc': NoncentralT,
                          'límites': (-np.inf, np.inf)
                          },
                  'norm': {'scipy': estad.norm,
                           'pymc': Normal,
                           'límites': (-np.inf, np.inf)
                           },
                  'pareto': {'scipy': estad.pareto,
                             'pymc': Pareto,
                             'límites': (1, np.inf)
                             },
                  'pearson3': {'scipy': estad.pearson3,
                               'pymc': None,
                               'límites': (-np.inf, np.inf)
                               },
                  'powerlaw': {'scipy': estad.powerlaw,
                               'pymc': None,
                               'límites': (0, 1)
                               },
                  'powerlognorm': {'scipy': estad.powerlognorm,
                                   'pymc': None,
                                   'límites': (0, np.inf)
                                   },
                  'powernorm': {'scipy': estad.powernorm,
                                'pymc': None,
                                'límites': (0, np.inf)
                                },
                  'rdist': {'scipy': estad.rdist,
                            'pymc': None,
                            'límites': (-1, 1)
                            },
                  'reciprocal': {'scipy': estad.reciprocal,
                                 'pymc': None,
                                 'límites': (0, 1)  # El límite es (a, b)
                                 },
                  'rayleigh': {'scipy': estad.rayleigh,
                               'pymc': None,
                               'límites': (0, np.inf)
                               },
                  'rice': {'scipy': estad.rice,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  'recipinvgauss': {'scipy': estad.recipinvgauss,
                                    'pymc': None,
                                    'límites': (0, np.inf)
                                    },
                  'semicircular': {'scipy': estad.semicircular,
                                   'pymc': None,
                                   'límites': (-1, 1)
                                   },
                  't': {'scipy': estad.t,
                        'pymc': T,
                        'límites': (-np.inf, np.inf)
                        },
                  'triang': {'scipy': estad.triang,
                             'pymc': None,
                             'límites': (0, 1)  # El límite es (a, b)
                             },
                  'truncexpon': {'scipy': estad.truncexpon,
                                 'pymc': None,
                                 'límites': (0, 1)  # El límite es (0, b)
                                 },
                  'truncnorm': {'scipy': estad.truncnorm,
                                'pymc': TruncatedNormal,
                                'límites': (0, 1)  # El límite es (a, b)
                                },
                  'tukeylambda': {'scipy': estad.tukeylambda,
                                  'pymc': None,
                                  'límites': (-np.inf, np.inf)
                                  },
                  'uniform': {'scipy': estad.uniform,
                              'pymc': Uniform,
                              'límites': (0, 1)  # El límite es (a, b)
                              },
                  'vonmises': {'scipy': estad.vonmises,
                               'pymc': VonMises,
                               'límites': (-mat.pi, mat.pi)
                               },
                  'vonmises_line': {'scipy': estad.vonmises_line,
                                    'pymc': None,
                                    'límites': (-mat.pi, mat.pi)
                                    },
                  'wald': {'scipy': estad.wald,
                           'pymc': None,
                           'límites': (0, np.inf)
                           },
                  'weibull_min': {'scipy': estad.weibull_min,
                                  'pymc': None,
                                  'límites': (0, np.inf)
                                  },
                  'weibull_max': {'scipy': estad.weibull_max,
                                  'pymc': None,
                                  'límites': (0, np.inf)
                                  },
                  'wrapcauchy': {'scipy': estad.wrapcauchy,
                                 'pymc': None,
                                 'límites': (0, 2*mat.pi)
                                 }
                  },

         'disc': {'bernoulli': {'scipy': estad.bernoulli,
                                'pymc': Bernoulli,
                                'límites': (0, 1)
                                },
                  'binom': {'scipy': estad.binom,
                            'pymc': Binomial,
                            'límites': (0, 1)  # Límite es de (0, N)
                            },
                  'boltzmann': {'scipy': estad.boltzmann,
                                'pymc': None,
                                'límites': (0, 1)  # Límite es de (0, N-1)
                                },
                  'dlaplace': {'scipy': estad.dlaplace,
                               'pymc': None,
                               'límites': (-np.inf, np.inf)
                               },
                  'geom': {'scipy': estad.geom,
                           'pymc': Geometric,
                           'límites': (1, np.inf)
                           },
                  'hypergeom': {'scipy': estad.hypergeom,
                                'pymc': Hypergeometric,
                                'límites': (0, 1)  # El límite es (0, N)
                                },
                  'logser': {'scipy': estad.logser,
                             'pymc': None,
                             'límites': (1, np.inf)
                             },
                  'nbinom': {'scipy': estad.nbinom,
                             'pymc': NegativeBinomial,
                             'límites': (0, np.inf)
                             },
                  'planck': {'scipy': estad.alpha,
                             'pymc': None,
                             'límites': (0, np.inf)
                             },
                  'poisson': {'scipy': estad.poisson,
                              'pymc': Poisson,
                              'límites': (0, np.inf)
                              },
                  'randint': {'scipy': estad.randint,
                              'pymc': DiscreteUniform,
                              'límites': (0, 1)  # Límite es de (a, b)
                              },
                  'skellam': {'scipy': estad.skellam,
                              'pymc': None,
                              'límites': (-np.inf, np.inf)
                              },
                  'zipf': {'scipy': estad.alpha,
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
        for dic_dist in dists[categ_dist].values():
            if dic_dist['nombre'] == nombre:
                dist = dic_dist['scipy'](paráms)
                return dist

    raise ValueError('No se pudo decodar la distribución "%s".' % texto)


def ajustar_dist(datos, límites, cont, pymc=False, nombre=None):
    """
    Esta función, tomando las límites teoréticas de una distribución y una serie de datos proveniendo de dicha
      distribución, escoge la distribución de PyMC la más apropriada y ajusta sus parámetros. Al momento únicamente
      puede generar distribuciones continuas.

    :param cont:
    :param pymc:
    :param datos: Lista de parámetros

    :param límites: Las límites teoréticas de la distribucion (p. ej., (0, np.inf), (-np.inf, np.inf), etc.)

    :return: Distribución PyMC
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

    return mejor_ajuste
