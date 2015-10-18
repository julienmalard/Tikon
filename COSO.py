import os, shutil
# import Bayesiano.CALIB
import json
"""
Un "coso", por falta de mejor palabra, se refiere a todo, TODO en el programa
Tikon que representa un aspecto físico del ambiente y que tiene datos. Incluye
paisajes parcelas, variedades de cultivos, suelos, etc. Todos tienen la misma
lógica para leer y escribir sus datos en carpetas externas, tanto como para la
su calibración.
"""


class Coso(object):
    def __init__(simismo, nombre, carpeta="", reinit=False, dic={}, dic_incert={}):
        simismo.nombre = nombre
        # La carpeta dónde se ubica este objeto
        simismo.carpeta = carpeta
        # El nombre del documento de este objeto
        simismo.documento = os.path.join("Proyectos", carpeta, simismo.nombre + simismo.ext)
        simismo.dic = simismo.dic_base   # Para guardar los variables del coso
        if len(dic):
            for var in dic:
                simismo.dic[var] = dic[var]
        simismo.dic_incert = dic_incert   # para guardar listas (distribuciones de incertidumbre) para cada variable

        simismo.reinit = reinit  # Indica si el programa debe reinitializar or utilizar carpetas existentes.

        # Borrar/crear de nuevo o buscar/leer la carpeta de datos, si existe
        if simismo.reinit:  # Si estamos reinicializando el objeto, borrar y recrear la carpeta
            if os.path.isdir(simismo.documento):
                shutil.rmtree(simismo.documento)
            if os.path.isfile(simismo.documento):
                os.remove(simismo.documento)
        else:  # Si no estamos reinicializando el objeto, leer el documento
            if os.path.isfile(simismo.documento):
                simismo.leer(simismo.documento)

    # Función para escribir los datos a un documento externo
    def escribir(simismo, documento=""):
        if not len(documento):
            documento = simismo.documento
        # Si necesario, añadir el nombre y la extensión del documento al fin de la carpeta
        if simismo.ext not in documento.lower():
            if simismo.nombre not in documento:
                documento += "\\" + simismo.nombre + simismo.ext
            else:
                documento += simismo.ext
        # Para guardar el diccionario de incertidumbre:
        documento_incert = documento + "i"

        # Para guardar diccionarios de objetos, utilizamos el módulo JSON que escribe los diccionarios en
        # formato JSON, un formato fácil a leer por humanos ya varios programas (JavaScript, Python, etc.)
        try:
            with open(documento, mode="w") as d:
                json.dump(simismo.dic, d)
        except IOError:
            return "Documento " + documento + " no se pudo abrir para guadar datos."

        try:
            with open(documento_incert, mode="w") as d:
                json.dump(simismo.dic_incert, d)
        except IOError:
            return "Documento " + documento + " no se pudo abrir para guadar datos de incertidumbre."

    # Función para leer los datos desde un documento externo
    def leer(simismo, documento=""):
        if not len(documento):
            documento = simismo.documento
        # Si necesario, añadir el nombre y la extensión del documento al fin de la carpeta
        if simismo.ext not in documento.lower():
            if simismo.nombre not in documento:
                documento += "\\" + simismo.nombre + simismo.ext
            else:
                documento += simismo.ext
        documento_incert = documento + "i"

        try:
            with open(documento, mode="r") as d:
                simismo.dic = json.load(d)
        except IOError:
            return "Documento " + documento + " no se pudo abrir para leer datos."

        try:
            with open(documento_incert, mode="r") as d:
                simismo.dic_incert = json.load(d)
        except IOError:
            return "Documento " + documento + " no se pudo abrir para leer datos de incertidumbre."

    def inic_calibr(simismo, datos):
        # Si no existe diccionario de valores de incertidumbre, copiar la estructura del diccionario ordinario
        if not len(simismo.dic_incert):
            simismo.dic_incert = simismo.dic

            # Para cada variable numérico en el diccionario, crear una lista para contener varios valores posibles
            # del variable (análisis de incertidumbre)
            def dic_lista(d):
                for ll, v in d.items():
                    if type(v) is float or type(v) is int:  # Si el valor es numérico
                        d[ll] = [v]  # poner el valor en una lista
                    # Si el elemento es una lista no vacía con valores numéricos
                    if type(v) is list and len(v) and (type(v[0]) is float or type(v[0]) is int):
                        d[ll] = [v]
                    elif type(v) is dict:
                        dic_lista(d)

            dic_lista(simismo.dic_incert)

'''
    def calib(self,):
        pass
'''
