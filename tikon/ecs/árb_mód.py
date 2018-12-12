import numpy as np

from .paráms import MnjdrValsCoefs, MatrParám
from .árb_coso import ÁrbolEcsCoso, CategEcCoso, SubcategEcCoso, EcuaciónCoso, ParámCoso


class PlantillaRamaEc(object):
    cls_ramas = []
    nombre = NotImplemented
    _cls_en_coso = NotImplemented
    _nombre_res = NotImplemented

    def __init__(símismo, cosos, í_cosos, mód, n_rep, ecs=None):
        if ecs is None:
            ecs = [coso.ecs for coso in cosos]

        símismo.cosos = cosos
        símismo.í_cosos = í_cosos or np.arange(len(cosos))
        símismo.mód = mód
        símismo._ramas = {}

        for rm in símismo.cls_ramas:
            activos = símismo._ramas_activas([ec[rm.nombre] for ec in ecs])
            if activos:
                í_cosos_rm, ecs_rm = activos
                cosos_rm = [cs for í, cs in enumerate(cosos) if í in í_cosos_rm]
                símismo._ramas[rm.nombre] = rm(cosos_rm, í_cosos_rm, mód, n_rep, ecs=ecs_rm)

    def vals_paráms(símismo):
        return [pr for rm in símismo for pr in rm.vals_paráms()]

    def eval(símismo, paso):
        for rm in símismo._ramas.values():
            rm.eval(paso)

    @staticmethod
    def _ramas_activas(ramas_ecs):
        activos = [(i, rm) for i, rm in enumerate(ramas_ecs) if rm.verificar_activa()]
        return list(zip(*activos))

    @classmethod
    def para_coso(cls):
        return cls._cls_en_coso(cls, [c.para_coso() for c in cls.cls_ramas])

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
                símismo.mód.poner_valor(res, símismo._nombre_res, índs={'etapas': ec.í_cosos})


class Ecuación(PlantillaRamaEc):
    _cls_en_coso = EcuaciónCoso

    def __init__(símismo, cosos, í_cosos, mód, n_rep, ecs=None):
        super().__init__(cosos, í_cosos, mód, n_rep, ecs=ecs)
        símismo.cf = MnjdrValsCoefs(símismo._ramas.values(), n_reps=n_rep)

    def obt_res(símismo):
        return símismo.mód.obt_val(símismo._nombre_res)

    def obt_val_mód(símismo, var):
        return símismo.mód.obt_valor(var)

    def obt_val_extern(símismo, var, mód=None):
        símismo.mód.obt_val_extern(var, mód)

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

    def __init__(símismo, cosos, í_cosos, mód, n_rep, ecs=None):
        símismo._prms_cosos = ecs
        super().__init__(cosos, í_cosos, mód, n_rep, ecs=ecs)

    @classmethod
    def para_coso(cls):
        return cls._cls_en_coso(cls)

    def vals_paráms(símismo):
        return [val for cs in símismo.cosos for val in cs.vals_paráms]

    def gen_matr_parám(símismo, n_rep):
        return MatrParám([prm.gen_matr_parám(n_rep) for prm in símismo._prms_cosos])
