import numpy as np

from .paráms import MnjdrValsCoefs, MatrParám, ValsParámCoso, ValsParámCosoInter, MatrParámCoso
from .árb_coso import ÁrbolEcsCoso, CategEcCoso, SubcategEcCoso, EcuaciónCoso, ParámCoso


class PlantillaRamaEc(object):
    cls_ramas = []
    nombre = NotImplemented
    _cls_en_coso = NotImplemented
    _nombre_res = NotImplemented
    _eje_cosos = NotImplemented
    req_todas_ramas = False

    def __init__(símismo, cosos, sim, n_rep, í_cosos, ecs):

        símismo.cosos = cosos
        símismo.í_cosos = í_cosos
        símismo.sim = sim
        símismo._ramas = {}

        for rm in símismo.cls_ramas:
            ramas_ecs = [ec[rm.nombre] for ec in ecs]
            activos = [
                (i, rm_ec) for i, rm_ec in enumerate(ramas_ecs) if rm_ec.verificar_activa(sim)
            ]
            activos = list(zip(*activos))
            if activos:
                í_cosos_rm, ecs_rm = activos
                cosos_rm = [cs for í, cs in enumerate(cosos) if í in í_cosos_rm]
                símismo._ramas[rm.nombre] = rm(cosos_rm, í_cosos_rm, sim, n_rep, ecs=ecs_rm)

    def vals_paráms(símismo):
        return [pr for rm in símismo for pr in rm.vals_paráms()]

    def eval(símismo, paso):
        for rm in símismo:
            rm.eval(paso)

        símismo.postproc(paso)

    def postproc(símismo, paso):
        pass

    def act_vals(símismo):
        for rm in símismo:
            rm.act_vals()

    def obt_res(símismo, filtrar=True):
        return símismo.obt_val_mód(símismo._nombre_res, filtrar=filtrar)

    def obt_val_mód(símismo, var, filtrar=True):
        res = símismo.sim.obt_res(var)

        índs = {símismo._eje_cosos: símismo.cosos} if filtrar else None

        return res.obt_valor(índs)

    def poner_val_res(símismo, val, rel=False, índs=None):
        res = símismo.sim.obt_res(símismo._nombre_res)
        res.poner_valor(val, rel=rel, índs=índs)
        # para hacer: ¡filtrar!

    def poner_val_mód(símismo, var, val, rel=False, filtrar=True):
        res = símismo.sim.obt_res(var)
        res.poner_valor(val, rel=rel, índs={símismo._eje_cosos: símismo.cosos} if filtrar else None)

    def í_eje(símismo, var, eje):
        return símismo.sim.obt_res(var).í_eje(eje)

    def í_eje_res(símismo, eje):
        return símismo.í_eje(símismo._nombre_res, eje=eje)

    def obt_val_extern(símismo, var, mód=None):
        return símismo.sim.obt_val_extern(var, mód)

    def obt_val_control(símismo, var):
        return símismo.sim.obt_val_control(var)

    @classmethod
    def para_coso(cls, coso):
        return cls._cls_en_coso(cls, [c.para_coso(coso) for c in cls.cls_ramas], coso=coso)

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

    def __init__(símismo, cosos, sim, n_rep):
        super().__init__(cosos, sim, n_rep, í_cosos=np.arange(len(cosos)), ecs=[coso.ecs for coso in cosos])

    def cosos_en_categ(símismo, categ):
        if categ in símismo:
            return símismo[categ].cosos
        else:
            return []


class CategEc(PlantillaRamaEc):
    _cls_en_coso = CategEcCoso


class SubcategEc(PlantillaRamaEc):
    _cls_en_coso = SubcategEcCoso
    auto = None

    def eval(símismo, paso):
        for ec in símismo._ramas.values():
            res = ec.eval(paso)
            if res is not None:
                símismo.poner_val_res(res, índs={símismo._eje_cosos: ec.cosos})

        símismo.postproc(paso)


class Ecuación(PlantillaRamaEc):
    _cls_en_coso = EcuaciónCoso

    def __init__(símismo, cosos, sim, n_rep, í_cosos, ecs):
        super().__init__(cosos, sim, n_rep, í_cosos, ecs=ecs)
        símismo.cf = MnjdrValsCoefs(símismo._ramas.values(), n_reps=n_rep)

    def act_vals(símismo):
        símismo.cf.act_vals()

    def vals_paráms(símismo):
        return símismo.cf.vals_paráms()

    @classmethod
    def inter(símismo):
        return {tuple(prm.inter) if isinstance(prm.inter, list) else (prm.inter,)
                for prm in símismo.cls_ramas if prm.inter is not None}

    def eval(símismo, paso):
        raise NotImplementedError


class EcuaciónVacía(Ecuación):
    nombre = 'Nada'

    def eval(símismo, paso):
        pass


class Parám(PlantillaRamaEc):
    _cls_en_coso = ParámCoso
    líms = (None, None)
    unids = None
    inter = None
    cls_ramas = []

    def __init__(símismo, cosos, sim, n_rep, í_cosos, ecs):
        símismo._prms_cosos = ecs
        super().__init__(cosos, sim, n_rep, í_cosos, ecs=ecs)

    def obt_inter(símismo, coso):
        if símismo.inter is not None:
            return símismo.sim.inter(coso=coso, tipo=símismo.inter)

    def gen_matr_parám(símismo, n_rep):
        l_prms = []
        for coso, prm_cs in zip(símismo.cosos, símismo._prms_cosos):
            inters = símismo.obt_inter(coso)
            if inters is None:
                vals = ValsParámCoso(tmñ=n_rep, prm_base=prm_cs)
            else:
                vals = ValsParámCosoInter({
                    í: ValsParámCoso(tmñ=n_rep, prm_base=prm_cs, inter=inter)
                    for í, inter in inters
                }, tmñ_inter=inters.tmñ)

            l_prms.append(MatrParámCoso(vals))
        return MatrParám(l_prms)

    @classmethod
    def para_coso(cls, coso):
        return cls._cls_en_coso(cls, coso)
