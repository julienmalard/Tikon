import inspect
from itertools import product

import numpy as np

from tikon.central import Parcela, GrupoParcelas
from tikon.central.matriz import Datos, combinar, codificar_coords
from tikon.móds.rae.orgs.plantas import externa as plt_externas
from tikon.móds.rae.orgs.plantas.externa import CultivoExterno
from tikon.utils import EJE_PARÁMS, EJE_ESTOC


class ParcelasCultivoExterno(GrupoParcelas):

    def __init__(símismo, parcelas, combin=None):
        combin = combin if combin is not None else (EJE_ESTOC, EJE_PARÁMS)
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
    trads_cultivos = {}

    def __init__(símismo, sim, parcelas):
        símismo.sim = sim
        símismo.parcelas = parcelas
        símismo.combin = parcelas.combin
        símismo.reps = sim.simul_exper.reps

        símismo.instancias = [
            símismo.cls_instancia(
                sim=símismo, índs=índs, reps=símismo.reps
            ) for índs in símismo.combin.índices(símismo.reps)
        ]

    @property
    def cls_instancia(símismo):
        raise NotImplementedError

    def obt_org(símismo, cultivo, variedad=None):
        cultivo = cultivo.lower()
        if cultivo in símismo.trads_cultivos:
            cultivo = símismo.trads_cultivos[cultivo]

        if cultivo in símismo.parcelas.conv_cultivos:
            orgs_potenciales = símismo.parcelas.conv_cultivos[cultivo]
        else:
            _cls_apropriada = _cls_cultivos[cultivo.lower()]
            orgs_potenciales = [org for org in símismo.sim.orgs if isinstance(org, _cls_apropriada)]
        if variedad:
            return next(
                (clt for clt in orgs_potenciales if clt.variedad and clt.variedad.lower() == variedad.lower()),
                orgs_potenciales[0]
            )
        return orgs_potenciales[0]

    def requísitos(símismo, controles=False):
        raise NotImplementedError

    def iniciar(símismo):
        for inst in símismo.instancias:
            inst.iniciar()
        símismo.llenar_vals()

    def incrementar(símismo, paso, f):
        for inst in símismo.instancias:
            inst.incrementar(paso, f)
        símismo.llenar_vals()

    def llenar_vals(símismo):
        l_datos = [inst.datos for inst in símismo.instancias]
        vrs = set(vr for d in l_datos for vr in d)
        datos = {
            vr: símismo.combin.desagregar(
                combinar(*[d[vr] for d in l_datos]), reps=símismo.reps
            ) for vr in vrs
        }
        for var in datos:
            símismo.sim.poner_valor(var=var, val=datos[var])

    def aplicar_daño(símismo, daño):
        daño = símismo.combin.agregar(daño)
        for inst in símismo.instancias:
            inst.aplicar_daño(daño.loc[codificar_coords(inst.índices)])

    def cerrar(símismo):
        for inst in símismo.instancias:
            inst.cerrar()


class CombinSimsCult(object):
    def __init__(símismo, transf=None):
        transf = transf or {}
        if isinstance(transf, str):
            transf = [transf]
        if not isinstance(transf, dict):
            transf = {eje: np.median for eje in transf}
        símismo.transf = transf

    def agregar(símismo, ingreso):
        for eje, func in símismo.transf.items():
            ingreso = ingreso.f_eje(func, dim=eje)
        return ingreso

    def índs(símismo, reps):
        dims = [dim for dim in reps if dim not in símismo.transf]
        for índs in product(*[range(crds) for dim, crds in reps.items() if dim in dims]):
            yield dict(zip(dims, índs))

    def desagregar(símismo, egreso, reps):
        return egreso.expandir_dims(codificar_coords({ll: range(v) for ll, v in reps.items() if ll in símismo.transf}))


class InstanciaSimulCultivo(object):
    def __init__(símismo, sim, índs, reps):
        símismo.sim = sim
        símismo.índs = {ll: [v] if isinstance(v, int) else v for ll, v in índs.items()}
        res = [sim.sim[r] for r in sim.sim]
        símismo.datos = {
            str(vr): Datos(0., dims=[dim for dim in vr.datos.dims if dim not in reps] + list(símismo.índs),
                           coords={**{dim: vr.datos.coords[dim] for dim in vr.datos.dims if dim not in reps},
                                   **símismo.índs}) for vr in res
        }

    def iniciar(símismo):
        símismo.llenar_vals()

    def incrementar(símismo, paso, f):
        raise NotImplementedError

    def llenar_vals(símismo):
        raise NotImplementedError

    def aplicar_daño(símismo, daño):
        raise NotImplementedError

    def cerrar(símismo):
        raise NotImplementedError


_cls_cultivos = {
    clt[1].cultivo: clt[1] for clt in inspect.getmembers(plt_externas, inspect.isclass)
    if issubclass(clt[1], plt_externas.CultivoExterno) and clt[1] != plt_externas.CultivoExterno
}
