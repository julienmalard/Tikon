from tikon0.Coso import Simulable


class Paisaje(Simulable):
    """
    
    """

    ext = '.psj'

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

    def incrementar(símismo, paso, i, detalles, extrn):
        pass

    def _sacar_líms_coefs_interno(símismo):
        pass

    def _analizar_valid(símismo):
        pass

    def _gen_dics_calib(símismo, exper):
        pass
