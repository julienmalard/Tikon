import os, shutil
"""
Un "coso", por falta de mejor palabra, se refiere a todo, TODO en el programa
Tikon que representa un aspecto físico del ambiente y que tiene datos. Incluye
paisajes parcelas, variedades de cultivos, suelos, etc. Todos tienen la misma
lógica para leer y escribir sus datos en carpetas externas, tanto como para la
su calibración.
"""


class Coso(object):
    def __init__(self, nombre, carpeta="", reinit=False, dic={}, dic_incert={}):
        self.nombre = nombre
        # La carpeta dónde se ubica este objeto
        self.carpeta = carpeta
        # El nombre del documento de este objeto
        self.documento = os.path.join("Proyectos", carpeta, self.nombre + self.ext)
        self.dic = dic   # Para guardar los variables del coso
        self.dic_incert = dic_incert   # para guardar listas (distribuciones de incertidumbre) para cada variable
        self.reinit = reinit  # Indica si el programa debe reinitializar or utilizar carpetas existentes.

        if not len(dic):
            # Si no se especificó un diccionario, poner el diccionario de base (vacío)
            self.dic = self.dic_base
            if self.reinit:
                if os.path.isdir(self.documento):
                    shutil.rmtree(self.documento)
                if os.path.isfile(self.documento):
                    os.remove(self.documento)
            else:  # Si no estamos reinicializando el objeto, leer el documento
                if os.path.isfile(self.documento):
                    self.leer(self.documento)

    # Función para escribir los datos a un documento externo
    def escribir(self, documento=""):
        if not len(documento):
            documento = self.documento
        # Si necesario, añadir el nombre y la extensión del documento al fin de la carpeta
        if self.ext not in documento.lower():
            if self.nombre not in documento:
                documento += "\\" + self.nombre + self.ext
            else:
                documento += self.ext

        egreso = ""  # Lo que vamos a escribir al documento
        for i in self.dic:
            if len(self.dic[i]):
                egreso += str(i) + ": " + str(self.dic[i]) + "\n"
        if len(self.dic_incert):   # Si existen datos de calibración
            egreso += "*** Incert ***"
            for i in self.dic_incert:
                egreso += str(i) + ": " + str(self.dic_incert[i] + "\n")
        try:
            with open(documento, mode="w") as d:
                d.write(egreso)
        except IOError:
            return "Documento " + documento + " no se pudo abrir para guadar datos."

    # Función para leer los datos desde un documento externo
    def leer(self, documento=""):
        if not len(documento):
            documento = self.documento
        # Si necesario, añadir el nombre y la extensión del documento al fin de la carpeta
        if self.ext not in documento.lower():
            if self.nombre not in documento:
                documento += "\\" + self.nombre + self.ext
            else:
                documento += self.ext

        try:
            with open(documento, mode="r") as d:
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
        except IOError:
            return "Documento " + documento + " no se pudo abrir para leer datos."
