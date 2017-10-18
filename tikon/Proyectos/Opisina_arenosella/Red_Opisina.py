from tikon.RAE.RedAE import Red
import tikon.RAE.Insecto as Ins
import tikon.RAE.Planta as Plt


proyecto = 'Opisina_arenosella'


Coco = Plt.Hojas('Coco', proyecto=proyecto)
Ins.Sencillo('Araña', proyecto=proyecto)

O_arenosella = Ins.MetamCompleta('O. arenosella', proyecto=proyecto, njuvenil=5)

Parasitoide_larvas = Ins.Parasitoide('Parasitoide larvas', proyecto=proyecto)

Parasitoide_pupa = Ins.Parasitoide('Parasitoide pupas', proyecto=proyecto)

O_arenosella.secome(Coco, etps_depred='juvenil')

Parasitoide_larvas.parasita(O_arenosella, etps_infec=['juvenil_1', 'juvenil_2', 'juvenil_3'], etp_sale='juvenil_5')

Parasitoide_pupa.parasita(O_arenosella, etps_infec=['pupa'], etp_sale='pupa')

Red_coco = Red(nombre='Red coco_AM', organismos=[O_arenosella, Parasitoide_larvas, Parasitoide_pupa, Coco],
               proyecto=proyecto)

Araña = Ins.Sencillo('Araña', proyecto=proyecto)

Araña.secome(O_arenosella, etps_presa=['juvenil', 'adulto'])
Araña.secome(Parasitoide_pupa, etps_presa=['adulto'])
Araña.secome(Parasitoide_larvas, etps_presa=['adulto'])

Red_coco_araña = Red(nombre='Coco araña', proyecto=proyecto,
                     organismos=[O_arenosella, Parasitoide_larvas, Parasitoide_pupa, Araña, Coco])
