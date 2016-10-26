import RAE.NuevoInsecto as Ins
import RAE.Planta as Plt
from Matemáticas.Experimentos import Experimento
from RAE.NuevaRedAE import Red

proyecto = 'Opisina arenosella'
O_arenosella_senc = Ins.Sencillo(nombre='O. arenosella_senc', proyecto=proyecto)
Parasitoide_senc = Ins.Sencillo(nombre='Parasitoide_senc', proyecto=proyecto)

# Datos de desnsidad de coco: Agricultural Ecology and Environment, pg 321 +
# https://books.google.com.gt/books?id=0gjoQ0OTpAYC&pg=PA318&lpg=PA318&dq=coconut+field+leaf+area&source=bl&ots=I9GJ8L88y2&sig=t0LUc7kUPDyDlniDdoipiYx84uU&hl=en&sa=X&ved=0ahUKEwiKqcqs_Y7OAhXLlB4KHSOrBAAQ6AEIMDAC#v=onepage&q=coconut%20field%20leaf%20area&f=false
Coco = Plt.Constante(nombre='Palma de coco', densidad=40020, proyecto=proyecto)

O_arenosella_senc.secome(Coco)
Parasitoide_senc.secome(O_arenosella_senc)

Red_coco_senc = Red('Campos coco sencillo', organismos=[Coco, O_arenosella_senc, Parasitoide_senc],
                    proyecto=proyecto)
Red_coco_senc.guardar()

Experimento_A = Experimento(nombre='Sitio A', proyecto=proyecto)
Experimento_A.agregar_orgs(archivo='Oarenosella_A.csv', col_tiempo='Día', factor=655757.1429/500)

Experimento_B = Experimento(nombre='Sitio B', proyecto=proyecto)
Experimento_B.agregar_orgs(archivo='Oarenosella_B.csv', col_tiempo='Día', factor=655757.1429/500)

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

"""
ajuste_inic = Red_coco_senc.validar(exper=Experimento_A)
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
"""

# Especificar distribuciones a priori
"""
Referencia excelente:
http://www.nhm.ac.uk/our-science/data/chalcidoids/database/detail.dsml?VALDATE=1930&ValidAuthBracket=false&FamilyCode=CC&VALSPECIES=nephantidis&listPageURL=listChalcids.dsml%3FSpecies%3Daeca%26Superfamily%3DChalcidoidea%26Family%3DChalcididae%26Genus%3DBrachymeria&tab=biology&HOMCODE=0&VALGENUS=Brachymeria&VALAUTHOR=Gahan&keyword=Fc
"""
dib_aprioris = False
O_arenosella_senc.especificar_apriori(etapa='adulto',
                                      ubic_parám=['Crecimiento', 'Modif', 'Ninguna', 'r'],
                                      # Huevos por adulto / días de vida
                                      rango=((152-26*1.96)/(53.1+.2*1.96), (152+26*1.96)/(53.1-.2*1.96)),
                                      certidumbre=.95,
                                      dibujar=dib_aprioris)

O_arenosella_senc.especificar_apriori(etapa='adulto',
                                      ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                                      org_inter=Coco, etp_inter='planta',
                                      rango=(1/(1823e-6+(100e-6*1.96)), 1/(1823e-6-(100e-6*1.96))),
                                      certidumbre=.95,
                                      dibujar=dib_aprioris)

O_arenosella_senc.especificar_apriori(etapa='adulto',
                                      ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                                      org_inter=Coco, etp_inter='planta',
                                      rango=(1823e-6+(100e-6*1.96), 1823e-6-(100e-6*1.96)),
                                      certidumbre=.95,
                                      dibujar=dib_aprioris)

O_arenosella_senc.especificar_apriori(etapa='adulto',
                                      ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                                      org_inter=Coco, etp_inter='planta',
                                      rango=((1823e-6-(100e-6*1.96))**2, (1823e-6+(100e-6*1.96))**2),
                                      certidumbre=.95,
                                      dibujar=dib_aprioris)  # Para hacer

Parasitoide_senc.especificar_apriori(etapa='adulto',
                                     ubic_parám=['Crecimiento', 'Modif', 'Ninguna', 'r'],
                                     rango=(6/15, 164/9),
                                     certidumbre=0.95,
                                     dibujar=dib_aprioris)

Parasitoide_senc.especificar_apriori(etapa='adulto',
                                     ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                                     org_inter=O_arenosella_senc, etp_inter='adulto',
                                     rango=(1, 10),
                                     certidumbre=0.95,
                                     dibujar=dib_aprioris)

Parasitoide_senc.especificar_apriori(etapa='adulto',
                                     ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                                     org_inter=O_arenosella_senc, etp_inter='adulto',
                                     rango=(20, 164),
                                     certidumbre=.95,
                                     dibujar=dib_aprioris)

Parasitoide_senc.especificar_apriori(etapa='adulto',
                                     ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                                     org_inter=O_arenosella_senc, etp_inter='adulto',
                                     rango=(20 ** 2, 164 ** 2),
                                     certidumbre=.95,
                                     dibujar=dib_aprioris)  # Para hacer


# ajuste_con_aprioris = Red_coco_senc.validar(exper=Experimento_A, usar_especificadas=True)
# print('Ajuste con a prioris', ajuste_con_aprioris)

# Intentar calibrar de nuevo
Red_coco_senc.calibrar('Con aprioris', exper=Experimento_A, n_iter=10, quema=0, extraer=1,
                       dibujar=True)
Red_coco_senc.validar(exper=Experimento_A)
Red_coco_senc.validar(exper=Experimento_B)
Red_coco_senc.guardar_calib(descrip='Calibración de red sencilla (oruga y parasitoide) para O. arenosella en coco, '
                                    'empleando a prioris.'
                                    'Se aplicó el sitio A de Perera et al. para la calibración.',
                            utilizador='Julien Malard',
                            contacto='julien.malard@mail.mcgill.ca')
Red_coco_senc.guardar()


# Bueno, ahora vamos a ver con una estructura de red más compleja (agregando un depredador generalista)
Araña = Ins.Sencillo('Araña')
Araña.secome(O_arenosella_senc)
Araña.secome(Parasitoide_senc)
# Araña.especificar_apriori()
# Araña.especificar_apriori()

Red_coco_senc.añadir_org(Araña)

Red_coco_senc.calibrar(nombre='Con araña', exper=Experimento_A, n_iter=100, quema=10)
Red_coco_senc.validar(exper=Experimento_A)
Red_coco_senc.validar(exper=Experimento_B)
Red_coco_senc.guardar_calib(descrip='Calibración de red sencilla (oruga y parasitoide) para O. arenosella en coco, '
                                    'empleando a prioris.'
                                    'Se aplicó el sitio A de Perera et al. para la calibración.',
                            utilizador='Julien Malard',
                            contacto='julien.malard@mail.mcgill.ca')
Red_coco_senc.guardar()

# Intentemos algo más interesante ahora.
O_arenosella = Ins.MetamCompleta('O. arenosella', njuvenil=5)

Parasitoides_larvas = Ins.Parasitoide('Parasitoide larvas')

Parasitoides_pupa = Ins.Parasitoide('Parasitoide pupas')

Parasitoides_larvas.parasita(O_arenosella, etps_infec=['juvenil_1', 'juvenil_2', 'juvenil_3'], etp_sale='juvenil_5')

Red_coco = Red(nombre='Coco completa', organismos=[O_arenosella, Parasitoides_larvas, Parasitoides_pupa])

Red_coco.añadir_exp(Experimento_A,
                    corresp={'O. arenosella': {'juvenil_1': ['Estado 1'],
                                               'juvenil_2': ['Estado 2'],
                                               'juvenil_3': ['Estado 3'],
                                               'juvenil_4': ['Estado 4'],
                                               'juvenil_5': ['Estado 5'],
                                               'pupa': ['Pupa']},
                             'Parasitoide larvas': {'juvenil': ['Para_larv_abs']},
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

O_arenosella.especificar_apriori()
Parasitoides_larvas.especificar_apriori()
Parasitoides_pupa.especificar_apriori()

Red_coco.calibrar(exper=Experimento_A)
Red_coco.validar(Experimento_A)
Red_coco.validar(Experimento_B)

Red_coco.guardar_calib()
Red_coco.guardar()

# Ahora, con una red más compleja y con estructura completa para los insectos
Red_coco.añadir_org(Araña)

Red_coco.calibrar(nombre='Con araña', exper=Experimento_A, n_iter=100, quema=10)
Red_coco.validar(exper=Experimento_A)
Red_coco.validar(exper=Experimento_B)

Red_coco.guardar_calib()
Red_coco.guardar()