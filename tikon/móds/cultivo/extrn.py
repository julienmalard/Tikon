import inspect
from itertools import product

import xarray as xr
from tikon.central import Parcela, GrupoParcelas
from tikon.móds.rae.orgs.plantas import externa as plt_externas
from tikon.móds.rae.orgs.plantas.externa import CultivoExterno
from tikon.result import EJE_PARC


class ParcelasCultivoExterno(GrupoParcelas):

    def __init__(símismo, parcelas, combin=('estoc', 'parám')):
        parcelas = [parcelas] if isinstance(parcelas, Parcela) else parcelas
        super().__init__(parcelas=parcelas)

        símismo.combin = combin if isinstance(combin, CombinSimsCult) else CombinSimsCult(combin)
        símismo.conv_cultivos = {}

    def conectar_cultivo(símismo, obj_cultivo, nombre):
        if isinstance(obj_cultivo, CultivoExterno):
            obj_cultivo = [obj_cultivo]
        if nombre not in símismo.conv_cultivos:
            símismo.conv_cultivos = []
        símismo.conv_cultivos[nombre] += obj_cultivo

    def gen_simul(símismo, sim):
        raise NotImplementedError


class SimulCultivoExterno(object):
    _trads_cultivos = {}

    def __init__(símismo, sim, parcelas):
        símismo.sim = sim
        símismo.parcelas = parcelas
        símismo.combin = parcelas.combin
        símismo.reps = sim.simul_exper.reps

        nombres_parcelas = [str(prc) for prc in parcelas]
        símismo.instancias = [símismo.cls_instancia(
            sim=símismo, índs={EJE_PARC: nombres_parcelas, **índs}
        ) for índs in símismo.combin.índs(símismo.reps)]

        símismo.llenar_vals()

    @property
    def cls_instancia(símismo):
        raise NotImplementedError

    def obt_org(símismo, cultivo, variedad=None):
        cultivo = cultivo.lower()
        if cultivo in símismo._trads_cultivos:
            cultivo = símismo._trads_cultivos[cultivo]

        _cls_apropiada = símismo.parcelas.cls_cultivos[cultivo.lower()]
        if cultivo in símismo.parcelas.conv_cultivos:
            orgs_potenciales = símismo.parcelas.conv_cultivos[cultivo]
        else:
            # noinspection PyTypeHints
            orgs_potenciales = [org for org in símismo.sim.orgs if isinstance(org, _cls_apropiada)]
        if variedad:
            return next(
                (clt for clt in orgs_potenciales if clt.variedad.lower() == variedad.lower()), orgs_potenciales[0]
            )
        return orgs_potenciales[0]

    def requísitos(símismo, controles=False):
        raise NotImplementedError

    def iniciar(símismo):
        for inst in símismo.instancias:
            inst.iniciar()

    def incrementar(símismo, paso, f):
        for inst in símismo.instancias:
            inst.incrementar(paso, f)
        símismo.llenar_vals()

    def llenar_vals(símismo):
        datos = símismo.combin.desagregar(
            xr.merge([inst.obt_datos() for inst in símismo.instancias]), coords=símismo.reps
        )
        for var, val in datos.items():
            símismo.sim.poner_valor(var=var, val=val)

    def aplicar_daño(símismo, daño):
        daño = símismo.combin.agregar(daño)
        for inst in símismo.instancias:
            inst.aplicar_daño(daño.loc[inst.índs])

    def cerrar(símismo):
        for inst in símismo.instancias:
            inst.cerrar()


class CombinSimsCult(object):
    def __init__(símismo, transf=None):
        transf = transf or {}
        if isinstance(transf, str):
            transf = []
        if not isinstance(transf, dict):
            transf = {eje: xr.DataArray.median for eje in transf}
        símismo.transf = transf

    def agregar(símismo, ingreso):
        for eje, func in símismo.transf.items():
            ingreso = func(ingreso, dim=[eje])

    def índs(símismo, reps):
        dims = [dim for dim in reps if dim not in símismo.transf]
        for índs in product(*[crds for dim, crds in reps.items()]):
            yield dict(zip(dims, índs))

    @staticmethod
    def desagregar(egreso, coords):
        return egreso.expand_dims(coords)


class InstanciaSimulCultivo(object):
    def __init__(símismo, sim, vars_, índs):
        símismo.sim = sim
        símismo.datos = xr.Dataset({vr: xr.DataArray(0., coords=índs, dims=list(índs)) for vr in vars_})
        símismo.llenar_vals()

    def iniciar(símismo):
        símismo.llenar_vals()

    def incrementar(símismo, paso, f):
        raise NotImplementedError

    def llenar_vals(símismo):
        raise NotImplementedError

    def aplicar_daño(símismo, daño):
        raise NotImplementedError

    def cerrar(símismo, paso, f):
        raise NotImplementedError


_cls_cultivos = {
    clt.cultivo: clt for clt in inspect.getmembers(plt_externas, inspect.isclass)
    if issubclass(clt, plt_externas.CultivoExterno)
}
