import subprocess


class Cultivo(object):
    def __init__(self, nombre, variedad, suelo, meteo):  # Cada parámetro debe ser un objeto Python correspondiente
        self.nombre = nombre
        self.variedad = variedad
        self.suelo = suelo
        self.meteo = meteo
        self.fecha_init = fecha_init

    def ejec(self, tiempo_init, carpeta_egr):  # Este cree un sub-proceso con el modelo del cultivo
        if programa == "DSSAT":
            comanda = "C:\DSSAT45\\" + comanda + " B " + carpeta_ingr
        elif programa == "CropSyst":
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
