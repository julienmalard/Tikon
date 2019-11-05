from .paráms import MnjdrValsCoefs, MatrParám, ValsParámCoso, ValsParámCosoInter
from .árb_coso import ÁrbolEcsCoso, CategEcCoso, SubcategEcCoso, EcuaciónCoso, ParámCoso


class PlantillaRamaEc(object):
    cls_ramas = []
    req_todas_ramas = False

    _cls_en_coso = NotImplemented
    _nombre_res = NotImplemented
    _eje_cosos = NotImplemented

    def __init__(símismo, cosos, n_reps, ecs):

        símismo.cosos = cosos
        símismo._ramas = {}

        for rm in símismo.cls_ramas:
            ramas_ecs = [ec[rm.nombre] for ec in ecs]
            activos = [rm_ec for rm_ec in ramas_ecs if rm_ec.verificar_activa(mód=mód)]
            if activos:
                í_cosos_rm, ecs_rm = activos
                cosos_rm = [cs for í, cs in enumerate(cosos) if í in í_cosos_rm]
                símismo._ramas[rm.nombre] = rm(cosos_rm, n_reps=n_reps, ecs=ecs_rm)

    def vals_paráms(símismo):
        return {pr for rm in símismo for pr in rm.vals_paráms()}

    def requísitos(símismo, controles=False):
        return {req for rm in símismo for req in rm.requísitos()}

    def eval(símismo, paso, sim):
        for rm in símismo:
            rm.eval(paso, sim=sim)

        símismo.postproc(paso, sim=sim)

    def postproc(símismo, paso, sim):
        pass

    def act_vals(símismo):
        for rm in símismo:
            rm.act_vals()

    def obt_val_res(símismo, sim, filtrar=True):
        return símismo.obt_val_mód(sim, var=símismo._nombre_res, filtrar=filtrar)

    def obt_val_mód(símismo, sim, var, filtrar=True):
        if filtrar:
            return sim.obt_valor(var).loc[{símismo._eje_cosos: símismo.cosos}]
        return sim.obt_valor(var)

    def poner_val_res(símismo, sim, val, rel=False):
        sim.poner_valor(símismo._nombre_res, val=val, rel=rel)

    @staticmethod
    def poner_val_mód(sim, var, val, rel=False):
        sim.poner_valor(var, val, rel=rel)

    @staticmethod
    def obt_val_extern(sim, var, mód=None):
        if not mód:
            mód, var = var.split('.')
        return sim.simul_exper[mód].obt_valor(var)

    @staticmethod
    def obt_val_control(sim, var):
        return sim.exper.controles[var]

    @classmethod
    def para_coso(cls, coso):
        return cls._cls_en_coso(cls, [c.para_coso(coso) for c in cls.cls_ramas], coso=coso)

    @property
    def nombre(símismo):
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

    def __init__(símismo, cosos, n_reps):
        super().__init__(cosos, n_reps=n_reps, ecs=[coso.ecs for coso in cosos])

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

    def obt_val_res(símismo, sim, filtrar=False):
        return super().obt_val_res(sim=sim, filtrar=filtrar)

    @property
    def nombre(símismo):
        raise NotImplementedError


class SubcategEc(PlantillaRamaEc):
    _cls_en_coso = SubcategEcCoso

    def eval(símismo, paso, sim):
        for ec in símismo._ramas.values():
            res = ec.eval(paso)
            if res is not None:
                símismo.poner_val_res(sim, res)

        símismo.postproc(paso, sim=sim)

    @property
    def nombre(símismo):
        raise NotImplementedError


class Ecuación(PlantillaRamaEc):
    _cls_en_coso = EcuaciónCoso

    def __init__(símismo, cosos, n_reps, ecs):
        super().__init__(cosos, n_reps, ecs=ecs)
        símismo.cf = MnjdrValsCoefs(símismo._ramas.values(), n_reps=n_reps)

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

    def eval(símismo, paso, sim):
        raise NotImplementedError


class EcuaciónVacía(Ecuación):
    nombre = 'Nada'

    def eval(símismo, paso, sim):
        pass


class Parám(PlantillaRamaEc):
    _cls_en_coso = ParámCoso
    líms = (None, None)
    inter = None
    cls_ramas = []
    apriori = None

    def __init__(símismo, cosos, n_reps, ecs):
        símismo._prms_cosos = ecs
        super().__init__(cosos, n_reps, ecs=ecs)

    def obt_inter(símismo, sim, coso):
        if símismo.inter:
            return sim.inter(coso=coso, tipo=símismo.inter)

    def gen_matr_parám(símismo, sim, n_reps):
        l_prms = []
        for coso, prm_cs in zip(símismo.cosos, símismo._prms_cosos):
            inters = símismo.obt_inter(sim=sim, coso=coso)
            if not inters:
                vals = ValsParámCoso(tmñ=n_reps, prm_base=prm_cs, índice=coso)
            else:
                vals = ValsParámCosoInter([
                    ValsParámCoso(tmñ=n_reps, prm_base=prm_cs, índice=inter[-1], inter=inter) for inter in inters
                ], eje=inters.eje, índice=coso)

            l_prms.append(vals)
        return MatrParám(l_prms, eje=eje_coso, índice=None)

    @classmethod
    def para_coso(cls, coso):
        return cls._cls_en_coso(cls, coso)

    @property
    def unids(símismo):
        raise NotImplementedError

    @property
    def nombre(símismo):
        raise NotImplementedError
