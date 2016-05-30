import warnings as avisar
import math as mat
import numpy as np
import scipy.stats as estad
from pymc import Beta, Cauchy, Chi2, Exponential, Exponweib, Gamma, HalfCauchy, HalfNormal, InverseGamma, Laplace, \
    Logistic, Lognormal, NoncentralT, Normal, Pareto, T, TruncatedNormal, Uniform, VonMises, Bernoulli, Binomial, \
    Geometric, Hypergeometric, NegativeBinomial, Poisson, DiscreteUniform


# Un diccionario de las distribuciones y de sus objetos de SciPy y de PyMC correspondientes.
dists = {'Alpha': {'scipy': estad.alpha,
                   'pymc': None,
                   'límites': (0, np.inf),
                   'tipo': 'cont'
                   },
         'Anglit': {'scipy': estad.anglit,
                    'pymc': None,
                    'límites': (-mat.pi/4, mat.pi/4),
                    'tipo': 'cont'
                    },
         'Arcsen': {'scipy': estad.arcsine,
                    'pymc': None,
                    'límites': (0, 1),
                    'tipo': 'cont'
                    },
         'Beta': {'scipy': estad.beta,
                  'pymc': Beta,
                  'límites': (0, 1),
                  'tipo': 'cont'
                  },
         'BetaPrima': {'scipy': estad.betaprime,
                       'pymc': None,
                       'límites': (0, np.inf),
                       'tipo': 'cont'
                       },
         'Bradford': {'scipy': estad.bradford,
                      'pymc': None,
                      'límites': (0, 1),
                      'tipo': 'cont'
                      },
         'Burr': {'scipy': estad.burr,
                  'pymc': None,
                  'límites': (0, np.inf),
                  'tipo': 'cont'
                  },
         'Cauchy': {'scipy': estad.cauchy,
                    'pymc': Cauchy,
                    'límites': (-np.inf, np.inf),
                    'tipo': 'cont'
                    },
         'Chi': {'scipy': estad.chi,
                 'pymc': None,
                 'límites': (0, np.inf),
                 'tipo': 'cont'
                 },
         'ChiCuadrado': {'scipy': estad.chi2,
                         'pymc': Chi2,
                         'límites': (0, np.inf),
                         'tipo': 'cont'
                         },
         'Cosine': {'scipy': estad.cosine,
                    'pymc': None,
                    'límites': (-mat.pi, mat.pi),
                    'tipo': 'cont'
                    },
         'DobleGamma': {'scipy': estad.dgamma,
                        'pymc': None,
                        'límites': (0, np.inf),
                        'tipo': 'cont'
                        },
         'DobleWeibull': {'scipy': estad.dweibull,
                          'pymc': None,
                          'límites': (0, np.inf),
                          'tipo': 'cont'
                          },
         'Erlang': {'scipy': estad.erlang,
                    'pymc': None,
                    'límites': (0, np.inf),
                    'tipo': 'cont'
                    },
         'Exponencial': {'scipy': estad.arcsine,
                         'pymc': Exponential,
                         'límites': (0, np.inf),
                         'tipo': 'cont'
                         },
         'NormalExponencial': {'scipy': estad.arcsine,
                               'pymc': None,
                               'límites': (-np.inf, np.inf),
                               'tipo': 'cont'
                               },
         'WeibullExponencial': {'scipy': estad.arcsine,
                                'pymc': Exponweib,
                                'límites': (0, np.inf),
                                'tipo': 'cont'
                                },
         'PotencialExponencial': {'scipy': estad.exponpow,
                                  'pymc': None,
                                  'límites': (0, np.inf),
                                  'tipo': 'cont'
                                  },
         'F': {'scipy': estad.f,
               'pymc': None,
               'límites': (0, np.inf),
               'tipo': 'cont'
               },
         'BirnbaumSaunders': {'scipy': estad.fatiguelife,
                              'pymc': None,
                              'límites': (0, np.inf),
                              'tipo': 'cont'
                              },
         'Fisk': {'scipy': estad.fisk,
                  'pymc': None,
                  'límites': (0, np.inf),
                  'tipo': 'cont'
                  },
         'CauchyDoblada': {'scipy': estad.foldcauchy,
                           'pymc': None,
                           'límites': (0, np.inf),
                           'tipo': 'cont'
                           },
         'NormalDoblada': {'scipy': estad.foldnorm,
                           'pymc': None,
                           'límites': (0, np.inf),
                           'tipo': 'cont'
                           },
         'FrechetDerecha': {'scipy': estad.frechet_r,
                            'pymc': None,
                            'límites': (0, np.inf),
                            'tipo': 'cont'
                            },
         # 'FrechetIzquierda': {'scipy': estad.frechet_l,
         #               'pymc': None,
         #               'límites': (-np.inf, 0)
         #               },
         'LogísticaGeneral': {'scipy': estad.genlogistic,
                              'pymc': None,
                              'límites': (0, np.inf),
                              'tipo': 'cont'
                              },
         'NormalGeneral': {'scipy': estad.gennorm,
                           'pymc': None,
                           'límites': (-np.inf, np.inf),
                           'tipo': 'cont'
                           },
         'ParetoGeneral': {'scipy': estad.genpareto,
                           'pymc': None,
                           'límites': (0, np.inf),
                           'tipo': 'cont'
                           },
         'ExponencialGeneral': {'scipy': estad.genexpon,
                                'pymc': None,
                                'límites': (0, np.inf),
                                'tipo': 'cont'
                                },
         'ExtremaGeneral': {'scipy': estad.genextreme,
                            'pymc': None,
                            'límites': (-np.inf, np.inf),
                            'tipo': 'cont'
                            },
         'HyperGauss': {'scipy': estad.gausshyper,
                        'pymc': None,
                        'límites': (0, 1),
                        'tipo': 'cont'
                        },
         'Gamma': {'scipy': estad.gamma,
                   'pymc': Gamma,
                   'límites': (0, np.inf),
                   'tipo': 'cont'
                   },
         'GammaGeneral': {'scipy': estad.gengamma,
                          'pymc': None,
                          'límites': (0, np.inf),
                          'tipo': 'cont'
                          },
         'MitadLogísticaGeneral': {'scipy': estad.genhalflogistic,
                                   'pymc': None,
                                   'límites': (0, 1),  # El límite es (0, 1/c)
                                   'tipo': 'cont'
                                   },
         'Gilbrat': {'scipy': estad.gilbrat,
                     'pymc': None,
                     'límites': (0, np.inf),
                     'tipo': 'cont'
                     },
         'Gompertz': {'scipy': estad.gompertz,
                      'pymc': None,
                      'límites': (0, np.inf),
                      'tipo': 'cont'
                      },
         'GumbelDerecho': {'scipy': estad.gumbel_r,
                           'pymc': None,
                           'límites': (-np.inf, np.inf),
                           'tipo': 'cont'
                           },
         'GumbelIzquierda': {'scipy': estad.gumbel_l,
                             'pymc': None,
                             'límites': (-np.inf, np.inf),
                             'tipo': 'cont'
                             },
         'MitadCauchy': {'scipy': estad.halfcauchy,
                         'pymc': HalfCauchy,
                         'límites': (0, np.inf),
                         'tipo': 'cont'
                         },
         'MitadLogística': {'scipy': estad.halflogistic,
                            'pymc': None,
                            'límites': (0, np.inf),
                            'tipo': 'cont'
                            },
         'MitadNormal': {'scipy': estad.halfnorm,
                         'pymc': HalfNormal,
                         'límites': (0, np.inf),
                         'tipo': 'cont'
                         },
         'MitadNormalGeneral': {'scipy': estad.halfgennorm,
                                'pymc': None,
                                'límites': (0, np.inf),
                                'tipo': 'cont'
                                },
         'HyperSecante': {'scipy': estad.hypsecant,
                          'pymc': None,
                          'límites': (-np.inf, np.inf),
                          'tipo': 'cont'
                          },
         'GammaInversa': {'scipy': estad.invgamma,
                          'pymc': InverseGamma,
                          'límites': (0, np.inf),
                          'tipo': 'cont'
                          },
         'GaussInversa': {'scipy': estad.invgauss,
                          'pymc': None,
                          'límites': (0, np.inf),
                          'tipo': 'cont'
                          },
         'WeibullInversa': {'scipy': estad.invweibull,
                            'pymc': None,
                            'límites': (0, np.inf),
                            'tipo': 'cont'
                            },
         'JohnsonSB': {'scipy': estad.johnsonsb,
                       'pymc': None,
                       'límites': (0, 1),
                       'tipo': 'cont'
                       },
         'JohnsonSU': {'scipy': estad.johnsonsu,
                       'pymc': None,
                       'límites': (0, np.inf),
                       'tipo': 'cont'
                       },
         'KSUno': {'scipy': estad.ksone,
                   'pymc': None,
                   'límites': (0, np.inf),
                   'tipo': 'cont'
                   },
         'KSDosNLargo': {'scipy': estad.kstwobign,
                         'pymc': None,
                         'límites': (0, np.inf),
                         'tipo': 'cont'
                         },
         'Laplace': {'scipy': estad.laplace,
                     'pymc': Laplace,
                     'límites': (-np.inf, np.inf),
                     'tipo': 'cont'
                     },
         'Levy': {'scipy': estad.levy,
                  'pymc': None,
                  'límites': (0, np.inf),
                  'tipo': 'cont'
                  },
         # 'LevyIzquierda': {'scipy': estad.levy_l,
         #            'pymc': None,
         #            'límites': (-np.inf, 0)
         #            },
         'LevyEstable': {'scipy': estad.levy_stable,
                         'pymc': None,
                         'límites': (0, np.inf),
                         'tipo': 'cont'
                         },
         'Logística': {'scipy': estad.logistic,
                       'pymc': Logistic,
                       'límites': (-np.inf, np.inf),
                       'tipo': 'cont'
                       },
         'LogGamma': {'scipy': estad.loggamma,
                      'pymc': None,
                      'límites': (0, np.inf),
                      'tipo': 'cont'
                      },
         'LogLaplace': {'scipy': estad.loglaplace,
                        'pymc': None,
                        'límites': (0, np.inf),
                        'tipo': 'cont'
                        },
         'LogNormal': {'scipy': estad.lognorm,
                       'pymc': Lognormal,
                       'límites': (0, np.inf),
                       'tipo': 'cont'
                       },
         'Lomax': {'scipy': estad.lomax,
                   'pymc': None,
                   'límites': (0, np.inf),
                   'tipo': 'cont'
                   },
         'Maxwell': {'scipy': estad.maxwell,
                     'pymc': None,
                     'límites': (0, np.inf),
                     'tipo': 'cont'
                     },
         'Mielke': {'scipy': estad.mielke,
                    'pymc': None,
                    'límites': (0, np.inf),
                    'tipo': 'cont'
                    },
         'Nakagami': {'scipy': estad.nakagami,
                      'pymc': None,
                      'límites': (0, np.inf),
                      'tipo': 'cont'
                      },
         'Chi2NoCentral': {'scipy': estad.ncx2,
                           'pymc': None,
                           'límites': (0, np.inf),
                           'tipo': 'cont'
                           },
         'FNoCentral': {'scipy': estad.ncf,
                        'pymc': None,
                        'límites': (0, np.inf),
                        'tipo': 'cont'
                        },
         'TNoCentral': {'scipy': estad.nct,
                        'pymc': NoncentralT,
                        'límites': (-np.inf, np.inf),
                        'tipo': 'cont'
                        },
         'Normal': {'scipy': estad.norm,
                    'pymc': Normal,
                    'límites': (-np.inf, np.inf),
                    'tipo': 'cont'
                    },
         'Pareto': {'scipy': estad.pareto,
                    'pymc': Pareto,
                    'límites': (1, np.inf),
                    'tipo': 'cont'
                    },
         'Pearson3': {'scipy': estad.pearson3,
                      'pymc': None,
                      'límites': (-np.inf, np.inf),
                      'tipo': 'cont'
                      },
         'Potencial': {'scipy': estad.powerlaw,
                       'pymc': None,
                       'límites': (0, 1),
                       'tipo': 'cont'
                       },
         'PotencialLogNormal': {'scipy': estad.powerlognorm,
                                'pymc': None,
                                'límites': (0, np.inf),
                                'tipo': 'cont'
                                },
         'PotencialNormal': {'scipy': estad.powernorm,
                             'pymc': None,
                             'límites': (0, np.inf),
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
                      'límites': (0, np.inf),
                      'tipo': 'cont'
                      },
         'Rice': {'scipy': estad.rice,
                  'pymc': None,
                  'límites': (0, np.inf),
                  'tipo': 'cont'
                  },
         'GaussInversaRecíproco': {'scipy': estad.recipinvgauss,
                                   'pymc': None,
                                   'límites': (0, np.inf),
                                   'tipo': 'cont'
                                   },
         'Semicircular': {'scipy': estad.semicircular,
                          'pymc': None,
                          'límites': (-1, 1),
                          'tipo': 'cont'
                          },
         'T': {'scipy': estad.t,
               'pymc': T,
               'límites': (-np.inf, np.inf),
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
                         'límites': (0, 1),  # El límite es (a, b)
                         'tipo': 'cont'
                         },
         'TukeyLambda': {'scipy': estad.tukeylambda,
                         'pymc': None,
                         'límites': (-np.inf, np.inf),
                         'tipo': 'cont'
                         },
         'Uniforme': {'scipy': estad.uniform,
                      'pymc': Uniform,
                      'límites': (0, 1),  # El límite es (a, b)
                      'tipo': 'cont'
                      },
         'VonMises': {'scipy': estad.vonmises,
                      'pymc': VonMises,
                      'límites': (-mat.pi, mat.pi),
                      'tipo': 'cont'
                      },
         'VonMisesLín': {'scipy': estad.vonmises_line,
                         'pymc': None,
                         'límites': (-mat.pi, mat.pi),
                         'tipo': 'cont'
                         },
         'Wald': {'scipy': estad.wald,
                  'pymc': None,
                  'límites': (0, np.inf),
                  'tipo': 'cont'
                  },
         'WeibullMínimo': {'scipy': estad.weibull_min,
                           'pymc': None,
                           'límites': (0, np.inf),
                           'tipo': 'cont'
                           },
         'WeibullMáximo': {'scipy': estad.weibull_max,
                           'pymc': None,
                           'límites': (0, np.inf),
                           'tipo': 'cont'
                           },
         'CauchyEnvuelto': {'scipy': estad.wrapcauchy,
                            'pymc': None,
                            'límites': (0, 2*mat.pi),
                            'tipo': 'cont'
                            },

         # Distribuciones discretas

         'Bernoulli': {'scipy': estad.bernoulli,
                       'pymc': Bernoulli,
                       'límites': (0, 1),
                       'tipo': 'discr'
                       },
         'Binomial': {'scipy': estad.binom,
                      'pymc': Binomial,
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
                             'límites': (-np.inf, np.inf),
                             'tipo': 'discr'
                             },
         'Geométrica': {'scipy': estad.geom,
                        'pymc': Geometric,
                        'límites': (1, np.inf),
                        'tipo': 'discr'
                        },
         'Hypergeométrica': {'scipy': estad.hypergeom,
                             'pymc': Hypergeometric,
                             'límites': (0, 1),  # El límite es (0, N)
                             'tipo': 'discr'
                             },
         'Logarítmico': {'scipy': estad.logser,
                         'pymc': None,
                         'límites': (1, np.inf),
                         'tipo': 'discr'
                         },
         'BinomialNegativo': {'scipy': estad.nbinom,
                              'pymc': NegativeBinomial,
                              'límites': (0, np.inf),
                              'tipo': 'discr'
                              },
         'Planck': {'scipy': estad.planck,
                    'pymc': None,
                    'límites': (0, np.inf),
                    'tipo': 'discr'
                    },
         'Poisson': {'scipy': estad.poisson,
                     'pymc': Poisson,
                     'límites': (0, np.inf),
                     'tipo': 'discr'
                     },
         'EnteroAleatorio': {'scipy': estad.randint,
                             'pymc': DiscreteUniform,
                             'límites': (0, 1),  # Límite es de (a, b)
                             'tipo': 'discr'
                             },
         'Skellam': {'scipy': estad.skellam,
                     'pymc': None,
                     'límites': (-np.inf, np.inf),
                     'tipo': 'discr'
                     },
         'Zipf': {'scipy': estad.zipf,
                  'pymc': None,
                  'límites': (1, np.inf),
                  'tipo': 'discr'
                  }
         }


def texto_a_distscipy(texto):
    """
    Esta función convierte texto a su distribución SciPy correspondiente.

    :param texto: La distribución a convertir.
    :type texto: str
    """

    # Dividir el nombre de la distribución de sus parámetros.
    nombre, paráms = texto.split('~')

    # Si el nombre de la distribución está en la lista arriba...
    if nombre in dists:
        # Devolver la distribución SciPy appropiada
        return dists[nombre]['scipy'](paráms)

    # Si no encontramos el nombre de la distribución, hay un error.
    raise ValueError('No se pudo decodar la distribución "%s".' % texto)


def ajustar_dist(datos, límites, cont, pymc=False, nombre=None):
    """
    Esta función, tomando las límites teoréticas de una distribución y una serie de datos proveniendo de dicha
      distribución, escoge la distribución de Scipy o PyMC la más apropriada y ajusta sus parámetros.

    :param datos: Un vector de valores del parámetro
    :type datos: np.ndarray

    :param nombre: El nombre del variable, si vamos a generar un variable de PyMC
    :type nombre: str

    :param cont: Determina si la distribución es contínua (en vez de discreta)
    :type cont: bool

    :param pymc: Determina si queremos una distribución de tipo PyMC (en vez de SciPy)
    :type pymc: bool

    :param límites: Las límites teoréticas de la distribucion (p. ej., (0, np.inf), (-np.inf, np.inf), etc.)
    :type límites: tuple

    :return: Distribución PyMC y su ajuste (p)
    :rtype: dict[pymc.Stochastic, float]

    """

    # Separar el mínimo y el máximo de la distribución
    mín_parám, máx_parám = límites

    # Un diccionario para guardar el mejor ajuste
    mejor_ajuste = dict(dist=None, p=0)

    # Sacar las distribuciones del buen tipo (contínuas o discretas)
    if cont:
        categ_dist = 'cont'
    else:
        categ_dist = 'discr'

    dists_potenciales = [x for x in dists if dists[x]['tipo'] == categ_dist]

    # Si queremos generar una distribución PyMC, guardar únicamente las distribuciones con objeto de PyMC disponible
    if pymc is True:
        dists_potenciales = [x for x in dists_potenciales if dists[x]['pymc'] is not None]

    # Para cada distribución potencial para representar a nuestros datos...
    for nombre_dist in dists_potenciales:

        # El diccionario de la distribución
        dic_dist = dists[nombre_dist]

        # El máximo y el mínimo de la distribución
        mín_dist, máx_dist = dic_dist['límites']

        # Verificar que los límites del parámetro y de la distribución son compatibles
        lím_igual = (((mín_dist == mín_parám == -np.inf) or
                     (not np.isinf(mín_dist) and not np.isinf(mín_parám))) and
                     ((máx_dist == máx_parám == np.inf) or
                     (not np.isinf(máx_dist) and not np.isinf(máx_parám))))

        # Si son compatibles...
        if lím_igual:

            # Restringimos las posibilidades para las distribuciones a ajustar, si necesario
            if np.isinf(mín_parám):

                if np.isinf(máx_parám):
                    # Para el caso de un parámetro sín límites teoréticos (-inf, inf), no hay restricciones en la
                    # distribución.
                    restric = {}

                else:
                    # TIKON (por culpa de SciPy), no puede tomar distribuciones en (-inf, R].
                    raise ValueError('Tikon no puede tomar distribuciones en el intervalo (-inf, R]. Hay que '
                                     'cambiar tus ecuaciones para usar un variable en el intervalo [R, inf). '
                                     'Disculpas. Pero de verdad es la culpa del módulo SciPy.')
            else:

                if np.isinf(máx_parám):
                    # En el caso [R, inf), limitamos el valor inferior de la distribución al límite inferior del
                    # parámtro
                    restric = {'floc': mín_parám}

                else:
                    # En el caso [R, R], limitamos los valores inferiores y superiores de la distribución.
                    restric = {'floc': mín_parám, 'fscale': máx_parám - mín_parám}

            # Ajustar los parámetros de la distribución SciPy para caber con los datos.
            args = dic_dist['scipy'].fit(datos, **restric)

            # Medir el ajuste de la distribución
            p = estad.kstest(datos, nombre_dist, args=args)[1]

            # Si el ajuste es mejor que el mejor ajuste anterior...
            if p > mejor_ajuste['p']:

                # Guardarlo
                mejor_ajuste['p'] = p

                # Guardar también el objeto de la distribución, o de PyMC, o de SciPy, según lo que queremos
                if pymc:
                    mejor_ajuste['dist'] = dic_dist['pymc'](nombre, *args)
                else:
                    mejor_ajuste['dist'] = dic_dist['scipy'](*args)

    # Si no logramos un buen aujste, avisar al usuario.
    if mejor_ajuste['p'] <= 0.10:
        avisar.warn('El ajuste de la mejor distribución quedó muy mala (p = %f).' % round(mejor_ajuste['p'], 4))

    # Devolver la distribución con el mejor ajuste, tanto como el valor de su ajuste.
    return mejor_ajuste['dist'], mejor_ajuste['p']
