import csv
import datetime as ft
import os
from warnings import warn as avisar
import csv

import numpy as np

from tikon.Controles import directorio_base


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
        dic_datos_rae = dict(días=None, cols=None, datos=None, parc=None)
        símismo.datos = {
            'RAE': {'Pobs': dic_datos_rae.copy(),
                    'Muertes': dic_datos_rae.copy(),
                    'Transiciones': dic_datos_rae.copy(),
                    'Crecimiento': dic_datos_rae.copy(),
                    'Reproducción': dic_datos_rae.copy()
                    },
            'Parcelas': {'Nombres': [],
                         'Superficies': None,
                         'Polígonos': None
                         },
            'Cultivos': {},  # Para hacer: Llenar este.
            'Aplicaciones': {}  # Para hacer también

        }

        símismo.proyecto = proyecto

    def obt_datos(símismo, egr):

        dt_rae = símismo.datos['RAE']

        dic_egr = {
            'días': dt_rae[egr]['días'],
            'datos': dt_rae[egr]['datos'],
            'parcela': dt_rae[egr]['parc'],
            'cols': dt_rae[egr]['cols'],
        }

        return dic_egr if dic_egr['días'] is not None else None

    def obt_parcelas(símismo, tipo):
        s_parcelas = set()
        if tipo == '.red':
            for dic in símismo.datos['RAE'].values():
                if dic['parc'] is not None:
                    s_parcelas.update(s_parcelas)

        return s_parcelas

    def obt_info_parcelas(símismo, parc):

        if not isinstance(parc, list):
            parc = [parc]

        parc = [str(x) for x in parc]

        nombres = símismo.datos['Parcelas']['Nombres']  # type: list
        superficies = símismo.datos['Parcelas']['Superficies']  # type: list
        polígonos = símismo.datos['Parcelas']['Polígonos']  # type: list

        dic_info = {}
        for p in parc:
            if p not in nombres:
                avisar('Parcela "{}" no tiene datos en experimento "{}".'.format(p, símismo.nombre))
                continue
            índ_p = nombres.index(p)
            dic_info[p] = {
                'Superficie': superficies[índ_p] if superficies is not None else None,
                'Polígonos': polígonos[índ_p] if superficies is not None else None
            }

        return dic_info

    def superficies(símismo, parc):

        n_parc = len(parc)
        if n_parc == 0:
            return

        superficies = np.empty(n_parc)

        nombres = símismo.datos['Parcelas']['Nombres']  # type: list
        for i, p in enumerate(parc):
            try:
                índ_p = nombres.index(p)
                superficies[i] = símismo.datos['Parcelas']['Superficies'][índ_p]
            except ValueError:
                avisar('Tamaño de parcela no especificado para parcela "{}". Se supondrá un tamaño de 1 ha.'
                       .format(p))
                superficies[i] = 1

        return superficies

    def agregar_pobs(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Pobs',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_muertes(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Muertes',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_reprs(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Reproducción',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_trans_hacía(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Transiciones',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_crec(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Crecimiento',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_parcelas(símismo, archivo):
        pass  # Para hacer

    def _agregar_datos_rae(símismo, archivo, tipo_egr,
                           col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        bd = gen_bd(archivo)

        # Procesar los nombre de columnas
        nombres_cols = bd.sacar_cols()
        if col_tiempo not in nombres_cols:
            raise ValueError
        if col_parc is not None and col_parc not in nombres_cols:
            raise ValueError
        if cols_etps is None:
            cols_etps = nombres_cols.copy()
            cols_etps.remove(col_tiempo)
            if col_parc is not None:
                cols_etps.remove(col_parc)
        else:
            if not isinstance(cols_etps, list):
                cols_etps = [cols_etps]
            for c in cols_etps:
                if c not in nombres_cols:
                    raise ValueError

        n_obs = bd.n_obs

        if col_parc is not None:
            v_parc = bd.obt_datos_tx(cols=col_parc)
        else:
            v_parc = np.ones(n_obs)
        parc_únicas = np.unique(v_parc)
        n_parc = parc_únicas.shape[0]

        v_días = bd.obt_días(col=col_tiempo)
        días_únicos = np.unique(v_días)
        n_días = días_únicos.shape[0]

        n_etps = len(cols_etps)

        m_obs = bd.obt_datos(cols=cols_etps)  # Eje 0: col, eje 1: día/parcela
        np.multiply(m_obs, factor, out=m_obs)

        if cód_na is not None:
            m_obs[m_obs == cód_na] = np.nan

        matr_obs = np.empty((n_parc, n_etps, n_días))
        matr_obs[:] = np.nan

        for c in range(m_obs.shape[0]):
            matr_obs[v_parc, [c] * n_obs, v_días] = m_obs[c, :]

        dic_datos = símismo.datos['RAE'][tipo_egr]
        dic_datos['cols'] = cols_etps
        dic_datos['días'] = días_únicos
        dic_datos['datos'] = matr_obs
        dic_datos['parc'] = parc_únicas

    def agregar_orgs(símismo, archivo, col_tiempo, factor=1, col_parcela=None, fecha_ref=None):
        """
        Esta función establece la base de datos para las observaciones de organismos en el campo.

        :param archivo: La ubicación del archivo para leer
        :type archivo: str

        :param col_tiempo: El nombre de la columna que especifica el tiempo de las observaciones.
        :type col_tiempo: str

        :param factor: El factor con el cual multiplicar las observaciones de poblaciones (útil para compatibilidad
          de unidades).
        :type factor: float

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
            raise ValueError('No se encontró la columna de tiempo "{}" en la base de datos.'.format(col_tiempo))

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

                # Multiplicar por el factor
                np.multiply(matr, factor, out=matr)

                # Guardar, evitando fracciones de insectos
                símismo.datos['Organismos']['obs'][col] = matr.round()

    def agregar_cultivos(símismo, archivo):
        pass  # Para hacer

    def agregar_aplicaciones(símismo, archivo):
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


def gen_bd(archivo):
    """

    :param archivo:
    :type archivo: str
    :return:
    :rtype: BD
    """
    ext = os.path.splitext(archivo)[1]
    if ext == '.txt' or ext == '.csv':
        return BDtexto(archivo)
    elif ext == '.sql':
        return BDsql(archivo)
    else:
        raise ValueError


class BD(object):
    def __init__(símismo, archivo):
        símismo.archivo = archivo

        if not os.path.isfile(archivo):
            raise FileNotFoundError

        símismo.n_obs = símismo.calc_n_obs()

    def sacar_cols(símismo):
        """

        :return:
        :rtype: list[str]
        """
        raise NotImplementedError

    def obt_datos(símismo, cols):
        """

        :param cols:
        :type cols: list[str] | str
        :return:
        :rtype: np.ndarray
        """
        raise NotImplementedError

    def obt_datos_tx(símismo, cols):
        """

        :param cols:
        :type cols: list[str] | str
        :return:
        :rtype: list
        """
        raise NotImplementedError

    def obt_días(símismo, col):
        """

        :param col:
        :type col: str
        :return:
        :rtype: np.ndarray
        """
        raise NotImplementedError

    def calc_n_obs(símismo):
        """

        :return:
        :rtype: int
        """
        raise NotImplementedError


class BDtexto(BD):
    def obt_días(símismo, col):
        pass

    def calc_n_obs(símismo):
        with open(símismo.archivo) as d:
            n_filas = sum(1 for f in d if len(f)) - 1  # Sustrayemos la primera fila

        return n_filas

    def obt_datos(símismo, cols):
        if not isinstance(cols, list):
            cols = [cols]

        m_datos = np.empty((len(cols), símismo.n_obs))

        with open(símismo.archivo) as d:
            lector = csv.DictReader(d)
            for n_f, f in enumerate(lector):
                m_datos[:, n_f] = [float(f[c]) if f[c] != '' else np.nan for c in cols]

        if len(cols) == 1:
            m_datos = m_datos[0]

        return m_datos

    def obt_datos_tx(símismo, cols):
        if not isinstance(cols, list):
            cols = [cols]

        l_datos = [['']*len(cols)]*símismo.n_obs

        with open(símismo.archivo) as d:
            lector = csv.DictReader(d)
            for n_f, f in enumerate(lector):
                for i_c, c in enumerate(cols):
                    l_datos[i_c][n_f] = [f[c] for c in cols]

        if len(cols) == 1:
            l_datos = l_datos[0]

        return l_datos

    def sacar_cols(símismo):

        with open(símismo.archivo) as d:
            lector = csv.reader(d)

            nombres_cols = next(lector)

        return nombres_cols


class BDsql(BD):
    def calc_n_obs(símismo):
        pass

    def obt_días(símismo, col):
        pass

    def obt_datos(símismo, cols):
        pass

    def obt_datos_tx(símismo, cols):
        pass

    def sacar_cols(símismo):
        pass
