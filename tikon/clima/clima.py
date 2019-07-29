from datetime import timedelta

from tikon.estruc.módulo import Módulo, DimsRes
from tikon.result.res import Resultado, ResultadosMódulo
from تقدیر.مقام import مقام
from تقدیر.کوائف import کوائف


class Clima(Módulo):
    nombre = 'clima'

    def __init__(símismo, fuentes=None, escenario=8.5):
        símismo.fuentes = fuentes
        símismo.escenario = escenario
        símismo.datos = None  # type: کوائف or None

        super().__init__()

    def inter(símismo, coso, tipo):
        pass

    def iniciar_estruc(símismo, tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés):
        super().iniciar_estruc(tiempo, mnjdr_móds, calibs, n_rep_estoc, n_rep_parám, parc, vars_interés)
        if tiempo.fecha():
            t_inic, t_final = tiempo.fecha(), tiempo.fecha() + timedelta(days=tiempo._n_días)
            símismo.datos = مقام().کوائف_پانا(t_inic, t_final)

    def incrementar(símismo):
        if símismo.datos:
            diarios = símismo.datos.روزانہ()[símismo.tiempo.fecha()]
        # para hacer: aplicar diarios a Resultados

    def cerrar(símismo):
        pass

    def reqs_externos(símismo):
        pass

    def _gen_resultados(símismo, n_rep_estoc, n_rep_parám, vars_interés):
        if símismo.datos:
            vars_clima = símismo.datos.متاغیرات()
            parc = símismo.obt_val_control('parcelas')

            # para hacer: generalizar para todos módulos
            dims_base = DimsRes(n_estoc=n_rep_estoc, n_parám=n_rep_parám, parc=parc)

            if vars_interés is None:
                temporales = []
            elif vars_interés is True:
                temporales = vars_clima
            else:
                temporales = vars_interés

            return ResultadosMódulo([
                Resultado(
                    vr, dims_base,
                    tiempo=símismo.tiempo if vr in temporales else None,
                ) for vr in vars_clima
            ])
