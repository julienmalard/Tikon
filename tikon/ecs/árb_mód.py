import xarray as xr

from .paráms import MnjdrValsCoefs, MatrParám, ValsParámCoso, ValsParámCosoInter
from .árb_coso import ÁrbolEcsCoso, CategEcCoso, SubcategEcCoso, EcuaciónCoso, ParámCoso


class PlantillaRamaEc(object):
    cls_ramas = []

    _cls_en_coso = NotImplemented
    _nombre_res = NotImplemented

    def __init__(símismo, modelo, mód, cosos, n_reps, ecs):

        símismo.cosos = cosos
        símismo._ramas = {}

        for rm in símismo.cls_ramas:
            activos = list(zip(*[
                (ec[rm.nombre], coso) for ec, coso in zip(ecs, cosos)
                if ec[rm.nombre].verificar_activa(modelo=modelo, mód=mód)
            ]))
            if activos:
                ecs_activos, cosos_activos = activos
                # convertir tuple a lista abajo es necesario para xr.DataArray.loc después
                símismo._ramas[rm.nombre] = rm(modelo, mód, list(cosos_activos), n_reps=n_reps, ecs=list(ecs_activos))

    def requísitos(símismo, controles=False):
        return {req for rm in símismo for req in (rm.requísitos(controles) or set())}

    def vals_paráms(símismo):
        return [pr for rm in símismo for pr in rm.vals_paráms()]

    def eval(símismo, paso, sim):
        for rm in símismo:
            rm.eval(paso, sim=sim)

        símismo.postproc(paso, sim=sim)

    def postproc(símismo, paso, sim):
        pass

    def act_vals(símismo):
        for rm in símismo:
            rm.act_vals()

    def obt_valor_res(símismo, sim, filtrar=True):
        return símismo.obt_valor_mód(sim, var=símismo._nombre_res, filtrar=filtrar)

    def obt_valor_mód(símismo, sim, var, filtrar=True):
        if filtrar:
            return sim.obt_valor(var).loc[{símismo.eje_cosos: símismo.cosos}]
        return sim.obt_valor(var)

    def poner_valor_res(símismo, sim, val, rel=False):
        sim.poner_valor(símismo._nombre_res, val=val, rel=rel)

    @staticmethod
    def poner_valor_mód(sim, var, val, rel=False):
        sim.poner_valor(var, val, rel=rel)

    @staticmethod
    def obt_valor_extern(sim, var, mód=None):
        if not mód:
            mód, var = var.split('.')
        return sim.simul_exper[mód].obt_valor(var)

    @staticmethod
    def poner_valor_extern(sim, var, val, mód=None, rel=False):
        if not mód:
            mód, var = var.split('.')
        return sim.simul_exper[mód].poner_valor(var, val, rel=rel)

    @staticmethod
    def obt_valor_control(sim, var):
        return sim.exper.controles[var]

    @classmethod
    def para_coso(cls, coso):
        return cls._cls_en_coso(cls, [c.para_coso(coso) for c in cls.cls_ramas], coso=coso)

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def eje_cosos(símismo):
        raise NotImplementedError

    def __iter__(símismo):
        for rm in símismo._ramas.values():
            yield rm

    def __getitem__(símismo, itema):
        if not isinstance(itema, str):
            itema = itema.nombre
        return símismo._ramas[itema]

    def __contains__(símismo, itema):
        return itema in símismo._ramas

    def __str__(símismo):
        return símismo.nombre


class ÁrbolEcs(PlantillaRamaEc):
    _cls_en_coso = ÁrbolEcsCoso
    eje_cosos = None

    def __init__(símismo, modelo, mód, cosos, n_reps):
        super().__init__(modelo, mód, cosos=cosos, n_reps=n_reps, ecs=[coso.ecs for coso in cosos])

    def cosos_en_categ(símismo, categ):
        if categ in símismo:
            return símismo[categ].cosos
        else:
            return []

    @property
    def nombre(símismo):
        raise NotImplementedError


class CategEc(PlantillaRamaEc):
    _cls_en_coso = CategEcCoso

    def obt_valor_res(símismo, sim, filtrar=False):
        return super().obt_valor_res(sim=sim, filtrar=filtrar)

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def eje_cosos(símismo):
        raise NotImplementedError


class SubcategEc(PlantillaRamaEc):
    _cls_en_coso = SubcategEcCoso

    def eval(símismo, paso, sim):
        for ec in símismo._ramas.values():
            res = ec.eval(paso, sim)
            if res is not None:
                if not isinstance(res, xr.DataArray):
                    res = xr.DataArray(res, coords={ec.eje_cosos: ec.cosos}, dims=[ec.eje_cosos])
                símismo.poner_valor_res(sim, res)

        símismo.postproc(paso, sim=sim)

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def eje_cosos(símismo):
        raise NotImplementedError


class Ecuación(PlantillaRamaEc):
    _cls_en_coso = EcuaciónCoso

    def __init__(símismo, modelo, mód, cosos, n_reps, ecs):
        super().__init__(modelo, mód, cosos, n_reps, ecs=ecs)
        símismo.cf = MnjdrValsCoefs(modelo, mód, símismo._ramas.values(), n_reps=n_reps)

    def act_vals(símismo):
        símismo.cf.act_vals()

    def vals_paráms(símismo):
        return símismo.cf.vals_paráms()

    def requísitos(símismo, controles=False):
        pass

    @classmethod
    def inter(símismo):
        return {tuple(prm.inter) if isinstance(prm.inter, list) else (prm.inter,)
                for prm in símismo.cls_ramas if prm.inter is not None}

    @property
    def nombre(símismo):
        raise NotImplementedError

    @property
    def eje_cosos(símismo):
        raise NotImplementedError

    def eval(símismo, paso, sim):
        raise NotImplementedError


class EcuaciónVacía(Ecuación):
    nombre = 'Nada'
    eje_cosos = None

    def eval(símismo, paso, sim):
        pass


class Parám(PlantillaRamaEc):
    _cls_en_coso = ParámCoso
    eje_cosos = None
    cls_ramas = []

    # Éstos se pueden personalizar
    líms = (None, None)
    inter = None
    apriori = None

    def __init__(símismo, modelo, mód, cosos, n_reps, ecs):
        símismo._prms_cosos = ecs
        super().__init__(modelo, mód, cosos, n_reps, ecs=ecs)

    def obt_inter(símismo, modelo, mód, coso):
        if símismo.inter:
            return mód.inter(modelo, coso=coso, tipo=símismo.inter)

    def gen_matr_parám(símismo, modelo, mód, n_reps):
        l_prms = []
        for coso, prm_cs in zip(símismo.cosos, símismo._prms_cosos):
            inters = símismo.obt_inter(modelo, mód=mód, coso=coso)
            if not inters:
                vals = ValsParámCoso(tmñ=n_reps, prm_base=prm_cs, índice=coso)
            else:
                vals = ValsParámCosoInter([
                    ValsParámCoso(
                        tmñ=n_reps, prm_base=prm_cs, índice=inter, inter=inter.índices_inter
                    ) for inter in inters
                ], eje=inters.eje, índice=coso)

            l_prms.append(vals)
        return MatrParám(l_prms, eje=mód.eje_coso, índice=None)

    @classmethod
    def para_coso(cls, coso):
        return cls._cls_en_coso(cls, coso)

    @property
    def unids(símismo):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
