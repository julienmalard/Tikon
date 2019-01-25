from datetime import timedelta

from tikon.estruc.módulo import Módulo
from تقدیر.مقام import مقام
from تقدیر.کوائف import کوائف


class Clima(Módulo):
    nombre = 'clima'

    def __init__(símismo, fuentes=None, escenario=8.5):
        símismo.fuentes = fuentes
        símismo.escenario = escenario
        símismo.lugar = None  # type: کوائف

        super().__init__()

    def inter(símismo, coso, tipo):
        pass

    def iniciar_estruc(símismo, tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés):
        super().iniciar_estruc( tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés)
        if tiempo.fecha():
            t_inic, t_final = tiempo.fecha(), tiempo.fecha() + timedelta(days=tiempo._n_días)
            símismo.lugar = مقام().کوائف_پانا(t_inic, t_final)

    def incrementar(símismo):
        if símismo.lugar:
            datos = símismo.lugar.روزانہ()[símismo.tiempo.fecha()]

    def cerrar(símismo):
        pass

    def paráms(símismo):
        return []

    def reqs_externos(símismo):
        pass

    def _gen_resultados(símismo, n_rep_estoc, n_rep_parám, vars_interés):
        return
