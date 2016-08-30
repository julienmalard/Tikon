import csv
import datetime as ft
import os

import numpy as np

from Controles import directorio_base


class Experimento(object):
    def __init__(símismo, nombre, proyecto=None):
        """

        :param nombre:
        :type nombre: str

        :param proyecto:
        :type proyecto: str
        """

        # El nombre de referencia para el experimento
        símismo.nombre = nombre

        # La fecha de referencia (donde tiempo = 0):
        símismo.fecha_ref = None

        # El diccionario de los datos. Tiene una sub-categoría para cada clase de datos.
        símismo.datos = {'Organismos': {'tiempo': None,
                                        'obs': {},
                                        'parcelas': []
                                        },
                         'Cultivos': {'tiempo': None},  # Para hacer: Llenar este.
                         'Aplicaciones': {'tiempo': None},  # Para hacer también
                         'Parcelas': {}  # Para hacer también
                         }

        símismo.proyecto = proyecto

    def agregar_orgs(símismo, archivo, col_tiempo, col_parcela=None, fecha_ref=None):
        """
        Esta función establece la base de datos para las observaciones de organismos en el campo.

        :param archivo: La ubicación del archivo para leer
        :type archivo: str

        :param col_tiempo: El nombre de la columna que especifica el tiempo de las observaciones.
        :type col_tiempo: str

        :param col_parcela: Una columna, si existe, que referencia la parcela.
        :type col_parcela: str

        :param fecha_ref: Un parámetro opcional para especificar la fecha de referencia (la fecha para cual tiempo = 0
          en la columna 'col_tiempo').
        :type fecha_ref: ft.date

        """

        # Borrar datos anteriores, si habían
        símismo.datos['Organismos']['tiempo'] = None
        símismo.datos['Organismos']['obs'].clear()
        símismo.datos['Organismos']['parcelas'].clear()

        archivo = símismo.prep_archivo(archivo)

        # Leer el archivo
        dic_datos = símismo.leer_datos(archivo)

        # Asegurarse de que la columna de datos de tiempo existe
        if col_tiempo not in dic_datos:
            raise ValueError('No se encontró la columna de tiempo en la base de datos.')

        # Calcular la fecha inicial (objeto de fecha) y el vector numérico de las fechas
        fecha_inic_datos, vec_tiempos, vec_tiempos_únic = símismo.leer_fechas(dic_datos[col_tiempo])

        símismo.datos['Organismos']['tiempo'] = vec_tiempos_únic  # Guardar la lista de fechas numéricas

        # Si el usuario especificó una fecha inicial, usarla
        if fecha_ref is not None:
            fecha_inic_datos = fecha_ref

        # Si las fechas de la base de datos tienen una fecha inicial
        if fecha_inic_datos is not None:

            if símismo.fecha_ref is None:
                # Si no había fecha de referencia para este experimento...

                símismo.fecha_ref = fecha_inic_datos  # Guardarla

            else:

                # Sino, calcular la diferencia entre la fecha de referencia del experimento y la fecha de referencia
                # de la base de datos de organismos
                dif = (fecha_inic_datos - símismo.fecha_ref).days

                if dif < 0:
                    # Si la fecha existente era posterior a la nueva fecha:
                    símismo.fecha_ref = fecha_inic_datos  # Usar la nueva fecha como referencia

                    # Y ajustar las fechas de las otras partes de este experimento
                    símismo.mover_fechas(dif=dif, no_cambiar='Organismos')

                else:
                    # Si era anterior a la nueva fecha, guardar la fecha existente y ajustar los datos de organismos:
                    símismo.datos['Organismos']['tiempo'] += dif

        # Ahora, para cada columna de datos (excluyendo fechas) en la base de datos...
        for col in dic_datos:
            if col != col_tiempo and col != col_parcela:  # Si no es la columna de fecha o de parcelas...

                if col_parcela is None:
                    # Si no hay columna de parcelas...
                    matr = símismo.texto_a_datos(dic_datos[col])[np.newaxis, :]
                    símismo.datos['Organismos']['parcelas'] = ['1']  # Nombre genérico para parcela única

                else:
                    # Si hay más que una parcela...
                    parcelas = list(set(dic_datos[col_parcela]))
                    parcelas.sort()
                    símismo.datos['Organismos']['parcelas'] = parcelas
                    vec_parc = dic_datos[col_parcela]

                    matr = np.empty((len(parcelas), len(vec_tiempos_únic)))
                    matr.fill(np.nan)

                    for n, p in enumerate(parcelas):
                        vec_datos = dic_datos[col][np.where(vec_parc == p)]

                        tiempos_parc = dic_datos[col][np.where(vec_parc == p)]

                        matr[n, tiempos_parc] = vec_datos

                símismo.datos['Organismos']['obs'][col] = matr.round()  # Evitar fracciones de insectos

    def agregar_cultivos(símismo, archivo):
        pass  # Para hacer

    def agregar_aplicaciones(símismo, archivo):
        pass  # Para hacer

    def agregar_parcelas(símismo, archivo):
        pass  # Para hacer

    def mover_fechas(símismo, dif, no_cambiar):
        for bd in símismo.datos:
            if bd != no_cambiar:
                símismo.datos[bd]['tiempo'] += dif

    def prep_archivo(símismo, archivo):

        if os.path.splitdrive(archivo)[0] == '':
            # Si no se especifica directorio, se usará el directorio de Proyectos de Tiko'n.
            archivo = os.path.join(directorio_base, 'Proyectos', símismo.proyecto, archivo)

        return archivo

    @staticmethod
    def leer_datos(archivo):
        """
        Esta función lee una base de datos y devuelve un diccionario con el formato:
          {nombre_columna1: [lista de datos],
           nombre_columna2: [lista de datos],
           ...
           }

           Los datos de presentan todos en formato texto.

        :param archivo: La dirección del archivo para leer.
        :type archivo: str

        :return: Un diccionario de los datos.
        :rtype: dict

        """

        # Para guardar los datos leidos
        datos = {}

        # Detectar el tipo del archivo (por su extensión)
        tipo = os.path.splitext(archivo)[1]

        # Leer el archivo según su tipo.
        if tipo == '.csv':
            with open(archivo, newline='') as d:

                l = csv.reader(d)  # El lector de csv

                valores = []  # Para guardar la lista de datos de cada línea

                # Guardar la primera fila como nombres de columnas
                cols = next(l)

                # Para cada fila que sigue en el csv...
                for f in l:
                    valores.append(f)

            for n, col in enumerate(cols):
                datos[col] = [x[n] for x in valores]

        else:
            # Si quieres implementar un otro tipo de base de datos (digamos .xls, .xlsx, MySQL, etc.), lo puedes
            # hacer tanto como devuelve el diccionario 'datos' con el formato especificado arriba.

            raise NotImplementedError('No puedes cargar archivos de tipo \'%s\' todavía.' % tipo)

        return datos

    @staticmethod
    def texto_a_datos(datos):
        """
        Esta función toma una lista de datos en formato de texto y la convierte en matriz numpy. Valores vacíos ("") se
          convertirán a np.nan.

        :param datos: La lista de datos en formato de texto.
        :type datos: list

        :return: La matriz numpy de los datos. Datos que faltan se representan con np.nan
        :rtype: np.ndarray

        """

        matr = np.array(datos)
        matr[matr == ''] = np.nan

        return matr.astype(np.float)

    @staticmethod
    def leer_fechas(lista_fechas):
        """
        Esta función toma una lista de datos de fecha en formato de texto y detecta 1) la primera fecha de la lista,
          y 2) la posición relativa de cada fecha a esta.

        :param lista_fechas: Una lista con las fechas en formato de texto
        :type lista_fechas: list

        :return: Un tuple de la primera fecha, del vector numpy de la posición de cada fecha relativa a la primera,
          y del vector numpy de las fechas (numéricas) únicas.
        :rtype: (ft.date, np.ndarray, np.ndarray)

        """

        # Una lista de lso formatos de fecha posibles. Esta función intentará de leer los datos de fechas con cada
        # formato en esta lista y, si encuentra un que funciona, parará allí.
        separadores = ['-', '/', ' ', '.']

        f = ['%d{0}%m{0}%y', '%m{0}%d{0}%y', '%d{0}%m{0}%Y', '%m{0}%d{0}%Y',
             '%d{0}%b{0}%y', '%m{0}%b{0}%y', '%d{0}%b{0}%Y', '%b{0}%d{0}%Y',
             '%d{0}%B{0}%y', '%m{0}%B{0}%y', '%d{0}%B{0}%Y', '%m{0}%B{0}%Y',
             '%y{0}%m{0}%d', '%y{0}%d{0}%m', '%Y{0}%m{0}%d', '%Y{0}%d{0}%m',
             '%y{0}%b{0}%d', '%y{0}%d{0}%b', '%Y{0}%b{0}%d', '%Y{0}%d{0}%b',
             '%y{0}%B{0}%d', '%y{0}%d{0}%B', '%Y{0}%B{0}%d', '%Y{0}%d{0}%B']

        formatos_posibles = [x.format(s) for s in separadores for x in f]

        # Primero, si los datos de fechas están en formato simplemente numérico...
        if all([x.isdigit() for x in lista_fechas]):

            # Entonces, no conocemos la fecha inicial
            fecha_inic_datos = None

            # Convertir a vector Numpy
            vector_fechas = np.array(lista_fechas, dtype=int)

            # Quitar duplicaciones
            list(set(lista_fechas)).sort()

            # Pero podemos regresar un vector numpy con los números de cada fecha
            vector_únicas = np.array(lista_fechas, dtype=int)

        else:
            # Sino, intentar de leer el formato de fecha
            fechas = None

            # Intentar con cada formato en la lista de formatos posibles
            for formato in formatos_posibles:

                try:
                    # Intentar de convertir todas las fechas a objetos ft.datetime
                    fechas = [ft.datetime.strptime(x, formato).date() for x in lista_fechas]

                    # Si funcionó, parar aquí
                    break

                except ValueError:
                    # Si no funcionó, intentar el próximo formato
                    continue

            # Si todavía no lo hemos logrado, tenemos un problema.
            if fechas is None:
                raise ValueError('No puedo leer los datos de fechas. ¿Mejor le eches un vistazo a tu base de datos?')

            else:
                # Pero si está bien, ya tenemos que encontrar la primera fecha y calcular la posición relativa de las
                # otras con referencia en esta.

                # La primera fecha de la base de datos. Este paso se queda un poco lento, así que para largas bases de
                # datos podría ser útil suponer que la primera fila también contiene la primera fecha.
                fecha_inic_datos = min(fechas)

                # Si tenemos prisa, mejor lo hagamos así:
                # fecha_inic_datos = min(fechas[0], fechas[-1])

                # La posición relativa de todas las fechas a esta
                lista_fechas = [(x - fecha_inic_datos).days for x in fechas]

                # Convertir a vector Numpy
                vector_fechas = np.array(lista_fechas, dtype=int)

                # Quitar duplicaciones
                list(set(lista_fechas)).sort()

                # Convertir a vector Numpy
                vector_únicas = np.array(lista_fechas, dtype=int)

        return fecha_inic_datos, vector_fechas, vector_únicas
