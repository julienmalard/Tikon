import tikon0.RAE.Insecto as Ins
import tikon0.RAE.Planta as Plt
from tikon0.RAE.RedAE import Red

proyecto = 'Opisina_arenosella'


def gen_red(nombre=None, araña=False):
    Coco = Plt.Hojas('Coco', proyecto=proyecto)
    Ins.Sencillo('Araña', proyecto=proyecto)

    O_arenosella = Ins.MetamCompleta('O. arenosella', proyecto=proyecto, njuvenil=5)

    Parasitoide_larvas = Ins.Parasitoide('Parasitoide larvas', proyecto=proyecto)

    Parasitoide_pupa = Ins.Parasitoide('Parasitoide pupas', proyecto=proyecto)

    O_arenosella.secome(Coco, etps_depred='juvenil')

    Parasitoide_larvas.parasita(O_arenosella, etps_infec=['juvenil_1', 'juvenil_2', 'juvenil_3'], etp_sale='juvenil_5')

    Parasitoide_pupa.parasita(O_arenosella, etps_infec=['pupa'], etp_sale='pupa')

    if not araña:
        if nombre is None:
            nombre = 'Red coco'

        Red_coco = Red(nombre=nombre, organismos=[O_arenosella, Parasitoide_larvas, Parasitoide_pupa, Coco],
                       proyecto=proyecto)
        return Red_coco
    else:
        Araña = Ins.Sencillo('Araña', proyecto=proyecto)

        Araña.secome(O_arenosella, etps_presa=['juvenil', 'adulto'])
        Araña.secome(Parasitoide_pupa, etps_presa=['adulto'])
        Araña.secome(Parasitoide_larvas, etps_presa=['adulto'])

        if nombre is None:
            nombre = 'Red coco araña'

        Red_coco_araña = Red(nombre=nombre, proyecto=proyecto,
                             organismos=[O_arenosella, Parasitoide_larvas, Parasitoide_pupa, Araña, Coco])

        return Red_coco_araña
