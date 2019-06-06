# Un documento con todas las distribuciones a prioris necesarias para el modelo de O. arenosella


"""
Estos datos de distribuciones a prioris vienen de la literatura (ver el documento Excel adjunto).
¿Se me olvidó juntarlo? Escríbame: julien.malard@mail.mcgill.ca

Referencia excelente:
http://www.nhm.ac.uk/our-science/data/chalcidoids/database/detail.dsml?VALDATE=1930&ValidAuthBracket=false&FamilyCode
=CC&VALSPECIES=nephantidis&listPageURL=listChalcids.dsml%3FSpecies%3Daeca%26Superfamily%3DChalcidoidea%26Family%3DCha
lcididae%26Genus%3DBrachymeria&tab=biology&HOMCODE=0&VALGENUS=Brachymeria&VALAUTHOR=Gahan&keyword=Fc
"""
from tikon.ecs.aprioris import APrioriDens

a_prioris = {

    'O. arenosella_senc': [
        dict(etapa='adulto',
             categ='Crecimiento', subcateg='Modif', ec='Ninguna', prm='r',
             apriori=APrioriDens(((2.721 - 0.7539) / 2 * 1.96, (2.721 + 0.7539) / 2 * 1.96), 0.80)),
        dict(etapa='adulto',
             categ='Crecimiento', subcateg='Ecuación', ec='Logístico Presa', prm='K',
             org_inter='Palma de coco', etp_inter='planta',
             apriori=APrioriDens((1 / (1823 + 100 * 1.96), 1 / (1823 - 100 * 1.96)), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             org_inter='Palma de coco', etp_inter='planta',
             # Unidades: 100m**2 d -1
             apriori=APrioriDens(((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * 1e-9,
                                  (1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * 1e-9), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             org_inter='Palma de coco', etp_inter='planta',
             apriori=APrioriDens(
                 (((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * 1e-9) ** 2,
                  ((1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * 1e-9) ** 2), 0.80))  # Para hacer
    ],

    'Parasitoide_senc': [
        dict(etapa='adulto',
             categ='Crecimiento', subcateg='Modif', ec='Ninguna', prm='r',
             # 1:5 = 0.2 = 1-0.8 = ratio de sexos (macho a hembra)
             apriori=APrioriDens((0.402 * .8, (4.35 + 2.214 / 2) * .8), 0.80)),
        dict(etapa='adulto',
             categ='Crecimiento', subcateg='Ecuación', ec='Logístico Presa', prm='K',
             org_inter='O. arenosella_senc', etp_inter='adulto',
             # Visto que los datos son de orugas infectadas, tenemos que representar a
             # "un parasitoide" por "una oruga infectada" en el modelo sencillo.
             apriori=APrioriDens((1, 1), 1)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             org_inter='O. arenosella_senc', etp_inter='adulto',
             apriori=APrioriDens((20 / 30, (116 + 36.465 / 2) / 30), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             org_inter='O. arenosella_senc', etp_inter='adulto',
             apriori=APrioriDens(((20 / 30) ** 2, ((116 + 36.465 / 2) / 30) ** 2), 0.80))  # para hacer

    ],

    'Araña': [
        dict(etapa='adulto',
             categ='Crecimiento', subcateg='Modif', ec='Ninguna', prm='r',
             apriori=APrioriDens((100 / 60 / 2, 300 / 60 / 2), 0.80)),
        dict(etapa='adulto',
             categ='Crecimiento', subcateg='Ecuación', ec='Logístico Presa', prm='K',
             # org_inter='O. arenosella_senc', etp_inter='adulto',
             apriori=APrioriDens((1 / 1.54, 1 / 0.70), 0.80)),
        dict(etapa='adulto',
             categ='Crecimiento', subcateg='Ecuación', ec='Logístico Presa', prm='K',
             # org_inter='Parasitoide_senc', etp_inter='adulto',
             apriori=APrioriDens((1 / 50, 1 / 10), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             # org_inter='O. arenosella_senc', etp_inter='adulto',
             apriori=APrioriDens((0.70, 1.54), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             # org_inter='O. arenosella_senc', etp_inter='adulto',
             apriori=APrioriDens((100 ** 2, 1000 ** 2), 0.80)),  # para hacer
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             # org_inter='Parasitoide_senc', etp_inter='adulto',
             apriori=APrioriDens((10, 50), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             # org_inter='Parasitoide_senc', etp_inter='adulto',
             apriori=APrioriDens((10000 ** 2, 100000 ** 2), 0.80)),  # para hacer
        dict(etapa='adulto',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.01), 1))
    ],

    'O. arenosella': [
        # population_dynamics_of_the_coconut_caterpillar_opisina_arenosella_walker_lepidoptera_xyloryctidae_in_sri_lanka.pdf
        dict(etapa='huevo',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((2, 4), 0.80),
             ),
        dict(etapa='huevo',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80),
             ),
        dict(etapa='huevo',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0, 0.1), 0.8)
             # apriori=APrioriDens((0.025, 0.029), 0.50),
             ),
        dict(etapa='huevo',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.1), 1)),
        dict(etapa='juvenil_1',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             apriori=APrioriDens(((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * 1e-9 * .2,
                                  (1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * 1e-9 * .2), 0.80),
             ),
        dict(etapa='juvenil_1',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             apriori=APrioriDens((((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * .2 * 1e-9) ** 2,
                                  ((1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * .2 * 1e-9) ** 2), 0.80),
             ),
        dict(etapa='juvenil_1',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.05, 0.1), 0.8)  # por día
             ),
        dict(etapa='juvenil_1',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((5, 7), 0.80),
             ),
        dict(etapa='juvenil_1',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80),
             ),
        dict(etapa='juvenil_1',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.1), 1)),
        dict(etapa='juvenil_2',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             apriori=APrioriDens(((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * 1e-9 * .2,
                                  (1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * 1e-9 * .2), 0.80),
             ),
        dict(etapa='juvenil_2',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             apriori=APrioriDens((((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * .2 * 1e-9) ** 2,
                                  ((1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * .2 * 1e-9) ** 2), 0.80)),
        dict(etapa='juvenil_2',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.00001, 0.001), 0.8),
             ),
        dict(etapa='juvenil_2',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((6, 8), 0.80),
             ),
        dict(etapa='juvenil_2',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='juvenil_2',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.1), 1)),
        dict(etapa='juvenil_3',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             apriori=APrioriDens(((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * 1e-9 * .2,
                                  (1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * 1e-9 * .2), 0.80)),
        dict(etapa='juvenil_3',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             apriori=APrioriDens((((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * .2 * 1e-9) ** 2,
                                  ((1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * .2 * 1e-9) ** 2), 0.80)),
        dict(etapa='juvenil_3',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.00001, 0.005), 0.8)),
        dict(etapa='juvenil_3',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((5, 7), 0.80)),
        dict(etapa='juvenil_3',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='juvenil_3',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.1), 1)),
        dict(etapa='juvenil_4',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             apriori=APrioriDens(((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * 1e-9 * .2,
                                  (1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * 1e-9 * .2), 0.80)),
        dict(etapa='juvenil_4',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             apriori=APrioriDens((((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * .2 * 1e-9) ** 2,
                                  ((1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * .2 * 1e-9) ** 2), 0.80)),
        dict(etapa='juvenil_4',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.001, 0.03), 0.8)),
        dict(etapa='juvenil_4',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((3, 5), 0.80)),
        dict(etapa='juvenil_4',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='juvenil_4',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.1), 1)),
        dict(etapa='juvenil_5',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             apriori=APrioriDens(((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * 1e-9 * .2,
                                  (1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * 1e-9 * .2), 0.80)),
        dict(etapa='juvenil_5',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             apriori=APrioriDens((((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96) * .2 * 1e-9) ** 2,
                                  ((1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96) * .2 * 1e-9) ** 2), 0.80)),
        dict(etapa='juvenil_5',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.03, 0.04), 0.8)),
        dict(etapa='juvenil_5',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((5, 7), 0.80)),
        dict(etapa='juvenil_5',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='juvenil_5',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.1), 1)),
        dict(etapa='pupa',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.1), 1)),
        dict(etapa='pupa',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((4, 6), 0.80)),
        dict(etapa='pupa',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='pupa',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.001, 0.01), 0.8)),
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((2.6, 8.4), 0.80)),
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 4), 0.80)),
        dict(etapa='adulto',
             categ='Reproducción', subcateg='Prob', ec='Normal', prm='n',
             apriori=APrioriDens((3, 5), 0.80)),
        dict(etapa='adulto',
             categ='Reproducción', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((2.5, 4.5), 0.80)),
        dict(etapa='adulto',
             categ='Reproducción', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='adulto',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.1), 1))
    ],

    'Parasitoide larvas': [
        # https://link.springer.com/content/pdf/10.1007/BF02377846.pdf
        # http://www.nbair.res.in/Featured_insects/Goniozus-nephantidis.php
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((6, 7), 0.80)),
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             índs=['O. arenosella', 'O. arenosella juvenil_3'],
             apriori=APrioriDens((.005, .01), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             índs=['O. arenosella', 'O. arenosella juvenil_4'],
             apriori=APrioriDens((.005, 0.01), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             índs=['O. arenosella', 'O. arenosella juvenil_5'],
             apriori=APrioriDens((0.8, 1.0), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             apriori=APrioriDens((0, 2000), 0.80)),
        dict(etapa='adulto',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.01), 1)),
        dict(etapa='pupa',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((9, 11), 0.80)),
        dict(etapa='pupa',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='pupa',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.0001, 0.001), 0.8)),
        dict(etapa='pupa',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.01), 1)),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Mult', ec='Linear', prm='a',
             apriori=APrioriDens((1.3, 2), 0.80)),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((4, 5), 0.80)),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='juvenil',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.0001, 0.01), 0.8)),
        dict(etapa='juvenil',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.01), 1))
    ],

    'Parasitoide pupa': [
        # https://www.researchgate.net/publication/322330636_Development_of_Brachymeria_nephantidis_Gahan_Hymenoptera_Chalcididae_on_artificial_diet_reared_Opisina_arenosella
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((32, 34), 0.80)),
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((2, 5), 0.80)),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             apriori=APrioriDens((0.08, 0.1), 0.80)),  # ratio M:H = 2.8:1  (0.5 / 3.8, 1 / 3.8)
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             apriori=APrioriDens((0.8e5, 1.0e5), 0.80)),
        dict(etapa='adulto',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.01), 1)),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Mult', ec='Linear', prm='a',
             apriori=APrioriDens((4, 5), 0.80)),  #
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((7, 8), 0.80)),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), 0.80)),
        dict(etapa='juvenil',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0, 0.01), 0.8)),
        dict(etapa='juvenil',
             categ='Estoc', subcateg='Dist', ec='Normal', prm='sigma',
             apriori=APrioriDens((0, 0.01), 1)),
    ]
}
