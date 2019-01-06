import numpy as np

from tikon0.Coso import Simulable
from ..Cultivo.NuevoCultivo import Cultivo
from ..RAE.RedAE import Red


class Parcela(Simulable):
    """

    """

    ext = '.prc'

    def __init__(símismo, nombre, cultivo, red, proyecto):
        """

        :param nombre:
        :type nombre: str

        :param cultivo:
        :type cultivo: Cultivo

        :param red:
        :type red: Red
        """

        super().__init__(nombre, proyecto=proyecto)

        símismo.cultivo = cultivo
        símismo.red = red

        #        símismo.receta['estr'][] =

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

    def incrementar(símismo, paso, i, extrn, **kwargs):
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

    def actualizar(símismo):
        pass

    def _sacar_coefs_interno(símismo):
        pass

    def _llenar_coefs(símismo, nombre_simul, n_rep_parám, dib_dists, calibs=None):
        pass

    def _sacar_coefs_no_espec(símismo):
        pass

    def _gen_dics_valid(símismo, exper, paso, n_pasos, n_rep_estoc, n_rep_parám):
        pass

    def dibujar(símismo, mostrar=True, directorio=None, exper=None, **kwargs):
        pass

    def _actualizar_vínculos_exps(símismo):
        pass

    def especificar_apriori(símismo, **kwargs):
        pass

    def _procesar_simul(símismo):
        pass

    def _justo_antes_de_simular(símismo):
        pass

    def _gen_dic_predics_exps(símismo, exper, n_rep_estoc, n_rep_parám, paso, n_pasos, detalles):
        pass

    def _sacar_líms_coefs_interno(símismo):
        pass

    def _analizar_valid(símismo):
        pass

    def _gen_dics_calib(símismo, exper):
        pass
