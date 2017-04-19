# Un documento con todas las distribuciones a prioris necesarias para el modelo de O. arenosella


"""
Estos datos de distribuciones a prioris vienen de la literatura (ver el documento Excel adjunto).
¿Se me olvidó juntarlo? Escríbame: julien.malard@mail.mcgill.ca

Referencia excelente:
http://www.nhm.ac.uk/our-science/data/chalcidoids/database/detail.dsml?VALDATE=1930&ValidAuthBracket=false&FamilyCode
=CC&VALSPECIES=nephantidis&listPageURL=listChalcids.dsml%3FSpecies%3Daeca%26Superfamily%3DChalcidoidea%26Family%3DCha
lcididae%26Genus%3DBrachymeria&tab=biology&HOMCODE=0&VALGENUS=Brachymeria&VALAUTHOR=Gahan&keyword=Fc
"""

a_prioris = {

    'O. arenosella_senc': [dict(etapa='adulto',
                                ubic_parám=['Crecimiento', 'Modif', 'Ninguna', 'r'],
                                rango=((2.721-0.7539)/2*1.96, (2.721+0.7539)/2*1.96),
                                certidumbre=.95),
                           dict(etapa='adulto',
                                ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                                org_inter='Palma de coco', etp_inter='planta',
                                rango=(1/(1823+100*1.96), 1/(1823-100*1.96)),
                                certidumbre=.95),
                           dict(etapa='adulto',
                                ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                                org_inter='Palma de coco', etp_inter='planta',
                                # Unidades: mm d -1
                                rango=((1823-100*1.96)/(53.1+10.64*1.96), (1823-100*1.96)/(53.1-10.64*1.96)),
                                certidumbre=.95),
                           dict(etapa='adulto',
                                ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                                org_inter='Palma de coco', etp_inter='planta',
                                rango=(((1823-100*1.96)/(53.1+10.64*1.96))**2, ((1823-100*1.96)/(53.1-10.64*1.96))**2),
                                certidumbre=.95)  # Para hacer
                           ],

    'Parasitoide_senc': [dict(etapa='adulto',
                              ubic_parám=['Crecimiento', 'Modif', 'Ninguna', 'r'],
                              # 1:5 = 0.2 = 1-0.8 = ratio de sexos (macho a hembra)
                              rango=(0.402*.8, (4.35+2.214/2)*.8),
                              certidumbre=0.80),
                         dict(etapa='adulto',
                              ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                              org_inter='O. arenosella_senc', etp_inter='adulto',
                              # Visto que los datos son de orugas infectadas, tenemos que representar a
                              # "un parasitoide" por "una oruga infectada" en el modelo sencillo.
                              rango=(1, 1),
                              certidumbre=1),
                         dict(etapa='adulto',
                              ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                              org_inter='O. arenosella_senc', etp_inter='adulto',
                              rango=(20 / 30, (116+36.465/2)/30),
                              certidumbre=.95),
                         dict(etapa='adulto',
                              ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                              org_inter='O. arenosella_senc', etp_inter='adulto',
                              rango=((20/30)**2, ((116+36.465/2)/30)**2),
                              certidumbre=.95)  # para hacer

                         ],

    'Araña': [dict(etapa='adulto',
                   ubic_parám=['Crecimiento', 'Modif', 'Ninguna', 'r'],
                   rango=(100/60/2, 300/60/2),
                   certidumbre=0.80),
              dict(etapa='adulto',
                   ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                   org_inter='O. arenosella_senc', etp_inter='adulto',
                   rango=(1/1.54, 1/0.70),
                   certidumbre=0.95),
              dict(etapa='adulto',
                   ubic_parám=['Crecimiento', 'Ecuación', 'Logístico Presa', 'K'],
                   org_inter='Parasitoide_senc', etp_inter='adulto',
                   rango=(1/50, 1/10),
                   certidumbre=0.95),
              dict(etapa='adulto',
                   ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                   org_inter='O. arenosella_senc', etp_inter='adulto',
                   rango=(0.70, 1.54),
                   certidumbre=.95),
              dict(etapa='adulto',
                   ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                   org_inter='O. arenosella_senc', etp_inter='adulto',
                   rango=(100**2, 1000**2),
                   certidumbre=.95),  # para hacer
              dict(etapa='adulto',
                   ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
                   org_inter='Parasitoide_senc', etp_inter='adulto',
                   rango=(10, 50),
                   certidumbre=.95),
              dict(etapa='adulto',
                   ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
                   org_inter='Parasitoide_senc', etp_inter='adulto',
                   rango=(10000**2, 100000**2),
                   certidumbre=.95),  # para hacer
              ],

    'O. arenosella': [
        dict(etapa='huevo',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(2, 4),
             certidumbre=0.95,
             ),
        dict(etapa='huevo',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(.5, .6),
             certidumbre=0.95,
             ),
        dict(etapa='huevo',
             ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
             rango=(0.025, 0.029),
             certidumbre=1,
             ),
        dict(etapa='juvenil_1',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
             rango=((1823-100*1.96)/(53.1+10.64*1.96)*.2, (1823-100*1.96)/(53.1-10.64*1.96)*.2),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil_1',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
             rango=(((1823-100*1.96)/(53.1+10.64*1.96))**2*.2, ((1823-100*1.96)/(53.1-10.64*1.96))**2*.2),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil_1',
             ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
             rango=(0.07/7, 0.5/5),  # por día
             certidumbre=1,
             ),
        dict(etapa='juvenil_1',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(5, 9),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil_1',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(1, 2),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil_2',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
             rango=((1823-100*1.96)/(53.1+10.64*1.96)*.2, (1823-100*1.96)/(53.1-10.64*1.96)*.2),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil_2',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
             rango=(((1823-100*1.96)/(53.1+10.64*1.96))**2*.2, ((1823-100*1.96)/(53.1-10.64*1.96))**2*.2),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil_2',
             ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
             rango=(0.07/8, 0.4/6),
             certidumbre=1,
             ),
        dict(etapa='juvenil_2',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(6, 8),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil_2',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(.5, .6),
             certidumbre=0.95),
        dict(etapa='juvenil_3',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
             rango=((1823-100*1.96)/(53.1+10.64*1.96)*.2, (1823-100*1.96)/(53.1-10.64*1.96)*.2),
             certidumbre=0.95),
        dict(etapa='juvenil_3',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
             rango=(((1823-100*1.96)/(53.1+10.64*1.96))**2*.2, ((1823-100*1.96)/(53.1-10.64*1.96))**2*.2),
             certidumbre=0.95),
        dict(etapa='juvenil_3',
             ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
             rango=(0.07/8, 0.4/6),
             certidumbre=1),
        dict(etapa='juvenil_3',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(6, 8),
             certidumbre=0.95),
        dict(etapa='juvenil_3',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(.5, .6),
             certidumbre=0.95),
        dict(etapa='juvenil_4',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
             rango=((1823-100*1.96)/(53.1+10.64*1.96)*.2, (1823-100*1.96)/(53.1-10.64*1.96)*.2),
             certidumbre=0.95),
        dict(etapa='juvenil_4',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
             rango=(((1823-100*1.96)/(53.1+10.64*1.96))**2*.2, ((1823-100*1.96)/(53.1-10.64*1.96))**2*.2),
             certidumbre=0.95),
        dict(etapa='juvenil_4',
             ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
             rango=(0.07/6, 0.5/4),
             certidumbre=1),
        dict(etapa='juvenil_4',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(4, 6),
             certidumbre=0.95),
        dict(etapa='juvenil_4',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(.5, .6),
             certidumbre=0.95),
        dict(etapa='juvenil_5',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
             rango=((1823-100*1.96)/(53.1+10.64*1.96)*.2, (1823-100*1.96)/(53.1-10.64*1.96)*.2),
             certidumbre=0.95),
        dict(etapa='juvenil_5',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
             rango=(((1823-100*1.96)/(53.1+10.64*1.96))**2*.2, ((1823-100*1.96)/(53.1-10.64*1.96))**2*.2),
             certidumbre=0.95),
        dict(etapa='juvenil_5',
             ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
             rango=(0.07/11, 0.8/9),
             certidumbre=1),
        dict(etapa='juvenil_5',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(9, 11),
             certidumbre=0.95),
        dict(etapa='juvenil_5',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(.5, .6),
             certidumbre=0.95),
        dict(etapa='pupa',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(7, 9),
             certidumbre=0.95),
        dict(etapa='pupa',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(.5, .6),
             certidumbre=0.95),
        dict(etapa='pupa',
             ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
             rango=(0.07/9, 0.6/7),
             certidumbre=1),
        dict(etapa='adulto',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(2.6, 8.4),
             certidumbre=.95),
        dict(etapa='adulto',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(1, 2),
             certidumbre=.95),
        dict(etapa='adulto',
             ubic_parám=['Reproducción', 'Prob', 'Constante', 'a'],
             rango=(59/2/10, 252/2/10),
             certidumbre=0.95)
    ],

    'Parasitoide larvas': [
        dict(etapa='adulto',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(10, 20),
             certidumbre=0.95),
        dict(etapa='adulto',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(5, 10),
             certidumbre=0.95),
        dict(etapa='adulto',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
             rango=(10/20/2, 30/10/2),
             certidumbre=0.95),
        dict(etapa='adulto',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
             rango=(0.1e7, 6.0e7),
             certidumbre=0.95),
        dict(etapa='juvenil',
             ubic_parám=['Transiciones', 'Mult', 'Linear', 'a'],
             rango=(1, 10),
             certidumbre=0.95),
        dict(etapa='juvenil',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(9, 11),
             certidumbre=0.95),
        dict(etapa='juvenil',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(.5, .6),
             certidumbre=0.95),
    ],

    'Parasitoide pupas': [
        dict(etapa='adulto',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(10, 20),
             certidumbre=0.95),
        dict(etapa='adulto',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(5, 10),
             certidumbre=0.95),
        dict(etapa='adulto',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
             rango=(10/20, 30/10),
             certidumbre=0.95),
        dict(etapa='adulto',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
             rango=(0.5e5, 6.0e5),
             certidumbre=0.95),
        dict(etapa='juvenil',
             ubic_parám=['Transiciones', 'Mult', 'Linear', 'a'],
             rango=(1, 10),
             certidumbre=0.95),
        dict(etapa='juvenil',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(7, 9),
             certidumbre=0.95),
        dict(etapa='juvenil',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(.5, .6),
             certidumbre=0.95),
    ]
}
