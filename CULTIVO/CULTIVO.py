import subprocess
import os
import CULTIVO.MODELOS_EXTERNOS.DSSAT.DSSAT as DSSAT


class Cultivo(object):
    # Cada parámetro en "__init__" debe ser un objeto Python correspondiente
    def __init__(simismo, nombre, cultivo, variedad, suelo, meteo, manejo, modelo=''):

        simismo.dic_base = {}
        simismo.nombre = nombre
        simismo.cultivo = cultivo
        simismo.variedad = variedad
        simismo.suelo = suelo
        simismo.meteo = meteo
        simismo.manejo = manejo
        simismo.modelo = modelo  # El modelo exterior que se utilizará para el cultivo
        # Para guardar los egresos del modelo de cultivo externo
        simismo.egresos = {"raices": (), "hojas": (), "asim": (), "tallo": (), "semillas": (), "frutas": {},
                           "nubes": (), "humrel": (), "lluvia": (), "tprom": (), "tmin": (), "tmax": (), "radsol": (),
                           "tsuelo": (), "humsuelo": ()}
        # Variables_suelos.csv contiene información sobre los modelos disponibles
        simismo.modelos_disp = {}
        with open(os.path.join(os.getcwd(), "CULTIVO\\Modelos_pl.csv")) as d:
            for núm_línea, línea in enumerate(d):
                if núm_línea == 0:
                    variables = línea.replace("\n", "").split(';')
                else:
                    datos = línea.replace("\n", "").split(';')
                    if datos[variables.index('Cultivo')] == simismo.cultivo:
                        mod_cul = datos[variables.index('Modelo')]
                        simismo.modelos_disp[mod_cul] = {}
                        simismo.modelos_disp[mod_cul]['Comanda'] = datos[variables.index('Comanda')]
                        simismo.modelos_disp[mod_cul]['Programa'] = datos[variables.index('Programa')]
                        simismo.modelos_disp[mod_cul]['Genotipo'] = datos[variables.index('Genotipo')]
                        simismo.modelos_disp[mod_cul]['Cód_cultivo'] = datos[variables.index('Cód_cultivo')]

    def ejec(self, fecha_init, carpeta):  # Este cree un sub-proceso con el modelo del cultivo
        # Si no hemos especificado un modelo de cultivo ya, escoger uno al hazar
        if len(self.modelo):
            if self.cultivo in self.modelos_disp:
                self.modelo = list(self.modelos_disp.keys())[0]
            else:
                return "No existe modelo de cultivo válido para cultivo" + self.cultivo + "."
        # Escoger el programa y la comanda apropiada para el modelo de cultivo escogido
        self.programa = self.modelos_disp[self.modelo]['Programa']
        self.comanda = self.modelos_disp[self.modelo]['Comanda']
        self.cód_cultivo = self.modelos_disp[self.modelo]['Cód_cultivo']

        if not os.path.isdir(carpeta):
            os.makedirs(carpeta)

        # Crear las carpetas de ingresos y enviar la comanda de ejecución a la computadora
        if self.programa == "DSSAT":
            dssat = DSSAT.Experimento(carpeta)
            dssat.gen_ingresos(nombre=self.nombre, fecha_init=fecha_init, cultivo=self.cultivo,
                                       modelo=self.modelo, variedad=self.variedad, suelo=self.suelo, meteo=self.meteo)
            comanda = "C:\DSSAT45\\" + self.comanda + " B " + carpeta + "DSSBatch.v46"
        elif self.programa == "CropSyst":
            # Sería chévere incluir un módulo para CropSyst, un dia, en el futuro...
            return "Falta un módulo para CropSyst."
        else:
            return "Modelo de cultivo no reconocido."
        
        self.proceso = subprocess.Popen(comanda,
                                        shell=True,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        cwd=carpeta,
                                        )

    def incr(self, paso, daño_plagas):
        # Convertir el diccionario de daño de plagas al formato texto (para ingresar en la línea de comanda)
        # El diccionario debe tener el formato siguiente: daño_plagas = dict(daño_hojas = (), daño_raíces = (),
        # daño_tallo = (), daño_semillas = (), daño_frutas = (), daño_asim = ()}
        daño_plagas_texto = ""
        for daño in daño_plagas:
            daño_plagas_texto += daño + ": " + daño_plagas[daño] + "; "

        # Para compatibilidad con FORTRAN (el modelo de cultivos DSSAT) y probablemente C++ también:
        daño_plagas_texto.replace("ñ", "n").replace("í", "i")

        # Incrementar el modelo de cultivo, por medio de la línea de comanda, para cada día
        for día in paso:
            self.proceso.stdin.write(daño_plagas_texto)  # Envía el estado de daño al modelo de cultivo
            self.proceso.stdin.flush()  # Una tecnicalidad obscura
            línea = self.proceso.stdout.readline()  # Leer lo que el modelo de cultivos tiene que decir...
            while "Empezando" not in línea and len(línea):  # ... y salvarlo en nuestro diccionario Python
                for egreso in self.egresos:
                    if egreso in línea:
                        self.egresos[egreso] = float(línea.decode()[len(egreso):len(línea)])
                línea = self.proceso.stdout.readline()

# Pruebas
prueba_cult = Cultivo("prueba_cult", modelo="MZCER046")

prueba_cult.ejec()

# "C:\CS_Suite_4\CropSyst\cropsyst_4.exe" "D:\AgMIP\Wheat Runs\Scenarios\ARBA0XXX\.CropSyst_scenario" NOGRAPH
# "d:\programs\CS_Suite_4\CropSyst\CropSyst_4.exe" "d:\path\project name\Scenarios\scenario name\.CropSyst_scenario"
# C:\cs_suite_4\cropsyst.exe "C:\my scenarios path\my scenario.CSN" NOGRAPH > NUL
#
#
# http://www.apsim.info/Documentation/TechnicalandDevelopment/RunAPSIMfromcommandlineorfromscripts.aspx
