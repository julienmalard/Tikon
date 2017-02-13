import tikon.RAE.Insecto as Ins
from tikon.Experimentos import Experimento
from tikon.Proyectos.Opisina_arenosella.a_prioris import a_prioris
from tikon.RAE.RedAE import Red

# Opciones artísticas
dib_aprioris = False
ops_dib = {'incert': None, 'todas_líneas': True}

# Empezamos las cosas serias ahora
proyecto = 'Opisina_arenosella'
"""
O_arenosella_senc = Ins.Sencillo(nombre='O. arenosella_senc', proyecto=proyecto)
Parasitoide_senc = Ins.Sencillo(nombre='Parasitoide_senc', proyecto=proyecto)

# Datos de desnsidad de coco: Agricultural Ecology and Environment, pg 321 +
# https://books.google.com.gt/books?id=0gjoQ0OTpAYC&pg=PA318&lpg=PA318&dq=coconut+field+leaf+area&source=bl&ots=I9GJ8L88y2&sig=t0LUc7kUPDyDlniDdoipiYx84uU&hl=en&sa=X&ved=0ahUKEwiKqcqs_Y7OAhXLlB4KHSOrBAAQ6AEIMDAC#v=onepage&q=coconut%20field%20leaf%20area&f=false
Coco = Plt.Constante(nombre='Palma de coco', densidad=40020e6, proyecto=proyecto)  # Unidades: mm2 / ha


O_arenosella_senc.secome(Coco)
Parasitoide_senc.secome(O_arenosella_senc)

Red_coco_senc = Red('Campos coco sencillo', organismos=[Coco, O_arenosella_senc, Parasitoide_senc],
                    proyecto=proyecto)
Red_coco_senc.guardar()
"""
Experimento_A = Experimento(nombre='Sitio A', proyecto=proyecto)
Experimento_A.agregar_orgs(archivo='Oarenosella_A.csv', col_tiempo='Día', factor=655757.1429/500)

Experimento_B = Experimento(nombre='Sitio B', proyecto=proyecto)
Experimento_B.agregar_orgs(archivo='Oarenosella_B.csv', col_tiempo='Día', factor=655757.1429/500)
"""
Red_coco_senc.añadir_exp(Experimento_A,
                         corresp={'O. arenosella_senc': {'adulto': ['Larva', 'Pupa']},
                                  'Parasitoide_senc': {'adulto': ['Para_larva_abs', 'Para_pupa_abs']}
                                  }
                         )

Red_coco_senc.añadir_exp(Experimento_B,
                         corresp={'O. arenosella_senc': {'adulto': ['Estado 1', 'Estado 2', 'Estado 3', 'Estado 4',
                                                                    'Estado 5', 'Pupa']}
                                  }
                         )


ajuste_inic = Red_coco_senc.validar(exper=Experimento_A, n_rep_parám=40, n_rep_estoc=40)
print('Ajuste inicial: ', ajuste_inic)


# Intentar calibrar
Red_coco_senc.calibrar(nombre='Sin a priori', exper=Experimento_A, n_iter=500, quema=10)
Red_coco_senc.validar(exper=Experimento_A)
Red_coco_senc.validar(exper=Experimento_B)
Red_coco_senc.guardar_calib(descrip='Calibración de red sencilla (oruga y parasitoide) para O. arenosella en coco, '
                                    'sin usar a prioris. Se aplicó el sitio A de Perera et al. para la calibración.',
                            utilizador='Julien Malard',
                            contacto='julien.malard@mail.mcgill.ca')
Red_coco_senc.guardar()


# Especificar distribuciones a priori
for a_priori in a_prioris[O_arenosella_senc.nombre]:
    O_arenosella_senc.especificar_apriori(dibujar=dib_aprioris, **a_priori)

for a_priori in a_prioris[Parasitoide_senc.nombre]:
    Parasitoide_senc.especificar_apriori(dibujar=dib_aprioris, **a_priori)


# Verificar el modelo ahora
ajuste_con_aprioris = Red_coco_senc.validar(exper=Experimento_A, n_rep_parám=40, n_rep_estoc=40)
print('Ajuste con a priosis: ', ajuste_con_aprioris)

# Intentar calibrar de nuevo
Red_coco_senc.calibrar('Con aprioris', exper=Experimento_A, n_iter=100, quema=10, extraer=1,
                       dibujar=True)
Red_coco_senc.validar(exper=Experimento_A, n_rep_estoc=5, n_rep_parám=5, opciones_dib=ops_dib)
Red_coco_senc.validar(exper=Experimento_B, n_rep_estoc=5, n_rep_parám=5, opciones_dib=ops_dib)
Red_coco_senc.guardar_calib(descrip='Calibración de red sencilla (oruga y parasitoide) para O. arenosella en coco, '
                                    'empleando a prioris.'
                                    'Se aplicó el sitio A de Perera et al. para la calibración.',
                            utilizador='Julien Malard',
                            contacto='julien.malard@mail.mcgill.ca')
Red_coco_senc.guardar()
"""
# Bueno, ahora vamos a ver con una estructura de red más compleja (agregando un depredador generalista)
Araña = Ins.Sencillo('Araña', proyecto=proyecto)
"""
Araña.secome(O_arenosella_senc)
Araña.secome(Parasitoide_senc)

for a_priori in a_prioris[Araña.nombre]:
    Araña.especificar_apriori(dibujar=dib_aprioris, **a_priori)

Red_coco_senc.añadir_org(Araña)

Red_coco_senc.validar(exper=Experimento_A, n_rep_parám=40, n_rep_estoc=40)

Red_coco_senc.calibrar(nombre='Con araña', exper=Experimento_A, n_iter=1000, quema=100, extraer=10,
                       dibujar=True)
Red_coco_senc.validar(exper=Experimento_A)
Red_coco_senc.validar(exper=Experimento_B)
Red_coco_senc.guardar_calib(descrip='Calibración de red sencilla (oruga y parasitoide) para O. arenosella en coco, '
                                    'empleando a prioris.'
                                    'Se aplicó el sitio A de Perera et al. para la calibración.',
                            utilizador='Julien Malard',
                            contacto='julien.malard@mail.mcgill.ca')
Red_coco_senc.guardar()
"""

# Intentemos algo más interesante ahora.
O_arenosella = Ins.MetamCompleta('O. arenosella', njuvenil=5)

Parasitoide_larvas = Ins.Parasitoide('Parasitoide larvas')

Parasitoides_pupa = Ins.Parasitoide('Parasitoide pupas')

Parasitoide_larvas.parasita(O_arenosella, etps_infec=['juvenil_1', 'juvenil_2', 'juvenil_3'], etp_sale='juvenil_5')

Parasitoides_pupa.parasita(O_arenosella, etps_infec=['pupa'], etp_sale='pupa')

Red_coco = Red(nombre='Coco completa', organismos=[O_arenosella, Parasitoide_larvas, Parasitoides_pupa])

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
for a_priori in a_prioris[O_arenosella.nombre]:
    O_arenosella.especificar_apriori(**a_priori)

# for a_priori in a_prioris[Parasitoide_larvas.nombre]:
#     Parasitoide_larvas.especificar_apriori(**a_priori)

# for a_priori in a_prioris[Parasitoides_pupa.nombre]:
#     Parasitoides_pupa.especificar_apriori(**a_priori)


Red_coco.calibrar(exper=Experimento_A)
Red_coco.validar(Experimento_A)
Red_coco.validar(Experimento_B)

Red_coco.guardar_calib(descrip='Calibración de red completa (oruga y parasitoides) para O. arenosella en coco, '
                               'empleando a prioris.'
                               'Se aplicó el sitio A de Perera et al. para la calibración.',
                       utilizador='Julien Malard',
                       contacto='julien.malard@mail.mcgill.ca')
Red_coco.guardar()

# Ahora, con una red más compleja y con estructura completa para los insectos
Red_coco.añadir_org(Araña)

Red_coco.calibrar(nombre='Con araña', exper=Experimento_A, n_iter=100, quema=10)
Red_coco.validar(exper=Experimento_A)
Red_coco.validar(exper=Experimento_B)

Red_coco.guardar_calib(descrip='Calibración de red completa (oruga, parasitoide y araña) para O. arenosella en coco, '
                               'empleando a prioris.'
                               'Se aplicó el sitio A de Perera et al. para la calibración.',
                       utilizador='Julien Malard',
                       contacto='julien.malard@mail.mcgill.ca')
Red_coco.guardar()


# Podríamos hacer modelos más complejos con especies distintas de avispas, etc.
