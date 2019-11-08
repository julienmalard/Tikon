from math import pi

import scipy.stats as estad
# Un diccionario de las distribuciones y de sus objetos de SciPy correspondientes.
from tikon.utils import proc_líms

dists = {
    'Alpha': {'scipy': estad.alpha,
              'paráms': ['a', 'loc', 'scale'],
              'límites': (0, None)
              },
    'Anglit': {'scipy': estad.anglit,
               'paráms': ['loc', 'scale'],
               'límites': (-pi / 4, pi / 4)
               },
    'Arcsen': {'scipy': estad.arcsine,
               'paráms': ['loc', 'scale'],
               'límites': (0, 1)
               },
    'Beta': {'scipy': estad.beta,
             'paráms': ['a', 'b', 'loc', 'scale'],
             'límites': (0, 1)
             },
    'Bradford': {'scipy': estad.bradford,
                 'paráms': ['c', 'loc', 'scale'],
                 'límites': (0, 1)
                 },
    'Burr': {'scipy': estad.burr,
             'paráms': ['c', 'd', 'loc', 'scale'],
             'límites': (0, None)
             },
    'Cauchy': {'scipy': estad.cauchy,
               'paráms': ['loc', 'scale'],
               'límites': (None, None)
               },
    'Chi': {'scipy': estad.chi,
            'paráms': ['df', 'loc', 'scale'],
            'límites': (0, None)
            },
    'Chi2': {'scipy': estad.chi2,
             'paráms': ['df', 'loc', 'scale'],
             'límites': (0, None)
             },
    'DobleGamma': {'scipy': estad.dgamma,
                   'paráms': ['a', 'loc', 'scale'],
                   'límites': (None, None)
                   },
    'DobleWeibull': {'scipy': estad.dweibull,
                     'paráms': ['c', 'loc', 'scale'],
                     'límites': (None, None)
                     },
    'Exponencial': {'scipy': estad.expon,
                    'paráms': ['loc', 'scale'],
                    'límites': (0, None)
                    },
    'NormalExponencial': {'scipy': estad.exponnorm,
                          'paráms': ['K', 'loc', 'scale'],
                          'límites': (None, None)
                          },
    'F': {'scipy': estad.f,
          'paráms': ['dfn', 'dfd', 'loc', 'scale'],
          'límites': (0, None)
          },
    'BirnbaumSaunders': {'scipy': estad.fatiguelife,
                         'paráms': ['c', 'loc', 'scale'],
                         'límites': (0, None)
                         },
    'Fisk': {'scipy': estad.fisk,
             'paráms': ['c', 'loc', 'scale'],
             'límites': (0, None)
             },
    'CauchyDoblada': {'scipy': estad.foldcauchy,
                      'paráms': ['c', 'loc', 'scale'],
                      'límites': (0, None)
                      },
    'NormalDoblada': {'scipy': estad.foldnorm,
                      'paráms': ['c', 'loc', 'scale'],
                      'límites': (0, None)
                      },
    'LogísticaGeneral': {'scipy': estad.genlogistic,
                         'paráms': ['c', 'loc', 'scale'],
                         'límites': (None, None)
                         },
    'NormalGeneral': {'scipy': estad.gennorm,
                      'paráms': ['beta', 'loc', 'scale'],
                      'límites': (None, None)
                      },
    'ParetoGeneral': {'scipy': estad.genpareto,
                      'paráms': ['c', 'loc', 'scale'],
                      'límites': (0, None)
                      },
    'ExtremaGeneral': {'scipy': estad.genextreme,
                       'paráms': ['c', 'loc', 'scale'],
                       'límites': (None, None)
                       },
    'Gamma': {'scipy': estad.gamma,
              'paráms': ['a', 'loc', 'scale'],
              'límites': (0, None)
              },
    'GammaGeneral': {'scipy': estad.gengamma,
                     'paráms': ['a', 'c', 'loc', 'scale'],
                     'límites': (0, None)
                     },
    'Gilbrat': {'scipy': estad.gilbrat,
                'paráms': ['loc', 'scale'],
                'límites': (0, None)
                },
    'GumbelDerecho': {'scipy': estad.gumbel_r,
                      'paráms': ['loc', 'scale'],
                      'límites': (None, None)
                      },
    'GumbelIzquierda': {'scipy': estad.gumbel_l,
                        'paráms': ['loc', 'scale'],
                        'límites': (None, None)
                        },
    'MitadCauchy': {'scipy': estad.halfcauchy,
                    'paráms': ['loc', 'scale'],
                    'límites': (0, None)
                    },
    'MitadLogística': {'scipy': estad.halflogistic,
                       'paráms': ['loc', 'scale'],
                       'límites': (0, None)
                       },
    'MitadNormal': {'scipy': estad.halfnorm,
                    'paráms': ['loc', 'scale'],
                    'límites': (0, None)
                    },
    'HyperSecante': {'scipy': estad.hypsecant,
                     'paráms': ['loc', 'scale'],
                     'límites': (None, None)
                     },
    'GammaInversa': {'scipy': estad.invgamma,
                     'paráms': ['a', 'loc', 'scale'],
                     'límites': (0, None)
                     },
    'GaussInversa': {'scipy': estad.invgauss,
                     'paráms': ['mu', 'loc', 'scale'],
                     'límites': (0, None)
                     },
    'WeibullInversa': {'scipy': estad.invweibull,
                       'paráms': ['c', 'loc', 'scale'],
                       'límites': (0, None)
                       },
    'Laplace': {'scipy': estad.laplace,
                'paráms': ['loc', 'scale'],
                'límites': (None, None)
                },
    'Levy': {'scipy': estad.levy,
             'paráms': ['loc', 'scale'],
             'límites': (0, None)
             },
    'Logística': {'scipy': estad.logistic,
                  'paráms': ['loc', 'scale'],
                  'límites': (None, None)
                  },
    'LogGamma': {'scipy': estad.loggamma,
                 'paráms': ['c', 'loc', 'scale'],
                 'límites': (None, None)
                 },
    'LogLaplace': {'scipy': estad.loglaplace,
                   'paráms': ['c', 'loc', 'scale'],
                   'límites': (0, None)
                   },
    'LogNormal': {'scipy': estad.lognorm,
                  'paráms': ['s', 'loc', 'scale'],
                  'límites': (0, None)
                  },
    'Lomax': {'scipy': estad.lomax,
              'paráms': ['c', 'loc', 'scale'],
              'límites': (0, None)
              },
    'Maxwell': {'scipy': estad.maxwell,
                'paráms': ['loc', 'scale'],
                'límites': (0, None)
                },
    'Nakagami': {'scipy': estad.nakagami,
                 'paráms': ['nu', 'loc', 'scale'],
                 'límites': (0, None)
                 },
    'Chi2NoCentral': {'scipy': estad.ncx2,
                      'paráms': ['df', 'nc', 'loc', 'scale'],
                      'límites': (0, None)
                      },
    'Normal': {'scipy': estad.norm,
               'paráms': ['loc', 'scale'],
               'límites': (None, None)
               },
    'Pareto': {'scipy': estad.pareto,
               'paráms': ['b', 'loc', 'scale'],
               'límites': (1, None)
               },
    'Pearson3': {'scipy': estad.pearson3,
                 'paráms': ['skew', 'loc', 'scale'],
                 'límites': (None, None)
                 },
    'Potencial': {'scipy': estad.powerlaw,
                  'paráms': ['a', 'loc', 'scale'],
                  'límites': (0, 1)
                  },
    'Rayleigh': {'scipy': estad.rayleigh,
                 'paráms': ['loc', 'scale'],
                 'límites': (0, None)
                 },
    'Rice': {'scipy': estad.rice,
             'paráms': ['b', 'loc', 'scale'],
             'límites': (0, None)
             },
    'NormalSesgada': {'scipy': estad.skewnorm,
                      'paráms': ['a', 'loc', 'scale'],
                      'límites': (None, None)
                      },
    'T': {'scipy': estad.t,
          'paráms': ['df', 'loc', 'scale'],
          'límites': (None, None)
          },
    'Triang': {'scipy': estad.triang,
               'paráms': ['c', 'loc', 'scale'],
               'límites': (0, 1),  # El límite es ('a', 'b')
               'tipo': 'cont'
               },
    'TukeyLambda': {'scipy': estad.tukeylambda,
                    'paráms': ['lam', 'loc', 'scale'],
                    'límites': (None, None)
                    },
    'Uniforme': {'scipy': estad.uniform,
                 'paráms': ['loc', 'scale'],
                 'límites': (0, 1),
                 'tipo': 'cont'
                 },
    'Wald': {'scipy': estad.wald,
             'paráms': ['loc', 'scale'],
             'límites': (0, None)
             },
    'Weibull': {'scipy': estad.weibull_min,
                'paráms': ['c', 'loc', 'scale'],
                'límites': (0, None)
                },
    'WeibullMáximo': {'scipy': estad.weibull_max,
                      'paráms': ['c', 'loc', 'scale'],
                      'límites': (None, 0)
                      },
    'CauchyEnvuelto': {'scipy': estad.wrapcauchy,
                       'paráms': ['c', 'loc', 'scale'],
                       'límites': (0, 2 * pi)
                       }
}


def _valid_nombre(nombre):
    try:
        return next(nmbr for nmbr in dists if nmbr.lower() == nombre.lower())
    except StopIteration:
        raise ValueError(
            'No hay distribución llamada "{nm}". Debe ser una de:\n'
            '\t{ops}'.format(nm=nombre, ops=', '.join(dists))
        )


def _obt_dic_dist(nombre):
    nombre = _valid_nombre(nombre)
    return dists[nombre]


def clase_scipy(nombre):
    return _obt_dic_dist(nombre)['scipy']


def líms_dist(nombre):
    return proc_líms(_obt_dic_dist(nombre)['límites'])


def prms_dist(nombre):
    return _obt_dic_dist(nombre)['paráms']


def obt_scipy(nombre, paráms):
    cls_dist = clase_scipy(nombre)

    if isinstance(paráms, dict):
        return cls_dist(**paráms)
    else:
        return cls_dist(*paráms[0], **paráms[1])


def obt_prms_obj_scipy(dist_sp):
    return [dist_sp.args, dist_sp.kwds]


def obt_nombre(dist_sp):
    return next(nmb for nmb in dists if dists[nmb]['scipy'].name == dist_sp.dist.name)
