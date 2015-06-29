# La clase Insecto contiene la información sobre las relaciones cualitativas (depredadores y presas) y la ecuación que describe la dinámicas
# de la población de insectos individualmente.
class Insecto(object):
    
    def __init__(self,Nombre,depred=[],pres=[]):      #depred, prens = listas
        self.Nombre = Nombre                          #Nombre scientífico del insecto (para el usuario)
        self.nombre = self.Nombre.replace(" ","")     #Nombre sin espacios (para la compu)
        self.depred = depred
        self.pres = pres
        self.ecuación = "poblaciones[" + self.nombre + "]*(¿)"  #La ecuación de base. "¿" es un marcador para añadir más cositos después
    def incr(self, paso, ecuación, poblaciones):
        taza_crec = eval(ecuación)
        return poblaciones[self.nombre] + taza_crec * paso

class Depredor(Insecto):
    pass
    
class Herbívoro(Insecto):
    pass



# Generador de ecuación Lotka-Voltera sencilla
def gen_ecua_LV(insectos):       
    ecuación = ""
    for j in insectos:   #Para cada depredor o prensa
        ecuación = ecuación + (" + poblaciones['" + j + "'] * %(" + j + ")")   #Añadirlo a la ecuación
    return ecuación
    

# La clase mod_plagas contiene la información de la red trófica de un agroecosistema
class mod_plagas(object):
    
    def __init__(self,nombre,insectos,ecuaciones={}): 
        self.nombre = nombre                #El nombre del modelo
        self.insectos = insectos            #Los insectos a modelar. mod_plagas.insectos tiene que ser una lista de "Insectos" 
        self.ecuaciones = ecuaciones        #Un diccionario a llenar con las ecuaciones. Inicialmente vacio por modelos no calibrados
        if len(self.ecuaciones):            #Si e modelo ya tiene ecuaciones calibradas...
            self.calibrado = True
        else:
            self.calibrado = False          #Sino...
            for i in self.insectos:             #Para cada insecto de interés...
                self.ecuaciones[i] = {"Ecuación":eval(i).ecuación, "Coef":{}}       #eval(i) convierte i (texto) en el objeto correspondiente
                k = eval(i + ".depred") + eval(i + ".pres")                  #Lista de depredores y presas del insecto de interés
                for j in k:
                    if j not in self.insectos: k.remove(j)              #Quita depredores y presas no incluidos en este modelo
                if len(k):                      #Si el insecto todavía tiene depredores o prensas
                    self.ecuaciones[i]["Ecuación"] = self.ecuaciones[i]["Ecuación"].replace("¿",gen_ecua_LV(k))    #generar la ecuación
    
    def incr(self,poblaciones,paso):    #poblaciones tiene que ser escritas como un un diccionario (e.g. {'Araña':'45','Mosca':'30'}).
        if self.calibrado == True:
            for i in self.ecuaciones:
                ecuación = self.ecuaciones[i]["Ecuación"] % self.ecuaciones[i]["Coef"]
                poblaciones[i] = eval(i).incr(paso,ecuación,poblaciones)
            return poblaciones
        else:
            print("El modelo no está calibrado.")
            return "El modelo no está calibrado."
    
    def calib(self,datos):
        self.calibrado==True


###Pruebas
Araña = Depredor("Araña",pres=["Mosca"])
Mosca = Herbívoro("Mosca",depred=["Araña"])
Modelo = mod_plagas("Ensayo",["Mosca","Araña"])





