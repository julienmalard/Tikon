from tikon.ecs.árb_mód import ÁrbolEcs, CategEc, SubcategEc, Ecuación, Parám, EcuaciónVacía


class ParámAPriori(Parám):
    pass


class ParámInter(Parám):
    pass


class Parám0aInf(Parám):
    nombre = '0 a inf'
    unids = 'm2'
    líms = (0, None)


class ParámSinLíms(Parám):
    nombre = 'Sin líms'
    unids = 'm2'
    líms = None


class ParámInfa0(Parám):
    nombre = 'Inf a 0'
    unids = 'm2'
    líms = (None, 0)


class Parám0a2(Parám):
    nombre = '0 a 2'
    unids = 'm2'
    líms = (0, 2)


class EcuaciónSencilla(Ecuación):
    nombre = 'Sencilla'


class EcuaciónReqs(Ecuación):
    nombre = 'Requísitos'


class SubcategEc1a(SubcategEc):
    nombre = '1a'
    cls_ramas = [EcuaciónVacía, EcuaciónSencilla]


class SubcategEc1b(SubcategEc):
    nombre = '1b'
    cls_ramas = [EcuaciónVacía]


class SubcategEc2a(SubcategEc):
    nombre = '2a'
    cls_ramas = [EcuaciónVacía]


class SubcategEc2b(SubcategEc):
    nombre = '2b'
    cls_ramas = [EcuaciónVacía]


class CategEc1(CategEc):
    nombre = '1'
    cls_ramas = [SubcategEc1a, SubcategEc1b]


class CategEc2(CategEc):
    nombre = '2'
    cls_ramas = [SubcategEc2a, SubcategEc2b]


class EjÁrbol(ÁrbolEcs):
    nombre = 'Prueba'
    cls_ramas = [CategEc1, CategEc2]
