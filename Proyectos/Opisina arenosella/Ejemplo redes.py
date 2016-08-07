import os

import RAE.NuevoINSECTO as Ins
from RAE.NuevaRedAE import Red
import RAE.Planta as Plt
from MATEMÁTICAS.Experimentos import Experimento

proyecto = 'Opisina arenosella'
O_arenosella_senc = Ins.Sencillo(nombre='O. arenosella_senc', proyecto=proyecto)
Parasitoide_senc = Ins.Sencillo(nombre='Parasitoide_senc', proyecto=proyecto)

# Datos de desnsidad de coco: Agricultural Ecology and Environment, pg 321 +
# https://books.google.com.gt/books?id=0gjoQ0OTpAYC&pg=PA318&lpg=PA318&dq=coconut+field+leaf+area&source=bl&ots=I9GJ8L88y2&sig=t0LUc7kUPDyDlniDdoipiYx84uU&hl=en&sa=X&ved=0ahUKEwiKqcqs_Y7OAhXLlB4KHSOrBAAQ6AEIMDAC#v=onepage&q=coconut%20field%20leaf%20area&f=false
Coco = Plt.Constante(nombre='Palma de coco', densidad=(2*12 + 7*14)/2, proyecto=proyecto)

O_arenosella_senc.secome(Coco)
Parasitoide_senc.secome(O_arenosella_senc)

Red_coco_senc = Red('Campos coco sencillo', organismos=[Coco, O_arenosella_senc, Parasitoide_senc],
                    proyecto=proyecto)

Experimento_A = Experimento(nombre='Sitio A')
directorio = os.path.dirname(__file__)
Experimento_A.cargar_orgs(archivo=os.path.join(directorio, 'Oarenosella.csv'), col_tiempo='Día')

Experimento_B = Experimento(nombre='Sitio B')
Experimento_B.cargar_orgs(archivo=os.path.join(directorio, 'Oarenosella_B.csv'), col_tiempo='Día')

Red_coco_senc.añadir_exp(Experimento_A,
                         corresp={'O. arenosella_senc': {'adulto': ['Larva', 'Pupa']},
                                  'Parasitoide_senc': {'adulto': ['Para_larva_abs']}
                                  }
                         )

Red_coco_senc.añadir_exp(Experimento_B,
                         corresp={'O. arenosella_senc': {'adulto': ['Estado 1', 'Estado 2', 'Estado 3', 'Estado 4',
                                                                    'Estado 5', 'Pupa']}
                                  }
                         )

ajuste_inic = Red_coco_senc.validar(exper=Experimento_A)
print('Ajuste inicial: ', ajuste_inic)

# Intentar calibrar
Red_coco_senc.calibrar(nombre='Sin a priori', exper=Experimento_A, n_iter=100, quema=10)
Red_coco_senc.validar(exper=Experimento_A)
Red_coco_senc.validar(exper=Experimento_B)
Red_coco_senc.guardar_calib(descrip='Calibración de red sencilla (oruga y parasitoide) para O. arenosella en coco, '
                                    'sin usar a prioris. Se aplicó el sitio A de Perera et al. para la calibración.',
                            utilizador='Julien Malard',
                            contacto='julien.malard@mail.mcgill.ca')

# Especificar distribuciones a priori
"""
Referencia excelente:
http://www.nhm.ac.uk/our-science/data/chalcidoids/database/detail.dsml?VALDATE=1930&ValidAuthBracket=false&FamilyCode=CC&VALSPECIES=nephantidis&listPageURL=listChalcids.dsml%3FSpecies%3Daeca%26Superfamily%3DChalcidoidea%26Family%3DChalcididae%26Genus%3DBrachymeria&tab=biology&HOMCODE=0&VALGENUS=Brachymeria&VALAUTHOR=Gahan&keyword=Fc
"""

O_arenosella_senc.especificar_apriori(etapa='adulto',
                                      ubic_parám=['Crecimiento', 'Modif', 'Ninguna', 'r'],
                                      rango=(126/53*1.96, 178/53*1.96),  # Huevos por adulto / días de vida
                                      certidumbre=.95)
O_arenosella_senc.especificar_apriori(etapa='adulto',
                                      ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                                      org_inter=Coco, etp_inter='planta',
                                      rango=(1723e-6*1.96, 1923e-6*1.96),
                                      certidumbre=.95)
Parasitoide_senc.especificar_apriori(etapa='adulto',
                                     ubic_parám=['Crecimiento', 'Modif', 'Ninguna', 'r'],
                                     rango=(6/15, 164/9),
                                     certidumbre=0.95)
Parasitoide_senc.especificar_apriori(etapa='adulto',
                                     ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                                     org_inter=O_arenosella_senc, etp_inter='adulto',
                                     rango=(6, 164),
                                     certidumbre=0.95)

ajuste_con_aprioris = Red_coco_senc.validar(exper=Experimento_A, usar_especificados=True)
print('Ajuste con a prioris', ajuste_con_aprioris)

# Intentar calibrar de nuevo
Red_coco_senc.calibrar('Con aprioris', exper=Experimento_A, n_iter=100, quema=10)
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
Araña.especificar_apriori()
Araña.especificar_apriori()

Red_coco_senc.añadir_org(Araña)

Red_coco_senc.calibrar(nombre='Con araña', exper=Experimento_A, n_iter=100, quema=10)
Red_coco_senc.validar(exper=Experimento_A)
Red_coco_senc.validar(exper=Experimento_B)
Red_coco_senc.guardar_calib()
Red_coco_senc.guardar()

# Intentemos algo más interesante ahora.
O_arenosella = Ins.MetamCompleta('O. arenosella', njuvenil=5)

Parasitoides_larvas = Ins.Parasitoide('Parasitoide larvas')

Parasitoides_pupa = Ins.Parasitoide('Parasitoide pupas')

Parasitoides_larvas.parasita(O_arenosella, etps_infec=[1, 2, 3], etp_sale=[])

Red_coco = Red(nombre='Coco compleja', organismos=[O_arenosella, Parasitoides_larvas, Parasitoides_pupa])

O_arenosella.especificar_apriori()
Parasitoides_larvas.especificar_apriori()
Parasitoides_pupa.especificar_apriori()

Red_coco.calibrar(exper=Experimento_A)
Red_coco.validar(Experimento_A)
Red_coco.validar(Experimento_B)

Red_coco.guardar_calib()
