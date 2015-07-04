import subprocess, os

class Cultivo(object):
    # Cada parámetro en "__init__" debe ser un objeto Python correspondiente
    def __init__(self, nombre, variedad, suelo, meteo, fecha_siembra, modelo={}):
        self.nombre = nombre
        self.variedad = variedad
        self.suelo = suelo
        self.meteo = meteo
        self.fecha_init = fecha_siembra
        self.modelo = modelo  # El modelo exterior que se utilizará para el cultivo

        # Variables_suelos.csv contiene información sobre los modelos disponibles
        modelos = {}
        with open(os.path.join(os.getcwd(), "CULTIVO\\Modelos_pl.csv")) as d:
            for núm_línea, línea in enumerate(d):
                if núm_línea == 0:
                    variables = línea.replace("\n", "").split(';')
                else:
                    datos = línea.replace("\n", "").split(';')
                    cultivo = datos[0]
                    cul_modelo = datos[variables.index('Modelo')]
                    if cultivo not in modelos.keys():  # SI el cultivo todavía no existe en el diccionario
                        modelos[cultivo] = {}
                        modelos[cultivo][cul_modelo] = dict(comanda=datos[variables.index('comanda')],
                                                        programa=datos[variables.index('Programa')])
                    else:
                        modelos[cultivo][cul_modelo]["comanda"].append(variables.index('comanda'))
                        modelos[cultivo][cul_modelo]["programa"].append(variables.index('Programa'))
        if not len(self.modelo):
            if self.variedad in modelos:
                self.modelo = modelos[self.variedad]["Modelo"][0]
            self.programa = modelos[self.variedad][self.modelo]["programa"][0]
            self.comanda = modelos[self.variedad][self.modelo]["comanda"][0]

    def ejec(self, tiempo_init, carpeta_egr):  # Este cree un sub-proceso con el modelo del cultivo
        if not os.path.isdir(carpeta_egr):
            os.makedirs(carpeta_egr)
        if self.programa == "DSSAT":
            comanda = "C:\DSSAT45\\" + self.comanda + " B " + carpeta_ingr
        elif self.programa == "CropSyst":
            # Sería chévere incluir un módulo para CropSyst, un dia, en el futuro...
            return "Falta un módulo para CropSyst."
        else:
            return "Modelo de cultivo no reconocido."
        
        self.proceso = subprocess.Popen(comanda,
                                        shell=True,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        cwd = carpeta_egr,
                                        )

    def incr(self, paso, daño_plagas):
        egresos = {"raices": (), "hojas": (), "asim": (), "tallo": (), "semillas": (), "frutas": {},
                   "nubes": (), "humrel": (), "lluvia": (), "tprom": (), "tmin": (), "tmax": (), "radsol": (),
                   "tsuelo": (), "humsuelo": ()}
        # Convertir el diccionario de daño de plagas al formato texto (para ingresar en la línea de comanda)
        # El diccionario debe tener el formato siguiente: daño_plagas = dict(daño_hojas = (), daño_raíces = (),
        # daño_tallo = (), daño_semillas = (), daño_frutas = (), daño_asim = ()}
        daño_plagas_texto = ""
        for daño in daño_plagas:
            daño_plagas_texto += daño + ": " + daño_plagas[daño] + "; "

        # Para compatibilidad con FORTRAN (el modelo de cultivos DSSAT):
        daño_plagas_texto.replace("ñ", "n").replace("í", "i")

        # Incrementar el modelo de cultivo, por medio de la línea de comanda, para cada día
        for día in paso:
            self.proceso.stdin.write(daño_plagas_texto)  # Envia el estado de daño al modelo de cultivo
            self.proceso.stdin.flush()  # Una tecnicalidad obscura
            línea = self.proceso.stdout.readline()  # Leer lo que el modelo de cultivos tiene que decir...
            while "Empezando" not in línea and len(línea):  # ... y salvarlo en nuestro diccionario Python
                for egreso in egresos:
                    if egreso in línea:
                        egresos[egreso] = float(línea.decode()[len(egreso):len(línea)])
                línea = self.proceso.stdout.readline()
        return egresos  # Pasar el estado del cultivo (incluye le meteorología)

# Pruebas
prueba_cult = Cultivo("prueba_cult", programa = "DSSAT", modelo="MZCER046",
        carpeta_egr="F:\Julien\PhD\Python\Resultados_DSSAT",
        carpeta_ingr="F:\Julien\PhD\Python\Resultados_DSSAT\DSSBatch.v45")

prueba_cult.ejec()

##"C:\CS_Suite_4\CropSyst\cropsyst_4.exe" "D:\AgMIP\Wheat Runs\Scenarios\ARBA0XXX\.CropSyst_scenario" NOGRAPH 
##"d:\programs\CS_Suite_4\CropSyst\CropSyst_4.exe" "d:\path\project name\Scenarios\scenario name\.CropSyst_scenario" 
##C:\cs_suite_4\cropsyst.exe "C:\my scenarios path\my scenario.CSN" NOGRAPH > NUL
##
##
##http://www.apsim.info/Documentation/TechnicalandDevelopment/RunAPSIMfromcommandlineorfromscripts.aspx
