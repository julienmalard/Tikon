# Un documento con todas las distribuciones a prioris necesarias para el modelo de L. coffeella


"""
Estos datos de distribuciones a prioris vienen de la literatura (ver el documento Excel adjunto).
¿Se me olvidó juntarlo? Escríbame: marcela.rojas@mail.mcgill.ca

Referencia excelente:
http://www.nhm.ac.uk/our-science/data/chalcidoids/database/detail.dsml?VALDATE=1930&ValidAuthBracket=false&FamilyCode
=CC&VALSPECIES=nephantidis&listPageURL=listChalcids.dsml%3FSpecies%3Daeca%26Superfamily%3DChalcidoidea%26Family%3DCha
lcididae%26Genus%3DBrachymeria&tab=biology&HOMCODE=0&VALGENUS=Brachymeria&VALAUTHOR=Gahan&keyword=Fc
"""
from tikon.ecs.aprioris import APrioriDens

a_prioris = {

    'L. coffeella': [
        dict(etapa='huevo',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((5, 20), 0.95),
             ),
        dict(etapa='huevo',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 5), 0.90),
             ),
        dict(etapa='huevo',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.30 / 20, 0.532 / 5), 1),
             ),
        dict(etapa='juvenil',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             apriori=APrioriDens((396, 1943), 0.95),
             ),
        dict(etapa='juvenil',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             apriori=APrioriDens(
                 (((1823 - 100 * 1.96) / (53.1 + 10.64 * 1.96)) ** 2 * .2,
                  ((1823 - 100 * 1.96) / (53.1 - 10.64 * 1.96)) ** 2 * .2), 0.95
             ),
             ),
        dict(etapa='juvenil',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.163 / 26, 0.491 / 7), 1)  # por día
             ),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((7, 26), 0.95),
             ),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 3), 0.90),
             ),
        dict(etapa='pupa',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((7, 14), 0.95)
             ),
        dict(etapa='pupa',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 3), 0.95)
             ),
        dict(etapa='pupa',
             categ='Muertes', subcateg='Ecuación', ec='Constante', prm='q',
             apriori=APrioriDens((0.011 / 14, 0.078 / 7), 1)
             ),
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((4, 14), .95)
             ),
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((1, 2), .95)
             ),
        dict(etapa='adulto',
             categ='Reproducción', subcateg='Prob', ec='Constante', prm='a',
             apriori=APrioriDens((12.5 / (14 * 2), 21.2 / (4 * 2)), 0.95))
    ],

    'Parasitoide larvas': [
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((10, 20), 0.95)
             ),
        dict(etapa='adulto',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((5, 10), 0.95)
             ),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='a',
             apriori=APrioriDens((10 / 20 / 2, 30 / 10 / 2), 0.95)
             ),
        dict(etapa='adulto',
             categ='Depredación', subcateg='Ecuación', ec='Kovai', prm='b',
             apriori=APrioriDens((0.1e7, 6.0e7), 0.95)
             ),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Mult', ec='Linear', prm='a',
             apriori=APrioriDens((1, 10), 0.95)
             ),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='mu',
             apriori=APrioriDens((9, 11), 0.95)
             ),
        dict(etapa='juvenil',
             categ='Transiciones', subcateg='Prob', ec='Normal', prm='sigma',
             apriori=APrioriDens((.5, .6), 0.95)
             )
    ]
}
