# Un documento con todas las distribuciones a prioris necesarias para el modelo de L. coffeella


"""
Estos datos de distribuciones a prioris vienen de la literatura (ver el documento Excel adjunto).
¿Se me olvidó juntarlo? Escríbame: marcela.rojas@mail.mcgill.ca

Referencia excelente:
http://www.nhm.ac.uk/our-science/data/chalcidoids/database/detail.dsml?VALDATE=1930&ValidAuthBracket=false&FamilyCode
=CC&VALSPECIES=nephantidis&listPageURL=listChalcids.dsml%3FSpecies%3Daeca%26Superfamily%3DChalcidoidea%26Family%3DCha
lcididae%26Genus%3DBrachymeria&tab=biology&HOMCODE=0&VALGENUS=Brachymeria&VALAUTHOR=Gahan&keyword=Fc
"""

a_prioris = {

    'L. coffeella': [
        dict(etapa='huevo',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(5, 7),
             certidumbre=0.95,
             ),
        dict(etapa='huevo',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(1, 2),
             certidumbre=0.95,
             ),
        dict(etapa='huevo',
             ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
             rango=(0.025, 0.029),
             certidumbre=1,
             ),
        dict(etapa='juvenil',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'a'],
             rango=((1823-100*1.96)/(53.1+10.64*1.96)*.2, (1823-100*1.96)/(53.1-10.64*1.96)*.2),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil',
             ubic_parám=['Depredación', 'Ecuación', 'Kovai', 'b'],
             rango=(((1823-100*1.96)/(53.1+10.64*1.96))**2*.2, ((1823-100*1.96)/(53.1-10.64*1.96))**2*.2),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil',
             ubic_parám=['Muertes', 'Ecuación', 'Constante', 'q'],
             rango=(0.07/7, 0.3/5),  # por día
             certidumbre=1,
             ),
        dict(etapa='juvenil',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'mu'],
             rango=(5, 7),
             certidumbre=0.95,
             ),
        dict(etapa='juvenil',
             ubic_parám=['Transiciones', 'Prob', 'Normal', 'sigma'],
             rango=(.5, .6),
             certidumbre=0.95,
             ),
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
             rango=(0.07/9, 0.3/7),
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
             rango=(10, 30),
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
}
