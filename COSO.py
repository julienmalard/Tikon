import os
import shutil
import json
import datetime as ft
# import Bayesiano.CALIB

"""
Un "coso", por falta de mejor palabra, se refiere a todo, TODO en el programa
Tikon que representa un aspecto físico del ambiente y que tiene datos. Incluye
paisajes parcelas, variedades de cultivos, suelos, etc. Todos tienen la misma
lógica para leer y escribir sus datos en carpetas externas, tanto como para la
su calibración.
"""


class Coso(object):
    def __init__(símismo, nombre, ext, directorio, reinic=False):
        símismo.ext = ext  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
        # La carpeta dónde se ubica este objeto
        símismo.directorio = directorio
        # El nombre del objeto
        símismo.nombre = nombre
        # El nombre del documento utilizado para guardar este objeto
        símismo.dirección = os.path.join("Proyectos", directorio, símismo.nombre + símismo.ext)

        # reinic Indica si el programa debe reinitializar or utilizar carpetas existentes.
        # Borrar/crear de nuevo o buscar/leer la carpeta de datos, si existe
        if reinic:  # Si estamos reinicializando el objeto, borrar y recrear el directorio
            if os.path.isdir(símismo.dirección):
                shutil.rmtree(símismo.dirección)
            if os.path.isfile(símismo.dirección):
                os.remove(símismo.dirección)
            # Y crear el directorio/documento de nuevo
            os.getcwd()
            os.makedirs(símismo.directorio)
        else:  # Si no estamos reinicializando el objeto, leer el documento, si existe
            if os.path.isfile(símismo.dirección):
                símismo.leer(símismo.dirección)
            else:  # Si no existe
                os.makedirs(símismo.directorio)

    # Función para escribir los datos a un documento externo
    def escribir(símismo, documento=""):
        if not len(documento):
            documento = símismo.dirección
        # Si necesario, añadir el nombre y la extensión del documento al fin de la carpeta
        if símismo.ext not in documento.lower():
            if símismo.nombre not in documento:
                documento += "\\" + símismo.nombre + símismo.ext
            else:
                documento += símismo.ext
        # Para guardar el diccionario de incertidumbre:
        documento_incert = documento + "i"

        # Para guardar diccionarios de objetos, utilizamos el módulo JSON que escribe los diccionarios en
        # formato JSON, un formato fácil a leer por humanos ya varios programas (JavaScript, Python, etc.)

        # Primero, convertimos objetos fechas en forma "cadena"
        dic_temp = símismo.dic.copy()  # Para no afectar el diccionario del objeto sí mismo
        dic_incert_temp = símismo.dic_incert.copy()

        def convertir_fechas(obj):
            for i in obj:
                if type(obj[i]) is list or type(obj[i]) is dict:
                    convertir_fechas(obj[i])  # Buscar en cada sub-diccionario o sub-lista del objeto
                elif type(obj[i]) is ft.datetime:
                    obj[i] = obj[i].strftime('%Y-%m-%d')  # Convertir fechas en formato cadena

        convertir_fechas(dic_temp)
        convertir_fechas(dic_incert_temp)

        try:
            with open(documento, mode="w") as d:
                json.dump(dic_temp, d)
        except IOError:
            return "Documento " + documento + " no se pudo abrir para guadar datos."

        try:
            with open(documento_incert, mode="w") as d:
                json.dump(dic_incert_temp, d)
        except IOError:
            return "Documento " + documento + " no se pudo abrir para guadar datos de incertidumbre."

    # Función para leer los datos desde un documento externo
    def leer(símismo, documento=""):
        if not len(documento):
            documento = símismo.dirección
        # Si necesario, añadir el nombre y la extensión del documento al fin de la carpeta
        if símismo.ext not in documento.lower():
            if símismo.nombre not in documento:
                documento += "\\" + símismo.nombre + símismo.ext
            else:
                documento += símismo.ext
        documento_incert = documento + "i"

        try:
            with open(documento, mode="r") as d:
                símismo.dic = json.load(d)
        except IOError:
            return "Documento " + documento + " no se pudo abrir para leer datos."

        try:
            with open(documento_incert, mode="r") as d:
                símismo.dic_incert = json.load(d)
        except IOError:
            return "Documento " + documento + " no se pudo abrir para leer datos de incertidumbre."

        # Convertir las fechas en objetos de fechas dinámicos
        def convertir_fechas(obj):
            f = ft.datetime(1, 1, 1)
            for i in obj:
                if type(obj[i]) is list or type(obj[i]) is dict:
                    convertir_fechas(obj[i])
                elif type(obj[i]) is str:
                    try:
                        obj[i] = f.strptime(obj[i], '%Y-%m-%d')
                    except ValueError:
                        pass

        convertir_fechas(símismo.dic)
        convertir_fechas(símismo.dic_incert)

    def inic_calibr(símismo, datos):
        # Si no existe diccionario de valores de incertidumbre, copiar la estructura del diccionario ordinario
        if not len(símismo.dic_incert):
            símismo.dic_incert = símismo.dic

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

            dic_lista(símismo.dic_incert)

'''
    def calib(self,):
        pass
'''
