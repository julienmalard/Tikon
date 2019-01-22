from math import pi

import scipy.stats as estad

# Un diccionario de las distribuciones y de sus objetos de SciPy correspondientes.
_dists = {
    'Alpha': {'scipy': estad.alpha,
              'paráms': ['a', 'ubic', 'escl'],
              'límites': (0, None)
              },
    'Anglit': {'scipy': estad.anglit,
               'paráms': ['ubic', 'escl'],
               'límites': (-pi / 4, pi / 4)
               },
    'Arcsen': {'scipy': estad.arcsine,
               'paráms': ['ubic', 'escl'],
               'límites': (0, 1)
               },
    'Beta': {'scipy': estad.beta,
             'paráms': ['a', 'b', 'ubic', 'escl'],
             'límites': (0, 1)
             },
    'BetaPrima': {'scipy': estad.betaprime,
                  'paráms': ['a', 'b', 'ubic', 'escl'],
                  'límites': (0, None)
                  },
    'Bradford': {'scipy': estad.bradford,
                 'paráms': ['c', 'ubic', 'escl'],
                 'límites': (0, 1)
                 },
    'Burr': {'scipy': estad.burr,
             'paráms': ['c', 'd', 'ubic', 'escl'],
             'límites': (0, None)
             },
    'Cauchy': {'scipy': estad.cauchy,
               'paráms': ['ubic', 'escl'],
               'límites': (None, None)
               },
    'Chi': {'scipy': estad.chi,
            'paráms': ['df', 'ubic', 'escl'],
            'límites': (0, None)
            },
    'Chi2': {'scipy': estad.chi2,
             'paráms': ['df', 'ubic', 'escl'],
             'límites': (0, None)
             },
    'Cosine': {'scipy': estad.cosine,
               'paráms': ['ubic', 'escl'],
               'límites': (-pi, pi)
               },
    'DobleGamma': {'scipy': estad.dgamma,
                   'paráms': ['a', 'ubic', 'escl'],
                   'límites': (0, None)
                   },
    'DobleWeibull': {'scipy': estad.dweibull,
                     'paráms': ['c', 'ubic', 'escl'],
                     'límites': (0, None)
                     },
    'Exponencial': {'scipy': estad.expon,
                    'paráms': ['ubic', 'escl'],
                    'límites': (0, None)
                    },
    'NormalExponencial': {'scipy': estad.exponnorm,
                          'paráms': ['K', 'ubic', 'escl'],
                          'límites': (None, None)
                          },
    'WeibullExponencial': {'scipy': estad.exponweib,
                           'paráms': ['a', 'c', 'ubic', 'escl'],
                           'límites': (0, None)
                           },
    'PotencialExponencial': {'scipy': estad.exponpow,
                             'paráms': ['b', 'ubic', 'escl'],
                             'límites': (0, None)
                             },
    'F': {'scipy': estad.f,
          'paráms': ['dfn', 'dfd', 'ubic', 'escl'],
          'límites': (0, None)
          },

    'BirnbaumSaunders': {'scipy': estad.fatiguelife,
                         'paráms': ['c', 'ubic', 'escl'],
                         'límites': (0, None)
                         },
    'Fisk': {'scipy': estad.fisk,
             'paráms': ['c', 'ubic', 'escl'],
             'límites': (0, None)
             },
    'CauchyDoblada': {'scipy': estad.foldcauchy,
                      'paráms': ['c', 'ubic', 'escl'],
                      'límites': (0, None)
                      },
    'NormalDoblada': {'scipy': estad.foldnorm,
                      'paráms': ['c', 'ubic', 'escl'],
                      'límites': (0, None)
                      },
    'FrechetDerecha': {'scipy': estad.frechet_r,
                       'paráms': ['c', 'ubic', 'escl'],
                       'límites': (0, None)
                       },
    'LogísticaGeneral': {'scipy': estad.genlogistic,
                         'paráms': ['c', 'ubic', 'escl'],
                         'límites': (0, None)
                         },
    'NormalGeneral': {'scipy': estad.gennorm,
                      'paráms': ['beta', 'ubic', 'escl'],
                      'límites': (None, None)
                      },
    'ParetoGeneral': {'scipy': estad.genpareto,
                      'paráms': ['c', 'ubic', 'escl'],
                      'límites': (0, None)
                      },
    'ExponencialGeneral': {'scipy': estad.genexpon,
                           'paráms': ['a', 'b', 'c', 'ubic', 'escl'],
                           'límites': (0, None)
                           },
    'ExtremaGeneral': {'scipy': estad.genextreme,
                       'paráms': ['c', 'ubic', 'escl'],
                       'límites': (None, None)
                       },
    'HyperGauss': {'scipy': estad.gausshyper,
                   'paráms': ['a', 'b', 'c', 'z', 'ubic', 'escl'],
                   'límites': (0, 1)
                   },
    'Gamma': {'scipy': estad.gamma,
              'paráms': ['a', 'ubic', 'escl'],
              'límites': (0, None)
              },
    'GammaGeneral': {'scipy': estad.gengamma,
                     'paráms': ['a', 'c', 'ubic', 'escl'],
                     'límites': (0, None)
                     },
    # 'MitadLogísticaGeneral': {'scipy': estad.genhalflogistic,
    #            'paráms': [],
    #                           'límites': (0, 1),  # El límite es (0, 1/'c')
    #                           'tipo': 'cont'
    #                           },
    'Gilbrat': {'scipy': estad.gilbrat,
                'paráms': ['ubic', 'escl'],
                'límites': (0, None)
                },
    'Gompertz': {'scipy': estad.gompertz,
                 'paráms': ['c', 'ubic', 'escl'],
                 'límites': (0, None)
                 },
    'GumbelDerecho': {'scipy': estad.gumbel_r,
                      'paráms': ['ubic', 'escl'],
                      'límites': (None, None)
                      },
    'GumbelIzquierda': {'scipy': estad.gumbel_l,
                        'paráms': ['ubic', 'escl'],
                        'límites': (None, None)
                        },
    'MitadCauchy': {'scipy': estad.halfcauchy,
                    'paráms': ['ubic', 'escl'],
                    'límites': (0, None)
                    },
    'MitadLogística': {'scipy': estad.halflogistic,
                       'paráms': ['ubic', 'escl'],
                       'límites': (0, None)
                       },
    'MitadNormal': {'scipy': estad.halfnorm,
                    'paráms': ['ubic', 'escl'],
                    'límites': (0, None)
                    },
    'MitadNormalGeneral': {'scipy': estad.halfgennorm,
                           'paráms': ['beta', 'ubic', 'escl'],
                           'límites': (0, None)
                           },
    'HyperSecante': {'scipy': estad.hypsecant,
                     'paráms': ['ubic', 'escl'],
                     'límites': (None, None)
                     },
    'GammaInversa': {'scipy': estad.invgamma,
                     'paráms': ['a', 'ubic', 'escl'],
                     'límites': (0, None)
                     },
    'GaussInversa': {'scipy': estad.invgauss,
                     'paráms': ['mu', 'ubic', 'escl'],
                     'límites': (0, None)
                     },
    'WeibullInversa': {'scipy': estad.invweibull,
                       'paráms': ['c', 'ubic', 'escl'],
                       'límites': (0, None)
                       },
    'JohnsonSB': {'scipy': estad.johnsonsb,
                  'paráms': ['a', 'b', 'ubic', 'escl'],
                  'límites': (0, 1)
                  },
    'JohnsonSU': {'scipy': estad.johnsonsu,
                  'paráms': ['a', 'b', 'ubic', 'escl'],
                  'límites': (0, None)
                  },
    'KSUno': {'scipy': estad.ksone,
              'paráms': ['n', 'ubic', 'escl'],
              'límites': (0, None)
              },
    'KSDosNLargo': {'scipy': estad.kstwobign,
                    'paráms': ['ubic', 'escl'],
                    'límites': (0, None)
                    },
    'Laplace': {'scipy': estad.laplace,
                'paráms': ['ubic', 'escl'],
                'límites': (None, None)
                },
    'Levy': {'scipy': estad.levy,
             'paráms': ['ubic', 'escl'],
             'límites': (0, None)
             },
    'Logística': {'scipy': estad.logistic,
                  'paráms': ['ubic', 'escl'],
                  'límites': (None, None)
                  },
    'LogGamma': {'scipy': estad.loggamma,
                 'paráms': ['c', 'ubic', 'escl'],
                 'límites': (0, None)
                 },
    'LogLaplace': {'scipy': estad.loglaplace,
                   'paráms': ['c', 'ubic', 'escl'],
                   'límites': (0, None)
                   },
    'LogNormal': {'scipy': estad.lognorm,
                  'paráms': ['s', 'ubic', 'escl'],
                  'límites': (0, None)
                  },
    'Lomax': {'scipy': estad.lomax,
              'paráms': ['c', 'ubic', 'escl'],
              'límites': (0, None)
              },
    'Maxwell': {'scipy': estad.maxwell,
                'paráms': ['ubic', 'escl'],
                'límites': (0, None)
                },
    'Mielke': {'scipy': estad.mielke,
               'paráms': ['k', 's', 'ubic', 'escl'],
               'límites': (0, None)
               },
    'Nakagami': {'scipy': estad.nakagami,
                 'paráms': ['nu', 'ubic', 'escl'],
                 'límites': (0, None)
                 },
    'Chi2NoCentral': {'scipy': estad.ncx2,
                      'paráms': ['df', 'nc', 'ubic', 'escl'],
                      'límites': (0, None)
                      },
    'FNoCentral': {'scipy': estad.ncf,
                   'paráms': ['dfn', 'dfd', 'nc', 'ubic', 'escl'],
                   'límites': (0, None)
                   },
    'TNoCentral': {'scipy': estad.nct,
                   'paráms': ['df', 'nc', 'ubic', 'escl'],
                   'límites': (None, None)
                   },
    'Normal': {'scipy': estad.norm,
               'paráms': ['ubic', 'escl'],
               'límites': (None, None)
               },
    'Pareto': {'scipy': estad.pareto,
               'paráms': ['b', 'ubic', 'escl'],
               'límites': (1, None)
               },
    'Pearson3': {'scipy': estad.pearson3,
                 'paráms': ['skew', 'ubic', 'escl'],
                 'límites': (None, None)
                 },
    'Potencial': {'scipy': estad.powerlaw,
                  'paráms': ['a', 'ubic', 'escl'],
                  'límites': (0, 1)
                  },
    'PotencialLogNormal': {'scipy': estad.powerlognorm,
                           'paráms': ['c', 's', 'ubic', 'escl'],
                           'límites': (0, None)
                           },
    'PotencialNormal': {'scipy': estad.powernorm,
                        'paráms': ['c', 'ubic', 'escl'],
                        'límites': (0, None)
                        },
    'R': {'scipy': estad.rdist,
          'paráms': ['c', 'ubic', 'escl'],
          'límites': (-1, 1)
          },
    'Recíproco': {'scipy': estad.reciprocal,
                  'paráms': ['a', 'b', 'ubic', 'escl'],
                  'límites': (0, 1),  # El límite es ('a', 'b')
                  'tipo': 'cont'
                  },
    'Rayleigh': {'scipy': estad.rayleigh,
                 'paráms': ['ubic', 'escl'],
                 'límites': (0, None)
                 },
    'Rice': {'scipy': estad.rice,
             'paráms': ['b', 'ubic', 'escl'],
             'límites': (0, None)
             },
    'GaussInversaRecíproco': {'scipy': estad.recipinvgauss,
                              'paráms': ['mu', 'ubic', 'escl'],
                              'límites': (0, None)
                              },
    'Semicircular': {'scipy': estad.semicircular,
                     'paráms': ['ubic', 'escl'],
                     'límites': (-1, 1)
                     },

    'NormalSesgada': {'scipy': estad.skewnorm,
                      'paráms': ['a', 'ubic', 'escl'],
                      'límites': (None, None)
                      },

    'T': {'scipy': estad.t,
          'paráms': ['df', 'ubic', 'escl'],
          'límites': (None, None)
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
                    'límites': (0, 1)
                    },

    'TukeyLambda': {'scipy': estad.tukeylambda,
                    'paráms': ['lam', 'ubic', 'escl'],
                    'límites': (None, None)
                    },
    'Uniforme': {'scipy': estad.uniform,
                 'paráms': ['ubic', 'escl'],
                 'límites': (0, 1),  # El límite es ('ubic', 'ubic+escl')
                 'tipo': 'cont'
                 },

    'VonMises': {'scipy': estad.vonmises,
                 'paráms': ['kappa', 'ubic', 'escl'],
                 'límites': (-pi, pi)
                 },
    'Wald': {'scipy': estad.wald,
             'paráms': ['ubic', 'escl'],
             'límites': (0, None)
             },
    'Weibull': {'scipy': estad.weibull_min,
                'paráms': ['c', 'ubic', 'escl'],
                'límites': (0, None)
                },
    'WeibullMáximo': {'scipy': estad.weibull_max,
                      'paráms': ['c', 'ubic', 'escl'],
                      'límites': (0, None)
                      },
    'CauchyEnvuelto': {'scipy': estad.wrapcauchy,
                       'paráms': ['c', 'ubic', 'escl'],
                       'límites': (0, 2 * pi)
                       }
}


def valid_nombre(nombre):
    try:
        return next(nmbr for nmbr in _dists if nmbr.lower() == nombre.lower())
    except StopIteration:
        raise ValueError(
            'No hay distribución llamada "{nm}". Debe ser una de:\n'
            '\t{ops}'.format(nm=nombre, ops=', '.join(_dists))
        )


def obt_scipy(nombre, paráms):
    nombre = valid_nombre(nombre)
    d_dist = _dists[nombre]

    for arg, arg_sp in {'ubic': 'loc', 'escl': 'scale'}.items():
        try:
            paráms[arg_sp] = paráms.pop(arg)
        except KeyError:
            pass

    return d_dist['scipy'](**paráms)


def líms_dist(nombre):
    nombre = valid_nombre(nombre)
    return _dists[nombre]


def obt_nombre(dist_sp):
    return next(nmb for nmb in _dists if isinstance(dist_sp, _dists[nmb]['scipy']))
