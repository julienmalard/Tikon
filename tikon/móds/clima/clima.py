import xarray as xr
from tikon.central.módulo import Módulo
from tikon.central.simul import SimulMódulo
from tikon.móds.clima.res import ResultadoClima
from tikon.utils import EJE_PARC, EJE_TIEMPO, EJE_COORD
from تقدیر.مقام import مقام, ذرائع_بنانا


class SimulClima(SimulMódulo):
    def __init__(símismo, mód, simul_exper, ecs, vars_interés):
        centroides = simul_exper.exper.controles['centroides']
        elev = simul_exper.exper.controles['elevaciones']
        parcelas = simul_exper.exper.controles['parcelas']
        eje_t = simul_exper.t.eje
        t_inic, t_final = eje_t[0], eje_t[-1]

        variables = mód.variables
        d_datos = {
            prc: مقام(
                centroides.loc[{EJE_PARC: prc, EJE_COORD: 'lat'}].matr[0],
                centroides.loc[{EJE_PARC: prc, EJE_COORD: 'lon'}].matr[0],
                elev.loc[{EJE_PARC: prc}].matr[0]
            ).کوائف_پانا(
                سے=t_inic, تک=t_final, ذرائع=mód.fuentes, خاکے=mód.escenario
            ).روزانہ().loc[eje_t[0]:eje_t[-1]]
            for prc in parcelas
        }
        símismo.datos = xr.Dataset({
            res: xr.DataArray(
                [d_datos[prc][res if res in d_datos[prc] else _vr_tikon_a_taqdir(res)] for prc in parcelas],
                coords={EJE_PARC: parcelas, EJE_TIEMPO: eje_t},
                dims=[EJE_PARC, EJE_TIEMPO]
            ) for res in variables
        })
        if all(x in símismo.datos.data_vars for x in ('temp_prom', 'temp_máx', 'temp_mín')):
            símismo.datos['temp_prom'] = símismo.datos['temp_prom'].fillna(
                (símismo.datos['temp_máx'] + símismo.datos['temp_mín']) / 2
            )
        for vr in símismo.datos.data_vars:
            if símismo.datos[vr].isnull().any():
                raise ValueError('Faltan datos en {vr}.'.format(vr=vr))

        super().__init__(Clima, simul_exper, ecs=ecs, vars_interés=vars_interés)

    @property
    def resultados(símismo):
        l_res = []
        for var in símismo.datos:  # type: str
            cls_res = type(var, (ResultadoClima,), {'nombre': var, 'unids': lambda: None})
            l_res.append(cls_res)
        return l_res

    def requísitos(símismo, controles=False):
        if controles:
            return {'centroides', 'elevaciones'}

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)
        diarios = símismo.datos.loc[{EJE_TIEMPO: f}].drop_vars(EJE_TIEMPO)
        for res in símismo:
            símismo[res].poner_valor(diarios[str(res)])


class Clima(Módulo):
    nombre = 'clima'
    cls_simul = SimulClima

    def __init__(símismo, fuentes=None, variables=None, escenario=8.5):
        símismo.fuentes = ذرائع_بنانا(fuentes)
        símismo.escenario = escenario
        símismo.variables = variables or list(set(vr for fnt in fuentes for vr in fnt.متغیرات))

        super().__init__()


def _vr_tikon_a_taqdir(vr):
    if vr in _conv_vars_taqdir:
        return _conv_vars_taqdir[vr]
    return vr


_conv_vars_taqdir = {
    'precip': 'بارش',
    'rad_solar': 'شمسی_تابکاری',
    'temp_máx': 'درجہ_حرارت_زیادہ',
    'temp_mín': 'درجہ_حرارت_کم',
    'temp_prom': 'درجہ_حرارت_اوسط',
    'fecha': 'تاریخ'
}
