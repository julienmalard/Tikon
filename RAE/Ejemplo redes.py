import RAE.NuevoINSECTO as Ins
from RAE.NuevaRED import Red
from INCERT.NuevaCALIB import Experimento


O_arenosella_senc = Ins.Sencillo(nombre='O_arenosella_senc')
Parasitoides_larvas_senc = Ins.Sencillo(nombre='')


O_arenosella = Ins.MetamCompleta('O oranosella', njuvenil=5)

Parasitoides_larvas = Ins.MetamCompleta('Parasitoide larvas', huevo=False)

Parasitoides_pupa = Ins.MetamCompleta('Parasitoide pupas', huevo=False)

Parasitoides_larvas.secome(O_arenosella)

Parasitoides_pupa.secome(O_arenosella)

Red_campos_de_coco = Red(nombre='Coco', organismos={O_arenosella, Parasitoides_larvas, Parasitoides_pupa})


Experimento_A = Experimento(nombre='Sitio A')
Experimento_A.estab_bd_rae(archivo='E:\\Julien\\PhD\\தமிழ்நாடு\\உபயோகான கட்டுரைகள்\\Oarenosella.csv',
                           tiempo='Día',
                           )

print(Experimento_A.datos)

Red_campos_de_coco.añadir_exp(Experimento_A,
                              corresp=dict(O_arenosella={'adulto': ['Larva', 'Pupa']},
                                           Parasitoides_larvas={'adulto': ['Para_larva_abs']},
                                           Parasitoides_pupa={'adulto': ['Para_pupa_abs']}
                                           )
                              )

print(Red_campos_de_coco.observ)

"""

Experimento_B = Experimento()
Experimento_B.estab_bd_rae('C:\\BasedeDatosB.csv')
Experimento_B.estab_datos(dict(O_arenosella='', Parasitoides_larvas='', Parasitoides_pupa=''))

Red_campos_de_coco.añadir_exp(Experimento_A)

Red_campos_de_coco.calibrar()

Red_campos_de_coco.validar(Experimento_B)

Red_campos_de_coco.simular()
"""