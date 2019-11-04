import xarray as xr
from tikon.estruc.módulo import Módulo
from tikon.estruc.simul import SimulMódulo
from tikon.result.utils import EJE_TIEMPO, EJE_PARC, EJE_COORD
# noinspection PyUnresolvedReferences
from تقدیر.مقام import مقام


class Clima(Módulo):
    nombre = 'clima'

    def __init__(símismo, fuentes=None, escenario=8.5):
        símismo.fuentes = fuentes
        símismo.escenario = escenario

        super().__init__()

    def gen_simul(símismo, simul_exper, vars_interés, ecs):
        return SimulClima(símismo, simul_exper=simul_exper, vars_interés=vars_interés, ecs=ecs)


class SimulClima(SimulMódulo):
    resultados = []

    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        centroides = símismo.simul_exper.exper.controles['centroides']
        elev = símismo.simul_exper.exper.obt_control('elevación')
        parcelas = símismo.simul_exper.exper.obt_control('parcelas')
        eje_t = símismo.simul_exper.t.eje
        t_inic, t_final = eje_t[0], eje_t[-1]

        variables = {vr for fnt in mód.fuentes for vr in fnt}
        d_datos = {
            prc: مقام(centroides.loc[{EJE_PARC: prc, EJE_COORD: 'lat'}],
                      centroides.loc[{EJE_PARC: prc, EJE_COORD: 'lon'}],
                      elev.loc[{EJE_PARC: prc}]
                      ).کوائف_پانا(
                سے=t_inic, تک=t_final, ذرائع=mód.fuentes, خاکے=mód.escenario
            ).روزانہ().loc[{EJE_TIEMPO: eje_t}]
            for prc in parcelas
        }
        símismo.datos = xr.Dataset({
            res: xr.DataArray(
                [d_datos[prc][res] for prc in parcelas],
                coords={EJE_PARC: parcelas, EJE_TIEMPO: eje_t},
                dims=[EJE_PARC, EJE_TIEMPO]
            ) for res in variables
        })

        super().__init__(Clima.nombre, simul_exper, ecs=ecs, vars_interés=vars_interés)

    def requísitos(símismo, controles=False):
        if controles:
            return ['centroides', 'elevación']

    def incrementar(símismo, paso, f):
        diarios = símismo.datos.loc[{EJE_TIEMPO: f}]
        for res in símismo:
            símismo[res].loc[{EJE_TIEMPO: f}] = diarios[str(res)]
