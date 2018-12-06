from tikon.ecs.paráms import MnjdrParáms
from .árb_coso import ÁrbolEcsCoso, CategEcCoso, SubcategEcCoso, EcuaciónCoso


class PlantillaRamaEc(object):
    _cls_ramas = []
    _cls_en_coso = NotImplemented
    nombre = NotImplemented

    def __init__(símismo, cosos, í_cosos, mnjdr_móds):
        símismo._í_cosos = í_cosos
        símismo.mnjdr_móds = mnjdr_móds
        símismo._ramas = {}

        for rm in símismo._cls_ramas:
            activos = _cosos_activos(cosos, rm)
            if len(activos):
                símismo._ramas[rm.nombre] = rm(*activos, mnjdr_móds)

    @classmethod
    def para_coso(cls):
        return cls._cls_en_coso(cls, [c.para_coso() for c in cls._cls_ramas])

    def __call__(símismo, paso):
        for rm in símismo._ramas.values():
            rm(paso)

    def __getitem__(símismo, itema):
        return símismo._ramas[itema]

    def __str__(símismo):
        return símismo.nombre


class ÁrbolEcs(PlantillaRamaEc):
    _cls_en_coso = ÁrbolEcsCoso


class CategEc(PlantillaRamaEc):
    _cls_en_coso = CategEcCoso


class SubcategEc(PlantillaRamaEc):
    _cls_en_coso = SubcategEcCoso
    auto = None

    def __call__(símismo, paso):
        for ec in símismo._ramas.values():
            símismo._res.poner_val(ec(paso), índs=símismo._í_cosos)


class Ecuación(PlantillaRamaEc):
    _cls_en_coso = EcuaciónCoso

    def __init__(símismo, cosos, í_cosos, mnjdr_móds):
        super().__init__(cosos, í_cosos, mnjdr_móds)

        símismo.cf = MnjdrParáms(cosos, símismo._ramas)

    def __call__(símismo, paso):
        raise NotImplementedError


class EcuaciónVacía(Ecuación):
    nombre = 'Vacía'

    def __call__(símismo, paso):
        pass


def _cosos_activos(cosos, cls_rama):
    activos = [(i, c) for i, c in enumerate(cosos) if c.verificar_activa(cls_rama)]
    return list(zip(*activos))
