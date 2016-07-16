import os

import RAE.NuevoINSECTO as Ins
from RAE.NuevaRedAE import Red
import RAE.PLANTA as Plt
from MATEMÁTICAS.Experimentos import Experimento


O_arenosella_senc = Ins.Sencillo(nombre='O. arenosella_senc')
Parasitoide_senc = Ins.Sencillo(nombre='Parasitoide_senc')
Coco = Plt.Constante(nombre='Palma de coco', densidad=5000)

O_arenosella_senc.secome(Coco)
Parasitoide_senc.secome(O_arenosella_senc)

Red_coco_senc = Red('Campos coco sencillo', organismos=[Coco, O_arenosella_senc, Parasitoide_senc])

Experimento_A = Experimento(nombre='Sitio A')
directorio = os.path.dirname(__file__)
Experimento_A.cargar_orgs(archivo=os.path.join(directorio, 'Oarenosella.csv'),
                          col_tiempo='Día'
                          )

Red_coco_senc.añadir_exp(Experimento_A,
                         corresp={'O. arenosella_senc': {'adulto': ['Larva', 'Pupa']},
                                  'Parasitoide_senc': {'adulto': ['Para_larva_abs']},
                                  'Palma de coco': {'planta': ['Coco']}
                                  }
                         )

# Red_coco_senc.validar(exper=Experimento_A)

Red_coco_senc.calibrar()

# Red_coco_senc.validar(exper=Experimento_A)

"""
O_arenosella = Ins.MetamCompleta('O. arenosella', njuvenil=5)

Parasitoides_larvas = Ins.MetamCompleta('Parasitoide larvas', huevo=False)

Parasitoides_pupa = Ins.MetamCompleta('Parasitoide pupas', huevo=False)

Red_campos_de_coco = Red(nombre='Coco', organismos=[O_arenosella, Parasitoides_larvas, Parasitoides_pupa])

Experimento_B = Experimento()
Experimento_B.estab_bd_rae('C:\\BasedeDatosB.csv')
Experimento_B.estab_datos(dict(O_arenosella='', Parasitoides_larvas='', Parasitoides_pupa=''))


Red_coco_senc.validar(Experimento_B)

Red_coco_senc.simular()
"""
