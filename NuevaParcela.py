from NuevoCoso import Simulable
from RAE.NuevaRedAE import Red
from CULTIVO.NuevoCultivo import Cultivo, ModeloCultivo
from Matemáticas.Experimentos import Experimento


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
        símismo.modelo_cultivo = ModeloCultivo(cultivo = cultivo)
        símismo.red = red

    def _prep_obs_exper(símismo, exper):
        raise NotImplementedError  # Para hacer

    def _procesar_predics_calib(símismo):
        raise NotImplementedError  # Para hacer

    def incrementar(símismo, paso, i, extrn):
        símismo.red.incrementar(paso=paso, i=i, extrn=extrn)
        símismo.modelo_cultivo.incrementar(paso=paso, i=i, extrn=extrn)

    def _sacar_líms_coefs_interno(símismo):
        raise NotImplementedError  # Para hacer

    def _llenar_coefs(símismo, n_rep_parám, calibs, comunes, usar_especificados):
        raise NotImplementedError  # Para hacer

    def dibujar(símismo, mostrar=True, archivo=None, exper=None):
        raise NotImplementedError  # Para hacer

    def _prep_predics(símismo, n_pasos, n_rep_parám, n_rep_estoc, n_parcelas):
        raise NotImplementedError  # Para hacer

    def _procesar_validación(símismo):
        raise NotImplementedError  # Para hacer

    def _prep_args_simul_exps(símismo, exper, n_rep_estoc, n_rep_paráms):
        raise NotImplementedError  # Para hacer

    def _acción_añadir_exp(símismo, experimento, corresp):
        raise NotImplementedError  # Para hacer

    def _sacar_coefs_interno(símismo):
        raise NotImplementedError  # Para hacer
