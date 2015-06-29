# Un "coso", por falta de mejor palabra, se refiere a todo, TODO en el programa
# Tikon que representa un aspecto físico del ambiente y que tiene datos. Incluye
# paisajes parcelas, variedades de cultivos, suelos, etc. Todos tienen la misma
# lógica para leer y escribir sus datos en carpetas externas, tanto como para la
# su calibración.


class Coso(object):
    # dic puede ser un diccionario (de datos) o la dirección de un documento (que contiene los datos)
    def __init__(self, nombre, dic={}, dic_incert={}):
        self.nombre = nombre
        self.dic = dic   # Para guardar los variables del coso
        self.dic_incert = dic_incert   # para guardar listas (distribuciones de incertidumbre) para cada variable
        if type(dic) is dict:
            # Si no se especificó un diccionario, poner el diccionario de base (vacío)
            if not len(dic): self.dic = self.dic_base
        elif type(dic) is str:
            self.leer(dic)  # Si se especificó un documento externo para el diccionario, leerlo
        else:
            print("Diccionario inválido para objeto " + self.nombre + ".")

    # Función para escribir los datos a un documento externo
    def escribir(self, carpeta=""):
        # Si necesario, añadir el nombre del documento al fin de la carpeta
        if self.ext not in carpeta.lower():
            if self.nombre not in carpeta:
                carpeta += "\\" + self.nombre + self.ext
            else:
                carpeta += self.ext
        egreso = ""  # Lo que vamos a escribir al documento
        for i in self.dic:
            if len(self.dic[i]):
                egreso += str(i) + ": " + str(self.dic[i]) + "\n"
        if len(self.dic_incert):   # Si existen datos de calibración
            egreso += "*** Incert ***"
            for i in self.dic_calib:
                egreso += str(i) + ": " + str(self.dic_calib[i] + "\n")
        try:
            with open(carpeta, mode="w") as d:
                d.write(egreso)
        except IOError:
            return "Carpeta " + carpeta + " no se pudo abrir."

    # Función para leer los datos desde un documento externo
    def leer(self, carpeta):
        # Si necesario, añadir el nombre del documento al fin de la carpeta
        if self.ext not in carpeta.lower():
            if self.nombre not in carpeta:
                carpeta += "\\" + self.nombre + self.ext
            else:
                carpeta += self.ext
        with open(carpeta, mode="r") as d:
            sec_incert = False  # Verificar si estamos la sección de datos ordinarios o datos de incertidumbre
            for línea in d:
                if len(línea):
                    var, valor = línea.split(':', 1)
                    valor = valor.replace("\n", "")
                    if "***" not in línea:
                        if not sec_incert:
                            self.dic[var] = eval(valor)
                        else:
                            self.dic_incert[var] = eval(valor)
                    else:
                        sec_incert = True
