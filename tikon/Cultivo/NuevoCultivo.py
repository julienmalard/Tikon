from tikon.Coso import Coso, Simulable


class Cultivo(Coso):
    """
    
    """
    ext = '.clt'
    
    def _sacar_coefs_interno(símismo):
        raise NotImplementedError

    def _sacar_líms_coefs_interno(símismo):
        raise NotImplementedError


class ModeloCultivo(Simulable):
    """
    Esta clase sirve para representar modelos de cultivos simulables.
    """

    def __init__(símismo, cultivo, variedad, programa=None, modelo=None):



    def _prep_obs_exper(símismo, exper):
        raise NotImplementedError  # Para hacer

    def _procesar_predics_calib(símismo):
        raise NotImplementedError  # Para hacer

    def incrementar(símismo, paso, i, extrn):
        raise NotImplementedError  # Para hacer

    def _sacar_líms_coefs_interno(símismo):
        raise NotImplementedError  # Para hacer

    def _llenar_coefs(símismo, n_rep_parám, calibs, comunes, usar_especificados):
        raise NotImplementedError  # Para hacer

    def dibujar(símismo, mostrar=True, archivo=None, exper=None, **kwargs):
        raise NotImplementedError  # Para hacer

    def _procesar_validación(símismo):
        raise NotImplementedError  # Para hacer

    def _prep_args_simul_exps(símismo, exper, n_rep_estoc, n_rep_paráms, **kwargs):
        raise NotImplementedError  # Para hacer

    def _actualizar_vínculos_exps(símismo):
        raise NotImplementedError  # Para hacer

    def _sacar_coefs_interno(símismo):
        raise NotImplementedError  # Para hacer


mods_cult = {
    'Maíz': {
        'DSSAT': {
            'IXIM': {
                'Comanda': 'DSCSM046.EXE MZIXM046',
                'Código cultivo': 'MZ'
            },
            'CERES': {
                'Comanda': 'DSCSM046.EXE MZCER046',
                'Código cultivo': 'MZ'
            }
        }
    },
    'Tomato': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'TM'
            }
        }
    },
    'Frijol': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'BN'
            }
        }
    },
    'Repollo': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'CB'
            }
        }
    },
    'Papas': {
        'DSSAT': {
            'SUBSTOR': {
                'Comanda': 'DSCSM046.EXE PTSUB046',
                'Código cultivo': 'PT'
            }
        }
    },
    'Piña': {
        'PIAL': {
            'CROPGRO': {
                'Comanda': 'MDRIV980.EXE MINPT980.EXE PIALO980.EXE I',
                'Código cultivo': 'PI'
            }
        }
    },
    'Habas': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'FB'
            }
        }
    },
    'Garbanzo': {
        'DSSAT': {
            'CROPGRO': {
                'Comanda': 'DSCSM046.EXE CRGRO046',
                'Código cultivo': 'CH'
            }
        }
    }
}
