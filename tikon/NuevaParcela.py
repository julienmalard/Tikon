from tikon.Cultivo.NuevoCultivo import ModeloCultivo

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
        símismo.modelo_cultivo = ModeloCultivo(cultivo = cultivo)
        símismo.red = red

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
        símismo.modelo_cultivo.incrementar(paso=paso, i=i, extrn=extrn)

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
