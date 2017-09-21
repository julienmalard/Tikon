import numpy as np
from tikon.Cultivo.NuevoCultivo import Cultivo

from tikon.Coso import Simulable


class Parcela(Simulable):
    """

    """
    ext = '.prc'

    def __init__(símismo, nombre, cultivo, red):
        """

        :param nombre:
        :type nombre: str

        :param cultivo:
        :type cultivo: Cultivo

        :param red:
        :type red: Red
        """

        super().__init__(nombre)

        símismo.cultivo = cultivo
        símismo.red = red

        símismo.receta['estr'][] =

        símismo.predics = {'Suelo': {'prof_nivel': np.array([]),
                                     'dens_apar_húm': np.array([]),
                                     'C_org': np.array([]),
                                     'N_total': np.array([]),
                                     'pH_agua': np.array([]),
                                     'pH_tamp': np.array([]),
                                     'P_extr': np.array([]),
                                     'K_intercamb': np.array([]),
                                     'Agua': np.array([]),
                                     'Amonio': np.array([]),
                                     'Nitrato': np.array([])
                                     },
                           'Crec': {'índ_super_hoja': np.array([]),
                                    'masa_seca_hoja': np.array([]),
                                    'masa_seca_tallo': np.array([]),
                                    'masa_seca_grano': np.array([]),
                                    'profund_suelo': np.array([]),
                                    'masa_seca_raíz': np.array([]),
                                    'masa_seca_total': np.array([])
                                    },
                           'Meteo': {'precip': np.array([]),
                                     'h_día': np.array([]),
                                     'h_crep_a_crep': np.array([]),
                                     'rad solar': np.array([]),
                                     'flujo_photon_día': np.array([]),
                                     'índice_nubes': np.array([]),
                                     'temp_máx_día': np.array([]),
                                     'temp_mín_día': np.array([]),
                                     'temp_prom_día': np.array([]),
                                     'temp_prom_h_día': np.array([]),
                                     'punto_rocío': np.array([]),
                                     'prom_temp_aire_crec': np.array([]),
                                     'prom_temp_aire_día_crec': np.array([]),
                                     'veloc_viento': np.array([]),
                                     'CO2': np.array([])
                                     }
                           }

    def _prep_obs_exper(símismo, exper):
        raise NotImplementedError  # Para hacer

    def _procesar_predics_calib(símismo):
        raise NotImplementedError  # Para hacer

    def incrementar(símismo, paso, i, extrn):
        """
        Incrementamos los modelos de RedAE y de cultivo.

        :param paso:
        :type paso:
        :param i:
        :type i:
        :param extrn:
        :type extrn:

        """
        símismo.red.incrementar(paso=paso, i=i, extrn=extrn)
        símismo.cultivo.incrementar(paso=paso, i=i, extrn=extrn)

    def _sacar_líms_coefs_interno(símismo):
        raise NotImplementedError  # Para hacer

    def _llenar_coefs(símismo, n_rep_parám, calibs, comunes, usar_especificadas):
        raise NotImplementedError  # Para hacer

    def dibujar(símismo, mostrar=True, archivo=None, exper=None, **kwargs):
        raise NotImplementedError  # Para hacer

    def _prep_args_simul_exps(símismo, exper, n_rep_estoc, n_rep_paráms, **kwargs):
        raise NotImplementedError  # Para hacer

    def _actualizar_vínculos_exps(símismo):
        raise NotImplementedError  # Para hacer

    def _sacar_coefs_interno(símismo):
        raise NotImplementedError  # Para hacer
