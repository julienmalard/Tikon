from pprint import pprint

import tikon.RAE.Insecto as Ins
from tikon.Matemáticas.Experimentos import Experimento
from tikon.Proyectos.Opisina_arenosella.a_prioris import a_prioris
from tikon.RAE.Planta import Hojas
from tikon.RAE.RedAE import Red

# Opciones artísticas
dibujar = True
ops_dib = {'n_líneas': 5}

# Empezamos las cosas serias ahora
proyecto = 'Opisina_arenosella'

método = 'mle'
n_iter = 100
quema = 0
extraer = 1
pedazitos = 1
n_rep_estoc = 30
n_rep_parám = 30

O_arenosella_senc = Ins.Sencillo(nombre='O. arenosella_senc', proyecto=proyecto)
Parasitoide_senc = Ins.Sencillo(nombre='Parasitoide_senc', proyecto=proyecto)

# Datos de desnsidad de coco: Agricultural Ecology and Environment, pg 321 +
# https://books.google.com.gt/books?id=0gjoQ0OTpAYC&pg=PA318&lpg=PA318&dq=coconut+field+leaf+area&source=bl&ots=I9GJ8L88y2&sig=t0LUc7kUPDyDlniDdoipiYx84uU&hl=en&sa=X&ved=0ahUKEwiKqcqs_Y7OAhXLlB4KHSOrBAAQ6AEIMDAC#v=onepage&q=coconut%20field%20leaf%20area&f=false
Coco = Hojas(nombre='Palma de coco', proyecto=proyecto)  # Unidades: mm2 / ha
Coco.estimar_densidad(rango=(38, 42), certidumbre=0.95)

# O_arenosella_senc.secome(Coco)
# Parasitoide_senc.secome(O_arenosella_senc)
#
# Red_coco_senc = Red('Campos coco sencillo', organismos=[Coco, O_arenosella_senc, Parasitoide_senc],
#                     proyecto=proyecto)
# Red_coco_senc.guardar()
#
Experimento_A = Experimento(nombre='Sitio A', proyecto=proyecto)
Experimento_A.agregar_pobs(archivo='Oarenosella_A.csv', col_tiempo='Día', factor=655757.1429 / 500)

Experimento_B = Experimento(nombre='Sitio B', proyecto=proyecto)
Experimento_B.agregar_pobs(archivo='Oarenosella_B.csv', col_tiempo='Día', factor=655757.1429 / 500)
#
# Red_coco_senc.añadir_exp(Experimento_A,
#                          corresp={'O. arenosella_senc': {'adulto': ['Larva', 'Pupa']},
#                                   'Parasitoide_senc': {'adulto': ['Para_larva_abs', 'Para_pupa_abs']}
#                                   }
#                          )
#
# Red_coco_senc.añadir_exp(Experimento_B,
#                          corresp={'O. arenosella_senc': {'adulto': ['Estado 1', 'Estado 2', 'Estado 3', 'Estado 4',
#                                                                     'Estado 5', 'Pupa']}
#                                   }
#                          )
#
# # Intentar calibrar
# ajuste_inic = Red_coco_senc.validar(
#     nombre='senc Sitio A, Antes de calibrar', exper=Experimento_A, dibujar=dibujar, n_rep_estoc=n_rep_estoc,
#     n_rep_parám=n_rep_parám, dib_dists=dibujar
# )
# print('Ajuste inicial: ')
# pprint(ajuste_inic)
#
# Red_coco_senc.calibrar(
#     nombre='Sin a priori', exper=Experimento_A, n_iter=n_iter, quema=quema, extraer=extraer, n_rep_estoc=n_rep_estoc,
#     dibujar=dibujar, método=método, pedazitos=pedazitos
# )
# vld = Red_coco_senc.validar(nombre='senc Sitio A, con calibración', exper=Experimento_A, dibujar=dibujar,
#                             n_rep_estoc=n_rep_estoc,
#                             n_rep_parám=n_rep_parám,
#                             dib_dists=dibujar)
# print('Sencilla, sitio A con calib sin AP\n********************')
# pprint(vld)
#
# vld = Red_coco_senc.validar(
#     nombre='senc Sitio B, con calibración', exper=Experimento_B, dibujar=dibujar, n_rep_estoc=n_rep_estoc,
#     n_rep_parám=n_rep_parám,
#     dib_dists=dibujar)
# print('Sencilla, sitio B con calib sin AP\n********************')
# pprint(vld)
#
# Red_coco_senc.guardar_calib(descrip='Calibración de red sencilla (oruga y parasitoide) para O. arenosella en coco, '
#                                     'sin usar a prioris. Se aplicó el sitio A de Perera et al. para la calibración.',
#                             utilizador='Julien Malard',
#                             contacto='julien.malard@mail.mcgill.ca')
# Red_coco_senc.guardar()
#
# # Especificar distribuciones a priori
# for a_priori in a_prioris[O_arenosella_senc.nombre]:
#     O_arenosella_senc.especificar_apriori(dibujar=dibujar, **a_priori)
#
# for a_priori in a_prioris[Parasitoide_senc.nombre]:
#     Parasitoide_senc.especificar_apriori(dibujar=dibujar, **a_priori)
#
# # Verificar el modelo ahora
# ajuste_con_aprioris = Red_coco_senc.validar(
#     exper=Experimento_A, nombre='senc Sitio A, ajust con aprioris', n_rep_estoc=n_rep_estoc, n_rep_parám=n_rep_parám
# )
# print('Ajuste con a prioris\n********************')
# pprint(ajuste_con_aprioris)
#
# # Intentar calibrar de nuevo
# vld = Red_coco_senc.validar(nombre='senc Sitio A, con a prioris', exper=Experimento_A, opciones_dib=ops_dib,
#                             n_rep_estoc=n_rep_estoc,
#                             n_rep_parám=n_rep_parám,
#                             dibujar=dibujar,
#                             dib_dists=dibujar)
# print('Sencilla, antes calib\n********************')
# pprint(vld)
# Red_coco_senc.calibrar('senc Con aprioris', exper=Experimento_A, n_iter=n_iter, quema=quema, extraer=extraer,
#                        n_rep_estoc=n_rep_estoc,
#                        dibujar=dibujar, método=método, pedazitos=pedazitos)
#
# vld = Red_coco_senc.validar(nombre='senc Sitio A, con calib a prioris', exper=Experimento_A, opciones_dib=ops_dib,
#                             n_rep_estoc=n_rep_estoc,
#                             n_rep_parám=n_rep_parám,
#                             dibujar=dibujar, dib_dists=dibujar)
# print('Sencilla, sitio A con calib\n********************')
# pprint(vld)
#
# vld = Red_coco_senc.validar(nombre='senc Sitio B, con calib a prioris', exper=Experimento_B, opciones_dib=ops_dib,
#                             n_rep_estoc=n_rep_estoc,
#                             n_rep_parám=n_rep_parám,
#                             dibujar=dibujar, dib_dists=dibujar)
# print('Sencilla, sitio B con calib\n********************')
# pprint(vld)
#
# Red_coco_senc.guardar_calib(descrip='Calibración de red sencilla (oruga y parasitoide) para O. arenosella en coco, '
#                                     'empleando a prioris.'
#                                     'Se aplicó el sitio A de Perera et al. para la calibración.',
#                             utilizador='Julien Malard',
#                             contacto='julien.malard@mail.mcgill.ca')
# Red_coco_senc.guardar()
#
# # Bueno, ahora vamos a ver con una estructura de red más compleja (agregando un depredador generalista)
Araña = Ins.Sencillo('Araña', proyecto=proyecto)

Araña.secome(O_arenosella_senc)
Araña.secome(Parasitoide_senc)

for a_priori in a_prioris[Araña.nombre]:
    Araña.especificar_apriori(dibujar=dibujar, **a_priori)

# Red_coco_senc.añadir_org(Araña)
#
# vld = Red_coco_senc.validar(nombre='senc Sitio A, con araña y ap', exper=Experimento_A, dibujar=dibujar,
#                             n_rep_estoc=n_rep_estoc,
#                             n_rep_parám=n_rep_parám,
#                             )
# print('Sencilla + araña, antes calib\n********************')
# pprint(vld)
#
# Red_coco_senc.calibrar(nombre='senc Con araña y ap', exper=Experimento_A, n_iter=n_iter, quema=quema, extraer=extraer,
#                        dibujar=dibujar, método=método, pedazitos=pedazitos, n_rep_estoc=n_rep_estoc)
#
# vld = Red_coco_senc.validar(nombre='senc Sitio A, con araña y calib', exper=Experimento_A, n_rep_estoc=n_rep_estoc,
#                             n_rep_parám=n_rep_parám, dibujar=dibujar,
#                             dib_dists=dibujar)
# print('Sencilla + araña, sitio A con calib\n********************')
# pprint(vld)
#
# vld = Red_coco_senc.validar(nombre='senc Sitio B, con araña y calib', exper=Experimento_B, n_rep_estoc=n_rep_estoc,
#                             n_rep_parám=n_rep_parám, dibujar=dibujar,
#                             dib_dists=dibujar)
# print('Sencilla + araña, sitio B con calib\n********************')
# pprint(vld)
#
# Red_coco_senc.guardar_calib(descrip='Calibración de red sencilla (oruga y parasitoide) para O. arenosella en coco, '
#                                     'empleando a prioris.'
#                                     'Se aplicó el sitio A de Perera et al. para la calibración.',
#                             utilizador='Julien Malard',
#                             contacto='julien.malard@mail.mcgill.ca')
# Red_coco_senc.guardar()
#
# del Red_coco_senc

# Intentemos algo más interesante ahora.
O_arenosella = Ins.MetamCompleta('O. arenosella', proyecto=proyecto, njuvenil=5)

Parasitoide_larvas = Ins.Parasitoide('Parasitoide larvas', proyecto=proyecto)

Parasitoide_pupa = Ins.Parasitoide('Parasitoide pupas', proyecto=proyecto)

O_arenosella.secome(Coco, etps_depred='juvenil')

Parasitoide_larvas.parasita(O_arenosella, etps_infec=['juvenil_1', 'juvenil_2', 'juvenil_3'], etp_sale='juvenil_5')

Parasitoide_pupa.parasita(O_arenosella, etps_infec=['pupa'], etp_sale='pupa')

Red_coco = Red(nombre='Red coco', organismos=[O_arenosella, Parasitoide_larvas, Parasitoide_pupa, Coco],
               proyecto=proyecto)

Red_coco.añadir_exp(Experimento_A,
                    corresp={'O. arenosella': {'juvenil_1': ['Estado 1'],
                                               'juvenil_2': ['Estado 2'],
                                               'juvenil_3': ['Estado 3'],
                                               'juvenil_4': ['Estado 4'],
                                               'juvenil_5': ['Estado 5'],
                                               'pupa': ['Pupa']},
                             'Parasitoide larvas': {'juvenil': ['Para_larva_abs']},
                             'Parasitoide pupas': {'juvenil': ['Para_pupa_abs']}}
                    )

Red_coco.añadir_exp(Experimento_B,
                    corresp={'O. arenosella': {'juvenil_1': ['Estado 1'],
                                               'juvenil_2': ['Estado 2'],
                                               'juvenil_3': ['Estado 3'],
                                               'juvenil_4': ['Estado 4'],
                                               'juvenil_5': ['Estado 5'],
                                               'pupa': ['Pupa']}}
                    )

# A prioris para la nueva red
for org in [O_arenosella, Parasitoide_larvas, Parasitoide_pupa]:
    try:
        for a_priori in a_prioris[org.nombre]:
            org.especificar_apriori(dibujar=dibujar, **a_priori)
    except KeyError:
        pass

pprint(Red_coco.ver_coefs_no_espec())

vld = Red_coco.validar(exper=Experimento_A, nombre='Sitio A, antes calib', usar_especificadas=True, dibujar=dibujar,
                       n_rep_estoc=n_rep_estoc,
                       n_rep_parám=n_rep_parám,
                       dib_dists=dibujar)
print('Completa, antes calib\n********************')
pprint(vld)

Red_coco.calibrar(exper=Experimento_A, nombre='Sin araña', n_iter=n_iter, quema=quema, extraer=extraer,
                  n_rep_estoc=n_rep_estoc, dibujar=dibujar, método=método, pedazitos=pedazitos)

vld = Red_coco.validar(nombre='Sitio A, con calib', exper=Experimento_A, opciones_dib=ops_dib, dibujar=dibujar,
                       n_rep_estoc=n_rep_estoc,
                       n_rep_parám=n_rep_parám,
                       dib_dists=dibujar)
print('Completa, sitio A con calib\n********************')
pprint(vld)

vld = Red_coco.validar(nombre='Sitio B, con calib', exper=Experimento_B, opciones_dib=ops_dib, dibujar=dibujar,
                       n_rep_estoc=n_rep_estoc,
                       n_rep_parám=n_rep_parám,
                       dib_dists=dibujar)
print('Completa, sitio B con calib\n********************')
pprint(vld)

# Red_coco.validar(Experimento_B, n_rep_parám=10, n_rep_estoc=10)

Red_coco.guardar_calib(descrip='Calibración de red completa (oruga y parasitoides) para O. arenosella en coco, '
                               'empleando a prioris.'
                               'Se aplicó el sitio A de Perera et al. para la calibración.',
                       utilizador='Julien Malard',
                       contacto='julien.malard@mail.mcgill.ca')
Red_coco.guardar()

# Ahora, con una red más compleja y con estructura completa para los insectos
Red_coco.añadir_org(Araña)
Araña.secome(O_arenosella)
Araña.secome(Parasitoide_larvas)
Araña.secome(Parasitoide_pupa)

for a_priori in a_prioris[Araña.nombre]:
    Araña.especificar_apriori(dibujar=dibujar, **a_priori)

vld = Red_coco.validar(nombre='Sitio A, antes calib con araña', exper=Experimento_A, opciones_dib=ops_dib,
                       n_rep_estoc=n_rep_estoc,
                       n_rep_parám=n_rep_parám,
                       dibujar=dibujar, dib_dists=dibujar)
print('Completa + araña, antes calib\n********************')
pprint(vld)

Red_coco.calibrar(nombre='Con araña', exper=Experimento_A, n_iter=n_iter, quema=quema, dibujar=dibujar,
                  método=método, pedazitos=pedazitos, n_rep_estoc=n_rep_estoc)

vld = Red_coco.validar(nombre='Sitio A, con calib y araña', exper=Experimento_A, opciones_dib=ops_dib, dibujar=dibujar,
                       n_rep_estoc=n_rep_estoc,
                       n_rep_parám=n_rep_parám,
                       dib_dists=dibujar)
print('Completa + araña, sitio A con calib\n********************')
pprint(vld)

vld = Red_coco.validar(nombre='Sitio B, con calib y araña', exper=Experimento_B, opciones_dib=ops_dib, dibujar=dibujar,
                       n_rep_estoc=n_rep_estoc,
                       n_rep_parám=n_rep_parám,
                       dib_dists=dibujar)
print('Completa + araña, sitio B con calib\n********************')
pprint(vld)

Red_coco.guardar_calib(descrip='Calibración de red completa (oruga, parasitoide y araña) para O. arenosella en coco, '
                               'empleando a prioris.'
                               'Se aplicó el sitio A de Perera et al. para la calibración.',
                       utilizador='Julien Malard',
                       contacto='julien.malard@mail.mcgill.ca')
Red_coco.guardar()

# Podríamos hacer modelos más complejos con especies distintas de avispas, etc.
