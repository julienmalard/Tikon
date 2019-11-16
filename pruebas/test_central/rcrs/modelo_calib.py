import numpy as np
import pandas as pd
import xarray as xr
from tikon.central import Módulo, SimulMódulo, Modelo, Exper, Parcela, Coso
from tikon.central.res import Resultado
from tikon.ecs import ÁrbolEcs, CategEc, EcuaciónVacía, SubcategEc, Ecuación, Parám
from tikon.ecs.aprioris import APrioriDens
from tikon.result import Obs
from tikon.utils import EJE_TIEMPO, EJE_PARC, EJE_ESTOC

f_inic = '2000-01-01'


class A(Parám):
    nombre = 'a'
    unids = None
    líms = (0, None)
    apriori = APrioriDens((0, 3), .90)
    eje_cosos = 'coso'


class EcuaciónParám(Ecuación):
    nombre = 'ec'
    eje_cosos = 'coso'
    cls_ramas = [A]
    _nombre_res = 'res'

    def eval(símismo, paso, sim):
        ant = símismo.obt_valor_res(sim)
        n_estoc = len(ant[EJE_ESTOC])
        return ant + símismo.cf['a'] + xr.DataArray(
            np.random.random(n_estoc)*0.1, coords={EJE_ESTOC: np.arange(n_estoc)}, dims=[EJE_ESTOC]
        )


class SubCategParám(SubcategEc):
    nombre = 'subcateg'
    cls_ramas = [EcuaciónParám, EcuaciónVacía]
    eje_cosos = 'coso'
    _nombre_res = 'res'


class CategParám(CategEc):
    nombre = 'categ'
    cls_ramas = [SubCategParám]
    eje_cosos = 'coso'


class EcsParám(ÁrbolEcs):
    nombre = 'árbol'
    cls_ramas = [CategParám]


class CosoParám(Coso):
    def __init__(símismo, nombre):
        super().__init__(nombre, EcsParám)


coso = CosoParám('hola')


class Res(Resultado):
    nombre = 'res'
    unids = None

    def __init__(símismo, sim, coords, vars_interés):
        coords = {'coso': sim.ecs.cosos, **coords}
        super().__init__(sim, coords, vars_interés)


class SimulMóduloValid(SimulMódulo):
    resultados = [Res]

    def incrementar(símismo, paso, f):
        super().incrementar(paso, f)


class MóduloValid(Módulo):
    nombre = 'módulo'
    cls_simul = SimulMóduloValid
    cls_ecs = EcsParám
    eje_coso = 'coso'


obs = Obs(
    mód='módulo', var='res', datos=xr.DataArray(
        np.arange(10),
        coords={EJE_TIEMPO: pd.date_range(f_inic, periods=10, freq='D')}, dims=[EJE_TIEMPO]
    ).expand_dims({EJE_PARC: ['parcela'], 'coso': [coso]})
)

exper = Exper('exper', Parcela('parcela'), obs=obs)
modelo = Modelo(MóduloValid(coso))
