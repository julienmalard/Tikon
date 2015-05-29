import subprocess
##call("CROPSYST PARAMA.SIM REPORTQ.FMT NOGRAPH")



class cultivo(object):
    def __init__(self,nombre,):
        self.nombre = nombre

    def ejec(self, programa, prog_cult = "", carpeta_ingr, carpeta_egr = carpeta_ingr):
        if self.programa == "DSSAT":
            comanda = "C:\DSSAT45\DSCSM046.EXE " + prog_cult + " B " + carpeta_ingr
        elif self.prog_cult == "CropSyst":
            #Sería chévere incluir un módulo para CropSyst, un dia, en el futuro...
            return("Falta un módulo para CropSyst.")
        else:
            return("Modelo de cultivo no reconocido.")
        
        self.proceso = subprocess.Popen(comanda,
                                        shell=True,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        cwd = carpeta_egr,
                                        )
    def incr(self,paso,plagas):
        egresos = {"Raices":"","Hojas":""}
        for día in paso:
            self.proceso.stdin.write(plagas)
            self.proceso.stdin.flush()
            línea = self.proceso.stdout.readline()
            while "Empezando" not in línea and len(línea):
                for egreso in egresos:
                    if egreso in línea:
                        egresos[egreso] = float(línea.decode()[len(egreso):len(línea)])
                línea = self.proceso.stdout.readline()

#Pruebas
cultivo("prueba_cult", programa = "DSSAT", prog_cult="MZCER046",
        carpeta_egr="F:\Julien\PhD\Python\Resultados_DSSAT",
        carpeta_ingr="F:\Julien\PhD\Python\Resultados_DSSAT\DSSBatch.v45")

prueba_cult.ejec()

##"C:\CS_Suite_4\CropSyst\cropsyst_4.exe" "D:\AgMIP\Wheat Runs\Scenarios\ARBA0XXX\.CropSyst_scenario" NOGRAPH 
##"d:\programs\CS_Suite_4\CropSyst\CropSyst_4.exe" "d:\path\project name\Scenarios\scenario name\.CropSyst_scenario" 
##C:\cs_suite_4\cropsyst.exe "C:\my scenarios path\my scenario.CSN" NOGRAPH > NUL
##
##
##http://www.apsim.info/Documentation/TechnicalandDevelopment/RunAPSIMfromcommandlineorfromscripts.aspx
