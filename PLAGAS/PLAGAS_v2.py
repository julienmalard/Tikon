# La clase Insecto contiene la información sobre las relaciones cualitativas (depredadores y presas) y la ecuación que describe la dinámicas
# de la población de insectos individualmente.
class Insecto(object):
    
    def __init__(self,Nombre,depred=[],pres=[]):    #depred, prens = listas
        self.Nombre = Nombre                        #Nombre scientífico del insecto (para el usuario)
        self.nombre = self.Nombre.replace(" ","")   #Nombre sin espacios (para la compu)
        self.depred = depred
        self.pres = pres
    def incr(self, paso, ecuación, poblaciones):
        taza_crec = eval(ecuación)
        return poblaciones[self.nombre] + taza_crec * paso

#Generador de ecuación general para insecto sin depredadores
def gen_ecua_dep(insecto, presas):  #insecto depredadores (con presas)
    sub_ecuación = ""
    pres_adición = ""
    for p in presas:
        pres_adición = pres_adición + "+ poblaciones['"+ p +"']"
    for p in presas:
        C = "C_{0}_{1}".format(p,insecto)
        b = "b_{0}_{1}".format(p,insecto)
        h = "h_{0}_{1}".format(p,insecto)
        sub_ecuación = sub_ecuación + "+ %({b}) * (({C}/poblaciones['"+ insecto +"']^m *"\
            "poblcaiones['"+ p +"'])/(1 + {C}/poblaciones['"+ insecto +"']^m*{h}*poblaciones['"+ p +"']))"\
            "*poblaciones['"+ p +"']/("+ pres_adición +")"
        sub_ecuación = sub_ecuación.format(**locals())
        ecuación = "poblaciones['"+ insecto + "'] * ("+ sub_ecuación +" - d)"  # Añadirlo a la ecuación
        ecuación = ecuación.format(**locals())
    return ecuación
def gen_ecua_herb(insecto):         # insecto herbivoros (sin presas)
    sub_ecuación = ""
    sub_ecuación = sub_ecuación + "+ (K*(1 - poblaciones['"+ insecto +"']/K)"
    ecuación = "poblaciones['"+ insecto +"']*a*("+ sub_ecuación +")"
    return ecuación

# Generador de ecuación general para adicionar la depredación del insecto
def ad_ecua_dep(insecto,depredadores):
    ecuación = ""
    for d in depredadores:
        C = "C_{0}_{1}".format(insecto,d)
        h = "h_{0}_{1}".format(insecto,d)
        ecuación = ecuación + "- poblaciones['"+ d +"']*(({C}/poblaciones['"+ d +"']^m * poblaciones['"+ insecto +"'])/(1 + {C}"\
        "/poblaciones['"+ d +"']* {h}*poblaciones['"+ insecto +"']"
        ecuación = ecuación.format(**locals())
    return ecuación

# Generador de ecuación general para insectos con depredadores
    

# La clase mod_plagas contiene la información de la red trófica de un agroecosistema
class mod_plagas(object):
    
    def __init__(self,nombre,insectos,ecuaciones={}): 
        self.nombre = nombre                #El nombre del modelo
        self.insectos = insectos            #Los insectos a modelar. mod_plagas.insectos tiene que ser una lista de "Insectos" 
        self.ecuaciones = ecuaciones        #Una lista de diccionario (Ecuación + Coef) a llenar con las ecuaciones. Inicialmente vacio por modelos no calibrados
        if len(self.ecuaciones):            #Si e modelo ya tiene ecuaciones calibradas... (tiene que tener TODAS las ecuaciónes de los insectos del modelo)
            self.calibrado = True
        else:
            self.calibrado = False          #Sino: CALIBRACIÓN
            for i in self.insectos:         #Para cada insecto de interés...
                self.ecuaciones[i] = {"Ecuación":{}, "d":[], "b":{}, "C":{}, "h":{}, "K":[], "a":[]}
                p = eval(i + ".pres")       #Lista de presas del insecto de interés. Nota: eval(i) convierte i (texto) en el objeto correspondiente
                for j in p:
                    if j not in self.insectos: p.remove(j)   #Quita presas no incluidos en este modelo
                d = eval(i + ".depred")     #Lista de depredores del insecto de interés
                for j in d:
                    if j not in self.insectos: d.remove(j)  #Quita depredores no incluidos en este modelo
        
                if len(p):              #Si el insecto tiene presas
                    self.ecuaciones[i]["Ecuación"] = gen_ecua_dep(i, p)    #generar la ecuación depredadores
                else:                   #Si el insecto es herbivoro (no tiene presas)
                    self.ecuaciones[i]["Ecuación"] = gen_ecua_herb(i)    #generar la ecuación para herbivoros
                if len(d):                  #Si el insecto tiene depredadors
                    if len(p):              #Insecto con presas
                        self.ecuaciones[i]["Ecuación"] = self.ecuaciones[i]["Ecuación"] + ad_ecua_dep(i,d)    #adiciona la depredación a insectos depredadores

                    else:                   #Insecto herbivoro (sin presas)
                        self.ecuaciones[i]["Ecuación"] = self.ecuaciones[i]["Ecuación"]+ ad_ecua_dep(i,d)    #adiciona la depredación a insectos herbivoros
                                                
    def incr(self,paso, poblaciones):    #poblaciones tiene que ser escritas como un un diccionario (e.g. {'Araña':'45','Mosca':'30'}).
            m = 1
            for i in self.ecuaciones:
                ecuación = self.ecuaciones[i]["Ecuación"]
                poblaciones[i] = eval(i).incr(paso,ecuación,poblaciones)
            return poblaciones

    


###Pruebas
Araña = Insecto("Araña",pres=["Mosca","Pulgón","Avispa1"])
Mosca = Insecto("Mosca",depred=["Araña","Avispa1"])
Pulgón = Insecto("Pulgón", depred=["Araña"])
Avispa1= Insecto("Avispa1", pres=["Mosca"], depred=["Araña"])
Ensayo = mod_plagas("Ensayo",["Mosca","Araña","Pulgón","Avispa1"])
#Ensayo.ecuaciones["Mosca"]["Coef"] = {'C':{'Araña':'1'},'a':'3','K':'5'}
#Ensayo.ecuaciones["Araña"]["Coef"] = {'d':'10','b':{'Mosca':'2'},'C':{'Mosca':'1'},'h':{'Mosca':'2'}}
#Ensayo.incr(1,{'Araña':'45','Mosca':'30'})





