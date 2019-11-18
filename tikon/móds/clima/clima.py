import xarray as xr
from tikon.central.módulo import Módulo
from tikon.central.simul import SimulMódulo
from tikon.móds.clima.res import ResultadoClima
# noinspection PyUnresolvedReferences
from tikon.utils import EJE_PARC, EJE_TIEMPO, EJE_COORD
from تقدیر.مقام import مقام


class SimulClima(SimulMódulo):
    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        centroides = simul_exper.exper.controles['centroides']
        elev = simul_exper.exper.controles['elevaciones']
        parcelas = simul_exper.exper.controles['parcelas']
        eje_t = simul_exper.t.eje
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
            _vr_taqdir_a_tikon(res): xr.DataArray(
                [d_datos[prc][res] for prc in parcelas],
                coords={EJE_PARC: parcelas, EJE_TIEMPO: eje_t},
                dims=[EJE_PARC, EJE_TIEMPO]
            ) for res in variables
        })

        super().__init__(Clima.nombre, simul_exper, ecs=ecs, vars_interés=vars_interés)

    @property
    def resultados(símismo):
        l_res = []
        for var in símismo.datos:
            cls_res = type(var, (ResultadoClima,))
            cls_res.nombre = var
            l_res.append(cls_res)
        return l_res

    def requísitos(símismo, controles=False):
        if controles:
            return ['centroides', 'elevación']

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        diarios = símismo.datos.loc[{EJE_TIEMPO: f}]
        for res in símismo:
            símismo[res].loc[{EJE_TIEMPO: f}] = diarios[str(res)]


class Clima(Módulo):
    nombre = 'clima'
    cls_simul = SimulClima

    def __init__(símismo, fuentes=None, escenario=8.5):
        símismo.fuentes = fuentes
        símismo.escenario = escenario

        super().__init__()


def _vr_taqdir_a_tikon(vr):
    if vr in _conv_vars_taqdir:
        return _conv_vars_taqdir[vr]
    return vr


_conv_vars_taqdir = {
    'بارش': 'precip',
    'شمسی_تابکاری': 'rad_solar',
    'درجہ_حرارت_زیادہ': 'temp_máx',
    'درجہ_حرارت_کم': 'temp_mín',
    'درجہ_حرارت_اوسط': 'temp_prom',
}
