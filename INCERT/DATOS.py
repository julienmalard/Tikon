import os
import csv
import datetime as ft
import numpy as np


class Experimento(object):
    def __init__(símismo, nombre):

        # El nombre de referencia para el experimento
        símismo.nombre = nombre

        # La fecha de referencia (donde tiempo = 0):
        símismo.fecha_ref = None

        # El diccionario de los datos. Tiene una sub-categoría para cada clase de datos
        símismo.datos = {'Organismos': {'tiempo': None,
                                        'obs': {}
                                        },
                         'Cultivos': {'tiempo': None},  # Para hacer: Llenar este.
                         'Aplicaciones': {'tiempo': None}  # Para hacer también
                         }

    def estab_bd_red(símismo, archivo, col_tiempo, fecha_ref=None):
        """

        :param archivo: La ubicación del archivo para leer
        :type archivo: str

        :param col_tiempo: El nombre de la columna que especifica el tiempo de las observaciones.
        :type col_tiempo: str

        :param fecha_ref: Un parámetro opcional para especificar la fecha de referencia (la fecha para cual tiempo = 0
          en la columna 'col_tiempo'.
        :type fecha_ref: ft.date

        """

        # Leer el archivo
        dic_datos = símismo.leer_datos(archivo)

        # Asegurarse de que la columna de datos de tiempo existe
        if col_tiempo not in dic_datos:
            raise ValueError('No se encontró la columna de tiempo en la base de datos.')

        # Calcular la fecha inicial y la lista numérica de las fechas
        fecha_inic_datos, lista_tiempos = símismo.leer_fechas(dic_datos[col_tiempo])

        símismo.datos['Organismos']['tiempo'] = lista_tiempos  # Guardar la lista de fechas numéricas

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
                    # Si era anterior a la nueva fecha, guardar la fecha existente y ajusta los datos de organismos:
                    símismo.datos['Organismos']['tiempo'] += dif

        # Ahora, para cada columna de datos (excluyendo fechas) en la base de datos...
        for col in dic_datos:
            if col != col_tiempo:  # Si no es la columna de fecha...
                símismo.datos['Organismos']['obs'][col] = símismo.texto_a_datos(dic_datos[col])

    def estab_bd_cultivo(símismo, archivo):
        pass  # Para hacer

    def estab_bd_aplic(símismo, archivo):
        pass  # Para hacer

    def mover_fechas(símismo, dif, no_cambiar):
        for bd in símismo.datos:
            if bd != no_cambiar:
                símismo.datos[bd]['tiempo'] += dif

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

                cols = []  # Para guardar los nombres de las columnas
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
        Esta función toma una lista de datos en formato de texto y la convierte en matriz numpy.

        :param datos:
        :type datos: list

        :return: La matriz numpy de los datos. Datos que faltan se representan con np.nan
        :rtype: np.ndarray

        """

        matr = np.array(datos)
        matr[matr == ''] = np.nan

        return matr.astype(np.float)

    @staticmethod
    def leer_fechas(lista):
        """
        Esta función toma una lista de datos de fecha en formato de texto y detecta 1) la primera fecha de la lista,
          y 2) la posición relativa de cada fecha a esta.

        :param lista: Una lista con las fechas en formato de texto
        :type lista: list

        :return: Un tuple de la primera fecha y del vector numpy de la posición de cada fecha relativa a la primera.
        :rtype: (ft.date, np.ndarray())

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
        if all([x.isdigit() for x in lista]):

            # Entonces, no conocemos la fecha inicial
            fecha_inic_datos = None

            # Pero podemos regresar un vector numpy con los números de cada fecha
            lista_datos = np.array(lista, dtype=float)

        else:

            # Sino, intentar de leer el formato de fecha
            fechas = None

            # Intentar con cada formato en la lista de formatos posibles
            for formato in formatos_posibles:

                try:
                    # Intentar de convertir todas las fechas a objetos ft.datetime
                    fechas = [ft.datetime.strptime(x, formato).date() for x in lista]

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

                # La posición relativa de todas las fechas a esta
                lista_datos = [(x - fecha_inic_datos).days for x in fechas]

        return fecha_inic_datos, lista_datos
