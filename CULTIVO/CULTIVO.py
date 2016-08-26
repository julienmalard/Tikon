import os
import subprocess

import CULTIVO.MODELOS_EXTERNOS.DSSAT.DSSAT as DSSAT
from COSO import Simulable
from CULTIVO.Controles import dir_DSSAT
from CULTIVO.Controles import sacar_modelos_disp

"""
Notar que un Cultivo no se inicia como una instancia de un COSO, porque solamente es un objecto intermediario
que toma información de las parcelas para comunicarse con los modelos externos  de cultivos.
No contienen información única que no esté ya presente en el objeto de la parcela correspondiente.
"""


class Cultivo(Simulable):
    # Cada parámetro en "__init__" debe ser un objeto Python correspondiente
    def __init__(símismo, cultivo, variedad, suelo, meteo, manejo, modelo=''):

        símismo.cultivo = cultivo
        símismo.variedad = variedad
        símismo.suelo = suelo
        símismo.meteo = meteo
        símismo.manejo = manejo
        símismo.modelo = modelo  # El modelo exterior que se utilizará para el cultivo
        # Para guardar los egresos del modelo de cultivo externo
        símismo.egresos = {"raices": (), "hojas": (), "asim": (), "tallo": (), "semillas": (), "frutas": {},
                           "nubes": (), "humrel": (), "lluvia": (), "tprom": (), "tmin": (), "tmax": (), "radsol": (),
                           "tsuelo": (), "humsuelo": ()}

        # Para guardar la conexión con el proceso externo del modelo del cultivo
        símismo.proceso = None

    def ejec(símismo, carpeta):  # Este cree un sub-proceso en la compu con el modelo del cultivo

        modelos_disp = sacar_modelos_disp(símismo.cultivo)

        # Si no hemos especificado un modelo de cultivo ya, escoger uno al hazar
        if not len(símismo.modelo):
            if símismo.cultivo in modelos_disp:
                símismo.modelo = list(modelos_disp.keys())[0]
            else:
                return "No existe modelo de cultivo válido para cultivo" + símismo.cultivo + "."

        # Escoger el programa y la comanda apropiada para el modelo de cultivo escogido
        programa = modelos_disp[símismo.modelo]['Programa']
        comanda = modelos_disp[símismo.modelo]['Comanda']

        if not os.path.isdir(carpeta):
            os.makedirs(carpeta)

        # Crear las carpetas de ingresos y enviar la comanda de ejecución a la computadora
        if programa == "DSSAT":
            dssat = DSSAT.Experimento(carpeta, suelo=símismo.suelo, variedad=símismo.variedad, meteo=símismo.meteo,
                                      cultivo=símismo.cultivo, manejo=símismo.manejo)
            dssat.gen_ingresos()
            comanda = os.path.join(dir_DSSAT, comanda) + " B " + carpeta + "DSSBatch.v46"
        elif programa == "CropSyst":
            # Sería chévere incluir un módulo para CropSyst, un dia, en el futuro...
            return "Falta un módulo para CropSyst."
        else:
            return "Modelo de cultivo no reconocido."
        
        símismo.proceso = subprocess.Popen(comanda,
                                           shell=True,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           cwd=carpeta,
                                           )

    def incr(símismo, paso, daño_plagas):
        # Convertir el diccionario de daño de plagas al formato texto (para ingresar en la línea de comanda)
        # El diccionario debe tener el formato siguiente: daño_plagas = dict(daño_hojas = (), daño_raíces = (),
        # daño_tallo = (), daño_semillas = (), daño_frutas = (), daño_asim = ()}
        daño_plagas_texto = ""
        for daño in daño_plagas:
            daño_plagas_texto += daño + ": " + daño_plagas[daño] + "; "

        # Para compatibilidad con FORTRAN (el modelo de cultivos DSSAT) y probablemente C++ también:
        daño_plagas_texto.replace("ñ", "n").replace("í", "i").replace('é', 'e').replace('á', 'a').replace('ó', 'o')
        daño_plagas_texto.replace('ú', 'u').replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O')
        daño_plagas_texto.replace('Ú', 'U')

        # Incrementar el modelo de cultivo, por medio de la línea de comanda, para cada día
        for día in paso:
            símismo.proceso.stdin.write(daño_plagas_texto)  # Envía el estado de daño al modelo de cultivo
            símismo.proceso.stdin.flush()  # Una tecnicalidad obscura
            línea = símismo.proceso.stdout.readline()  # Leer lo que el modelo de cultivos tiene que decir...
            while "Empezando" not in línea and len(línea):  # ... y salvarlo en nuestro diccionario Python
                for egreso in símismo.egresos:
                    if egreso in línea:
                        símismo.egresos[egreso] = float(línea.decode()[len(egreso):len(línea)])
                línea = símismo.proceso.stdout.readline()

# Para CropSyst, un día...
# "C:\CS_Suite_4\CropSyst\cropsyst_4.exe" "D:\AgMIP\Wheat Runs\Scenarios\ARBA0XXX\.CropSyst_scenario" NOGRAPH
# "d:\programs\CS_Suite_4\CropSyst\CropSyst_4.exe" "d:\path\project name\Scenarios\scenario name\.CropSyst_scenario"
# C:\cs_suite_4\cropsyst.exe "C:\my scenarios path\my scenario.CSN" NOGRAPH > NUL
#
#
# http://www.apsim.info/Documentation/TechnicalandDevelopment/RunAPSIMfromcommandlineorfromscripts.aspx
