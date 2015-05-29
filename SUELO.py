
#Esta clase representa los suelos de una parcela.

class suelo(object):
    #dic puede ser un diccionario (de datos) o la dirección de un documento (que contiene los datos)
    def __init__(self,nombre,dic={}):
        self.nombre = nombre
        if type(dic) is dict:
            if len(dic): self.dic = dic
        elif type(dic) is str:
            self.leer(dic)
        else:
            return "Diccionario de suelo inválido."

    #Función para escribir los datos de suelo a un documento externo
        
    def escribir(self,carpeta=""):
        #Si necesario, añadir el nombre del documento al fin de la carpeta
        if ".pysuel" not in carpeta.lower():
            if self.nombre not in carpeta:
                carpeta += "\\" + self.nombre + ".pysuel"
            else:
                carptea += ".pysuel"     
        egreso = "" #Lo que vamos a escribir al documento
        for i in self.dic:
            egreso += str(i)+ ": " + str(self.dic[i]) + "\n"
        try:
            with open(carpeta,mode="w") as d:
                d.write(egreso)
        except IOError:
            return "Carpeta " + carpeta + " no se pudo abrir."
    
    #Función para leer los datos de suelo de un documento externo    
    def leer(self,carpeta):
        #Si necesario, añadir el nombre del documento al fin de la carpeta
        if ".pysuel" not in carpeta.lower():
            if self.nombre not in carpeta:
                carpeta += "\\" + self.nombre + ".pysuel"
            else:
                carptea += ".pysuel"
        with open(carpeta,mode="r") as d:
            for línea in d:
                if len(línea):
                    var,valor = línea.split(':', 1)
                    valor = valor.replace("\n","")
                    self.dic[var] = eval(valor)


#Pruebas:
prueba=suelo("suelo",{'Conductividad': [0.2, 0.3, 0.4]})
print(prueba.escribir("C:\DSSAT45\Soil"))
print(prueba.dic)
prueba.dic = {}
prueba.leer("C:\DSSAT45\Soil")
print(prueba.dic)
