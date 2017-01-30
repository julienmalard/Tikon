import numpy as np

import tikon.Matemáticas.Incert as Incert

# Aquí ponemos la información de los parámetros para todas las ecuaciones posibles. Cada parámetro necesita dos
# pedazos de inforamción: 1) sus límites y 2) si interactua con la estructura del modelo. Por ejemplo, si un
# parámetro de un ecuación de depredación se debe repetir por cada presa del organismo (digamos el número de presa
# comida por el depredador), tendrá que tener el valor 'presa' para su interacción para que TIKON sepa que este variable
# se tiene que repetir para cada presa presente.


ecs_orgs = {
    'Crecimiento': {'Modif': {'Nada': {},
                              'Ninguna': {'r': {'límites': (0, np.inf),
                                                'inter': None}},
                              'Log Normal Temperatura': {'t': {'límites': (0, np.inf),
                                                               'inter': None},
                                                         'p': {'límites': (0, np.inf),
                                                               'inter': None}}
                              },
                    'Ecuación': {'Exponencial': {},  # El exponencial no tiene parámetros a parte de r
                                 'Logístico': {'K': {'límites': (0, np.inf),
                                                     'inter': None}},
                                 'Logístico Presa': {'K': {'límites': (0, np.inf),
                                                           'inter': ['presa']}},
                                 'Logístico Depredación': {'K': {'límites': (0, np.inf),
                                                                 'inter': ['presa']}},
                                 'Externo Cultivo': {}
                                 }
                    },

    'Depredación': {'Ecuación': {'Nada': {},

                                 'Tipo I_Dependiente presa': {'a': {'límites': (0, 1),
                                                                    'inter': ['presa', 'huésped']}
                                                              },

                                 'Tipo II_Dependiente presa': {'a': {'límites': (0, 1),
                                                                     'inter': ['presa', 'huésped']},
                                                               'b': {'límites': (0, np.inf),
                                                                     'inter': ['presa', 'huésped']}
                                                               },

                                 'Tipo III_Dependiente presa': {'a': {'límites': (0, 1),
                                                                      'inter': ['presa', 'huésped']},
                                                                'b': {'límites': (0, np.inf),
                                                                      'inter': ['presa', 'huésped']}
                                                                },

                                 'Tipo I_Dependiente ratio': {'a': {'límites': (0, 1),
                                                                    'inter': ['presa', 'huésped']}
                                                              },

                                 'Tipo II_Dependiente ratio': {'a': {'límites': (0, 1),
                                                                     'inter': ['presa', 'huésped']},
                                                               'b': {'límites': (0, np.inf),
                                                                     'inter': ['presa', 'huésped']}
                                                               },

                                 'Tipo III_Dependiente ratio': {'a': {'límites': (0, 1),
                                                                      'inter': ['presa', 'huésped']},
                                                                'b': {'límites': (0, np.inf),
                                                                      'inter': ['presa', 'huésped']}
                                                                },

                                 'Beddington-DeAngelis': {'a': {'límites': (0, 1),
                                                                'inter': ['presa', 'huésped']},
                                                          'b': {'límites': (0, np.inf),
                                                                'inter': ['presa', 'huésped']},
                                                          'c': {'límites': (0, np.inf),
                                                                'inter': ['presa', 'huésped']}
                                                          },

                                 'Tipo I_Hassell-Varley': {'a': {'límites': (0, np.inf),
                                                                 'inter': ['presa', 'huésped']},
                                                           'm': {'límites': (0, np.inf),
                                                                 'inter': ['presa', 'huésped']}
                                                           },

                                 'Tipo II_Hassell-Varley': {'a': {'límites': (0, np.inf),
                                                                  'inter': ['presa', 'huésped']},
                                                            'b': {'límites': (0, np.inf),
                                                                  'inter': ['presa', 'huésped']},
                                                            'm': {'límites': (0, np.inf),
                                                                  'inter': ['presa', 'huésped']}
                                                            },

                                 'Tipo III_Hassell-Varley': {'a': {'límites': (0, np.inf),
                                                                   'inter': ['presa', 'huésped']},
                                                             'b': {'límites': (0, np.inf),
                                                                   'inter': ['presa', 'huésped']},
                                                             'm': {'límites': (0, np.inf),
                                                                   'inter': ['presa', 'huésped']}
                                                             },

                                 'Kovai': {'a': {'límites': (0, np.inf),
                                                 'inter': ['presa', 'huésped']},
                                           'b': {'límites': (0, np.inf),
                                                 'inter': ['presa', 'huésped']},
                                           }
                                 },
                    },

    'Muertes': {'Ecuación': {'Nada': {},

                             'Constante': {'q': {'límites': (0, 1),
                                                 'inter': None}
                                           },

                             'Log Normal Temperatura': {'t': {'límites': (-np.inf, np.inf),
                                                              'inter': None},
                                                        'p': {'límites': (0, np.inf),
                                                              'inter': None}
                                                        },

                             'Asimptótico Humedad': {'a': {'límites': (0, np.inf),
                                                           'inter': None},
                                                     'b': {'límites': (-np.inf, np.inf),
                                                           'inter': None}
                                                     },
                             'Sigmoidal Temperatura': {'a': {'límites': (-np.inf, np.inf),
                                                             'inter': None},
                                                       'b': {'límites': (0, np.inf),
                                                             'inter': None}
                                                       }
                             }
                },

    'Transiciones': {'Edad': {'Nada': {},

                              'Días': {},  # No se necesitan coeficientes en este caso

                              'Días grados': {'mín': {'límites': (-np.inf, np.inf),
                                                      'inter': None},
                                              'máx': {'límites': (-np.inf, np.inf),
                                                      'inter': None}
                                              },
                              'Brière Temperatura': {'t_dev_mín': {'límites': (-np.inf, np.inf),
                                                                   'inter': None},
                                                     't_letal': {'límites': (-np.inf, np.inf),
                                                                 'inter': None}
                                                     },
                              'Logan Temperatura': {'rho': {'límites': (0, 1),
                                                            'inter': None},
                                                    'delta': {'límites': (0, 1),
                                                              'inter': None},
                                                    't_letal': {'límites': (-np.inf, np.inf),
                                                                'inter': None}
                                                    },
                              'Brière No Linear Temperatura': {'t_dev_mín': {'límites': (-np.inf, np.inf),
                                                                             'inter': None},
                                                               't_letal': {'límites': (-np.inf, np.inf),
                                                                           'inter': None},
                                                               'm': {'límites': (0, np.inf),
                                                                     'inter': None}
                                                               },
                              },

                     'Prob': {'Nada': {},

                              'Constante': {'a': {'límites': (0, np.inf),
                                                  'inter': None}
                                            },

                              'Normal': {'mu': {'límites': (0, np.inf),
                                                'inter': None},
                                         'sigma': {'límites': (0, np.inf),
                                                   'inter': None}
                                         },
                              'Triang': {'a': {'límites': (0, np.inf),
                                               'inter': None},
                                         'b': {'límites': (0, np.inf),
                                               'inter': None},
                                         'c': {'límites': (0, np.inf),
                                               'inter': None}
                                         },
                              'Cauchy': {'u': {'límites': (0, np.inf),
                                               'inter': None},
                                         'f': {'límites': (0, np.inf),
                                               'inter': None}
                                         },
                              'Gamma': {'u': {'límites': (0, np.inf),
                                              'inter': None},
                                        'f': {'límites': (0, np.inf),
                                              'inter': None},
                                        'a': {'límites': (0, np.inf),
                                              'inter': None}
                                        },
                              'Logística': {'u': {'límites': (0, np.inf),
                                                  'inter': None},
                                            'f': {'límites': (0, np.inf),
                                                  'inter': None},
                                            },
                              'T': {'k': {'límites': (0, np.inf),
                                          'inter': None},
                                    'mu': {'límites': (0, np.inf),
                                           'inter': None},
                                    'sigma': {'límites': (0, np.inf),
                                              'inter': None}
                                    }
                              },

                     'Mult': {'Nada': {},

                              'Linear': {'a': {'límites': (0, np.inf),
                                               'inter': None}
                                         }
                              }
                     },

    'Reproducción': {'Edad': {'Nada': {},

                              'Días': {},  # No se necesitan coeficientes en este caso

                              'Días grados': {'mín': {'límites': (-np.inf, np.inf),
                                                      'inter': None},
                                              'máx': {'límites': (-np.inf, np.inf),
                                                      'inter': None}
                                              },
                              'Brière Temperatura': {'t_dev_mín': {'límites': (-np.inf, np.inf),
                                                                   'inter': None},
                                                     't_letal': {'límites': (-np.inf, np.inf),
                                                                 'inter': None}
                                                     },
                              'Logan Temperatura': {'rho': {'límites': (0, 1),
                                                            'inter': None},
                                                    'delta': {'límites': (0, 1),
                                                              'inter': None},
                                                    't_letal': {'límites': (-np.inf, np.inf),
                                                                'inter': None}
                                                    },
                              'Brière No Linear Temperatura': {'t_dev_mín': {'límites': (-np.inf, np.inf),
                                                                             'inter': None},
                                                               't_letal': {'límites': (-np.inf, np.inf),
                                                                           'inter': None},
                                                               'm': {'límites': (0, np.inf),
                                                                     'inter': None}
                                                               },
                              },

                     'Prob': {'Nada': {},

                              'Constante': {'n': {'límites': (0, np.inf),
                                                  'inter': None},
                                            'q': {'límites': (0, np.inf),
                                                  'inter': None}
                                            },
                              'Depredación': {'n': {'límites': (0, np.inf),
                                                    'inter': ['presa']}
                                              },
                              'Normal': {'n': {'límites': (0, np.inf),
                                               'inter': None},
                                         'mu': {'límites': (0, np.inf),
                                                'inter': None},
                                         'sigma': {'límites': (0, np.inf),
                                                   'inter': None}
                                         },
                              'Triang': {'n': {'límites': (0, np.inf),
                                               'inter': None},
                                         'a': {'límites': (0, np.inf),
                                               'inter': None},
                                         'b': {'límites': (0, np.inf),
                                               'inter': None},
                                         'c': {'límites': (0, np.inf),
                                               'inter': None}
                                         },
                              'Cauchy': {'n': {'límites': (0, np.inf),
                                               'inter': None},
                                         'u': {'límites': (0, np.inf),
                                               'inter': None},
                                         'f': {'límites': (0, np.inf),
                                               'inter': None}
                                         },
                              'Gamma': {'n': {'límites': (0, np.inf),
                                              'inter': None},
                                        'u': {'límites': (0, np.inf),
                                              'inter': None},
                                        'f': {'límites': (0, np.inf),
                                              'inter': None},
                                        'a': {'límites': (0, np.inf),
                                              'inter': None}
                                        },
                              'Logística': {'n': {'límites': (0, np.inf),
                                                  'inter': None},
                                            'u': {'límites': (0, np.inf),
                                                  'inter': None},
                                            'f': {'límites': (0, np.inf),
                                                  'inter': None},
                                            },
                              'T': {'n': {'límites': (0, np.inf),
                                          'inter': None},
                                    'k': {'límites': (0, np.inf),
                                          'inter': None},
                                    'mu': {'límites': (0, np.inf),
                                           'inter': None},
                                    'sigma': {'límites': (0, np.inf),
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
    }

}


ecs_suelo = {
    'profund': {'límites': (0, np.inf),
                'unid': 'cm',
                'cód_DSSAT': 'SLDP',
                'tmñ_DSSAT': 5},
    'albedo': {'límites': (0, 1),
               'unid': None,
               'cód_DSSAT': 'SALB',
               'tmñ_DSSAT': 5
               },
    'límite_evap': {'límites': (0, np.inf),
                    'unid': 'cm',
                    'cód_DSSAT': 'SLU1',
                    'tmñ_DSSAT': 5
                    },
    'taza_drenaje': {'límites': (0, 1),
                     'unid': 'día -1',
                     'cód_DSSAT': 'SLDR',
                     'tmñ_DSSAT': 5
                     },
    'factor_drenaje_SCS': {'límites': (30, 100),
                           'unid': None,  # Verificar las unidades
                           'cód_DSSAT': 'SLDR',
                           'tmñ_DSSAT': 5
                           },
    'factor_mineral': {'límites': (0, 1),
                       'unid': None,
                       'cód_DSSAT': 'SLNF',
                       'tmñ_DSSAT': 5
                       },
    'factor_fotosyn': {'límites': (0, 1),
                       'unid': None,
                       'cód_DSSAT': 'SLPF',
                       'tmñ_DSSAT': 5
                       },
    'niveles': {'límites': (0, np.inf),
                'unid': 'cm',
                'cód_DSSAT': 'SLB',
                'tmñ_DSSAT': 5
                },
    'P_extract': {'límites': (0, np.inf),
                  'unid': 'mg kg-1',
                  'cód_DSSAT': 'SLPX',
                  'tmñ_DSSAT': 5
                  },
    'P_total': {'límites': (0, np.inf),
                'unid': 'mg kg-1',
                'cód_DSSAT': 'SLPT',
                'tmñ_DSSAT': 5
                },
    'P_orgán': {'límites': (0, np.inf),
                'unid': 'mg kg -1',
                'cód_DSSAT': 'SLPO',
                'tmñ_DSSAT': 5
                },
    'CaCO3': {'límites': (0, np.inf),
              'unid': 'g kg-1',
              'cód_DSSAT': 'SLCA',
              'tmñ_DSSAT': 5
              },
    'Al': {'límites': (0, np.inf),
           'unid': 'cmol kg-1',  # Verificar unidades
           'cód_DSSAT': 'SLAL',
           'tmñ_DSSAT': 5
           },
    'Fe': {'límites': (0, np.inf),
           'unid': 'cmol kg-1',  # Verificar unidades
           'cód_DSSAT': 'SLFE',
           'tmñ_DSSAT': 5
           },
    'Mn': {'límites': (0, np.inf),
           'unid': 'cmol kg-1',  # Verificar unidades
           'cód_DSSAT': 'SLMN',
           'tmñ_DSSAT': 5
           },
    'satur_base': {'límites': (0, np.inf),
                   'unid': 'cmol kg-1',
                   'cód_DSSAT': 'SLBS',
                   'tmñ_DSSAT': 5
                   },
    'isoterm_P_a': {'límites': (0, np.inf),
                    'unid': 'mmol kg-1',
                    'cód_DSSAT': 'SLPA',
                    'tmñ_DSSAT': 5
                    },
    'isoterm_P_b': {'límites': (0, np.inf),
                    'unid': 'mmol kg-1',
                    'cód_DSSAT': 'SLPB',
                    'tmñ_DSSAT': 5
                    },
    'K_intercamb': {'límites': (0, np.inf),
                    'unid': 'cmol kg-1',
                    'cód_DSSAT': 'SLKE',
                    'tmñ_DSSAT': 5
                    },
    'Mg': {'límites': (0, np.inf),
           'unid': 'cmol kg-1',
           'cód_DSSAT': 'SLMG',
           'tmñ_DSSAT': 5
           },
    'Na': {'límites': (0, np.inf),
           'unid': 'cmol kg-|',
           'cód_DSSAT': 'SLNA',
           'tmñ_DSSAT': 5
           },
    'S': {'límites': (0, np.inf),
          'unid': 'cmol kg-1',  # Verificar unidades
          'cód_DSSAT': 'SLSU',
          'tmñ_DSSAT': 5
          },
    'conduct_eléc': {'límites': (0, np.inf),
                     'unid': 'seimen',
                     'cód_DSSAT': 'SLEC',
                     'tmñ_DSSAT': 5
                     },
    'límite_bajo': {'límites': (0, np.inf),
                    'unid': None,
                    'cód_DSSAT': 'SLLL',
                    'tmñ_DSSAT': 5
                    },
    'límite_alto': {'límites': (0, np.inf),
                    'unid': None,
                    'cód_DSSAT': 'SDUL',
                    'tmñ_DSSAT': 5
                    },
    'límite_alto_sat': {'límites': (0, np.inf),
                        'unid': None,
                        'cód_DSSAT': 'SSAT',
                        'tmñ_DSSAT': 5
                        },
    'factor_crec_raíz': {'límites': (0, 1),
                         'unid': None,
                         'cód_DSSAT': 'SRGF',
                         'tmñ_DSSAT': 5
                         },
    'cond_hídr_sat': {'límites': (0, np.inf),
                      'unid': 'cm h-1',
                      'cód_DSSAT': 'SSKS',
                      'tmñ_DSSAT': 5
                      },
    'densidad_suelo': {'límites': (0, np.inf),
                       'unid': 'g cm-3',
                       'cód_DSSAT': 'SBDM',
                       'tmñ_DSSAT': 5
                       },
    'C_org': {'límites': (0, 100),
              'unid': None,
              'cód_DSSAT': 'SLOC',
              'tmñ_DSSAT': 5
              },
    'frac_arcill': {'límites': (0, 100),
                    'unid': None,
                    'cód_DSSAT': 'SLCL',
                    'tmñ_DSSAT': 5
                    },
    'frac_lim': {'límites': (0, 100),
                 'unid': None,
                 'cód_DSSAT': 'SLSI',
                 'tmñ_DSSAT': 5
                 },
    'frac_rocas': {'límites': (0, 100),
                   'unid': None,
                   'cód_DSSAT': 'SLCF',
                   'tmñ_DSSAT': 5
                   },
    'N_total': {'límites': (0, 100),
                'unid': None,
                'cód_DSSAT': 'SLNI',
                'tmñ_DSSAT': 5
                },
    'pH_agua': {'límites': (-np.inf, np.inf),
                'unid': None,
                'cód_DSSAT': 'SLHW',
                'tmñ_DSSAT': 5
                },
    'pH_tamp': {'límites': (-np.inf, np.inf),
                'unid': None,
                'cód_DSSAT': 'SLHB',
                'tmñ_DSSAT': 5
                },
    'poten_intercamb_cat': {'límites': (0, np.inf),
                            'unid': 'cmol kg-1',
                            'cód_DSSAT': 'SCEC',
                            'tmñ_DSSAT': 5
                            },
}


ecs_cult = {
    'Día_corto_crít': {
        'límites': (0, np.inf),
        'unid': 'horas',
        'cultivos': {
            'tomate': {
                'DSSAT': {
                    'CROPGRO': {
                        'tipo': 'variedad',
                        'cód': 'CSDL',
                        'unid': 'horas'
                    }
                }
            }
        }
    },
    'Pend_desarroll_fotoper': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'PPSEN',
                    'unid': '1/hora'
                }
            }
        }
    },
    'Tiempo_emerg_flor': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'EM-FL',
                    'unid': 'días'
                }
            }
        }
    },
    'Tiempo_flor_fruta': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'FL-SH',
                    'unid': 'días'
                }
            }
        }
    },
    'Tiempo_flor_sem': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'FL-SD',
                    'unid': 'días'
                }
            }
        }
    },
    'Tiempo_sem_matur': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'SD-PM',
                    'unid': 'días'
                }
            }
        }
    },
    'Tiempo_flor_finhoja': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'FL-LF',
                    'unid': 'días'
                }
            }
        }
    },
    'Foto_máx': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'LFMAX',
                    'unid': 'mg CO2/(m2*s)'
                }
            }
        }
    },
    'Superfi_spec_hoja': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'SLAVR',
                    'unid': 'cm2/g'
                }
            }
        }
    },
    'Tamañ_hoja_máx': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'SIZLF',
                    'unid': 'cm2'
                }
            }
        }
    },
    'Máx_crec_semfrut': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'XFRT',
                    'unid': 'días'
                }
            }
        }
    },
    'Peso_sem_máx': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'WTPSD',
                    'unid': 'g'
                }
            }
        }
    },
    'Tiempo_llenar_sem': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'SFDUR',
                    'unid': 'días'
                }
            }
        }
    },
    'Sem_por_frut': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'SDPDV',
                    'unid': 'semillas'
                }
            }
        }
    },
    'Tiempo_llen_sem_opt': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'PODUR',
                    'unid': 'días'
                }
            }
        }
    },
    'Ratio_sem_frut': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'THRSH',
                    'unid': None
                }
            }
        }
    },
    'Frac_prot_sem': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'SDPRO',
                    'unid': None
                }
            }
        }
    },
    'Frac_aceit_sem': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'variedad',
                    'cód': 'SDLIP',
                    'unid': None
                }
            }
        }
    },
    'Grupo_matur': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'MG',
                    'unid': ''
                }
            }
        }
    },
    'Indic_adapt_temp': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'TM',
                    'unid': ''
                }
            }
        }
    },
    'Taza_rep_min': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'THVAR',
                    'unid': ''
                }
            }
        }
    },
    'Tiempo_siembr_emer': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'PL-EM',
                    'unid': 'días'
                }
            }
        }
    },
    'Tiempo_emer_hoja': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'EM-V1',
                    'unid': 'días'
                }
            }
        }
    },
    'Tiempo_hoja_finjuv': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'V1-JU',
                    'unid': 'días'
                }
            }
        }
    },
    'Tiempo_inducflor': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'JU-R0',
                    'unid': 'días'
                }
            }
        }
    },
    'Prop_tiemp_flor_frut': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'PM06',
                    'unid': ''
                }
            }
        }
    },
    'Prop_tiemp_sem_mat': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'PM09',
                    'unid': ''
                }
            }
        }
    },
    'Tiemp_frut': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'LNGSH',
                    'unid': 'días'
                }
            }
        }
    },
    'Tiemp_matfis_matcos': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'R7-R8',
                    'unid': 'días'
                }
            }
        }
    },
    'Tiemp_flor_hoja': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'FL-VS',
                    'unid': 'días'
                }
            }
        }
    },
    'Taza_aparenc_hoja': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'TRIFL',
                    'unid': 'días'
                }
            }
        }
    },
    'Anch_rel_ecotipo': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'RWDTH',
                    'unid': ''
                }
            }
        }
    },
    'Altura_rel_ecotipo': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'RHGHT',
                    'unid': ''
                }
            }
        }
    },
    'Aumen_sensit_día': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'R1PPO',
                    'unid': 'h'
                }
            }
        }
    },
    'Temp_min_flor': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'OPTBI',
                    'unid': 'C'
                }
            }
        }
    },
    'Pend_desarroll_flor': {
        'tomate': {
            'DSSAT': {
                'CROPGRO': {
                    'tipo': 'ecotipo',
                    'cód': 'SLOBI',
                    'unid': ''
                }
            }
        }
    }
}


# Funciones necesarias para el manejo de diccionarios de ecuaciones y de parámetros
def gen_ec_inic(d_ecs, inter=None, d=None):
    """
    Esta función toma un diccionario de especificaciones de parámetros de ecuaciones y lo convierte en un diccionario
    de distribuciones iniciales.

    :param d_ecs: El diccionario de las especificaciones de parámetros para cada tipo de ecuación posible
    Por ejemplo, ``ecs_orgs``.
    :type d_ecs: dict

    :param inter: Un diccionario, si se aplica, de las interacciones con otras partes del modelo necesarios para
    establecer las ecuaciones de manera correcta. Un ejemplo común sería el diccionario de las presas de una etapa
    para establecer las ecuaciones de depredación.
    :type inter: dict

    :param d: Parámetro que siempre se debe dejar a ``None`` cuando de usa esta función. Está allí para permetir las
    funcionalidades recursivas de la función (que le permite convertir diccionarios de estructura arbitraria).
    :type d: dict

    :return: Un diccionario, con la misma estructura que d_tipos_ecs pero con diccionarios de distribuciones de
    parámetros ya iniciados con distribuciones no informativas.
    :rtype: dict
    """

    # Si es la primera iteración, crear un diccionario vacío
    if d is None:
        d = {}

    # Para cada llave el en diccionario
    for ll, v in d_ecs.items():

        if type(v) is dict:
            # Si el valor es otro diccionario, crearlo en "d" también.
            d[ll] = {}

            if 'límites' in v:
                # Si llegamos a la especificación de límites del parámetro

                # Crear la distribución inicial según las interacciones, si hay. La distribución inicial siempre tiene
                # el número de identificación '0'.
                if 'inter' not in v.keys() or v['inter'] is None:
                    # Si no hay interacciones, es muy fácil
                    d[ll]['0'] = Incert.límites_a_texto_apriori(v['límites'])

                else:
                    # Si hay interacciones, hay que repetir el parámetro para cada interacción.
                    d[ll] = {}

                    if inter is not None:
                        # Si se especificaron interaccciones...
                        for i in inter[v['inter']]:
                            # Crear una versión del parámetro para cada interacción
                            d[ll][i] = {}

                            # Llenar el nuevo diccionario con su distribución no informativa
                            d[ll][i]['0'] = Incert.límites_a_texto_apriori(v['límites'])
                    else:
                        # Si no se especificarion, pasar
                        pass

            else:
                # Si, en cambio, no llegamos a la especificación de límites del parámetro, llamar esta función
                # con el nuevo diccionario.
                gen_ec_inic(d_ecs=v, inter=inter, d=d[ll])

        else:
            # Si el valor no era diccionario, ignorarlo.
            pass

    # Devolver el diccionario inicializado con distribuciones no informativas.
    return d
