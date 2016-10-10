from NuevoCoso import Simulable


class Paisaje(Simulable):
    """
    
    """

    ext = '.psj'

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

    def dibujar(símismo, mostrar=True, archivo=None, exper=None):
        raise NotImplementedError  # Para hacer

    def _procesar_validación(símismo):
        raise NotImplementedError  # Para hacer

    def _prep_args_simul_exps(símismo, exper, n_rep_estoc, n_rep_paráms):
        raise NotImplementedError  # Para hacer

    def _actualizar_vínculos_exps(símismo, experimento, corresp):
        raise NotImplementedError  # Para hacer

    def _sacar_coefs_interno(símismo):
        raise NotImplementedError  # Para hacer
    