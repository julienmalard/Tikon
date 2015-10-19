import os
# Un documento con la información de modelos de cultivos necesaria par amuchos de los módulos TIKON

# El directorio donde está ubicado DSSAT
dir_DSSAT = "C:\DSSAT46"


# Una función para sacar los modelos disponibles para un cultivo dado
def sacar_modelos_disp(cultivo):
    modelos_disp = {}

    # Modelos_pl.csv contiene información sobre los modelos disponibles
    with open(os.path.join('CULTIVO', 'MODELOS_EXTERNOS', 'Modelos_pl.csv')) as d:
        doc = d.readlines()
    variables = doc[0].replace("\n", "").replace(';', ',').split(',')
    for núm_línea, línea in enumerate(doc[1:]):
        datos = línea.replace("\n", "").replace(';', ',').split(',')
        if datos[variables.index('Cultivo')] == cultivo:
            mod_cul = datos[variables.index('Modelo')]
            modelos_disp[mod_cul] = {}
            modelos_disp[mod_cul]['Comanda'] = datos[variables.index('Comanda')]
            modelos_disp[mod_cul]['Programa'] = datos[variables.index('Programa')]
            modelos_disp[mod_cul]['Modelo'] = datos[variables.index('Modelo')]
            modelos_disp[mod_cul]['Cód_cultivo'] = datos[variables.index('Cód_cultivo')]

    return modelos_disp
