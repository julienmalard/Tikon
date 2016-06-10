import os

import RAE.NuevoINSECTO as Ins
from RAE.NuevaRedAE import Red
from MATEMÁTICAS.Experimentos import Experimento


O_arenosella_senc = Ins.Sencillo(nombre='O. arenosella_senc')
Parasitoide_senc = Ins.Sencillo(nombre='Parasitoide_senc')

Parasitoide_senc.secome(O_arenosella_senc)

Red_coco_senc = Red('Campos coco sencillo', organismos=[O_arenosella_senc, Parasitoide_senc])

"""
O_arenosella = Ins.MetamCompleta('O. arenosella', njuvenil=5)

Parasitoides_larvas = Ins.MetamCompleta('Parasitoide larvas', huevo=False)

Parasitoides_pupa = Ins.MetamCompleta('Parasitoide pupas', huevo=False)

Red_campos_de_coco = Red(nombre='Coco', organismos=[O_arenosella, Parasitoides_larvas, Parasitoides_pupa])
"""

Experimento_A = Experimento(nombre='Sitio A')
directorio = os.path.dirname(__file__)
Experimento_A.cargar_orgs(archivo=os.path.join(directorio, 'Oarenosella.csv'),
                          col_tiempo='Día'
                          )

print(Experimento_A.datos)

Red_coco_senc.añadir_exp(Experimento_A,
                         corresp={'O. arenosella_senc': {'adulto': ['Larva', 'Pupa']},
                                  'Parasitoide_senc': {'adulto': ['Para_larva_abs']}
                                  }
                         )

Red_coco_senc.calibrar()

"""
Experimento_B = Experimento()
Experimento_B.estab_bd_rae('C:\\BasedeDatosB.csv')
Experimento_B.estab_datos(dict(O_arenosella='', Parasitoides_larvas='', Parasitoides_pupa=''))


Red_coco_senc.validar(Experimento_B)

Red_coco_senc.simular()
"""
