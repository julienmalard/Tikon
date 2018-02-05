import ast
import csv
import datetime as ft
import os
from warnings import warn as avisar

import numpy as np

from tikon.Controles import directorio_base


class Experimento(object):
    """
    Un `Experimento` permite conectar objetos `Simulable` a datos observados y a acciones de manejo de la parcela.
    """

    def __init__(símismo, nombre, proyecto=None):
        """
        Inicializa el Experimento, con su diccionario de datos inicialmente vacío.

        :param nombre: El nombre del Experimento.
        :type nombre: str

        :param proyecto: El proyecto al cual pertenece este Experimento.
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

    def obt_datos_rae(símismo, egr, t_final=None, por_parcela=False):
        """
        Saca datos de Red AgroEcológica.

        :param egr: El tipo de egreso de interés.
        :type egr: str

        :param por_parcela: Si querremos datos en unidades de indivíduos (o eventos) por parcela (y no por ha).
        :type por_parcela: bool

        :return: El diccionario de datos
        :rtype: dict
        """

        # El diccionario de interés
        dt_rae = símismo.datos['RAE']

        # El diccionario que vamos a devolver
        dic_egr = {
            'días': dt_rae[egr]['días'],
            'datos': dt_rae[egr]['datos'],
            'parc': dt_rae[egr]['parc'],
            'cols': dt_rae[egr]['cols'],
        }

        # Si encontramos datos...
        if dic_egr['días'] is not None:

            # Si hay que generar datos por parcela (y no por hectárea)...
            if por_parcela:
                # Simplificar el código
                datos = dic_egr['datos']  # type: np.ndarray
                parc = dic_egr['parc'].tolist()  # type: str

                # Calcular superficies
                superficies = símismo.superficies(parc=parc)

                # Convertir a individuos por parcela
                np.multiply(datos, superficies, out=datos)

                # No hay nano-zorros en este mundo
                dic_egr['datos'] = datos.astype(int)

            if t_final is not None:
                dic_egr['datos'] = dic_egr['datos'][..., dic_egr['días'] < t_final]
                dic_egr['días'] = dic_egr['días'][dic_egr['días'] < t_final]
        else:
            # Si no encontramos datos, bueno, pués no encontramos datos.
            dic_egr = None

        # Si encontramos algo, devolvémoslo
        return dic_egr

    def obt_parcelas(símismo, tipo):
        """
        Devuelve una lista de parcelas únicas que aparecen en los datos para el tipo de Simulable especificado.

        :param tipo: La extensión del tipo de simulable.
        :type tipo: str

        :return: Una lista de parcelas únicas con datos disponibles.
        :rtype: lista
        """

        c_parcelas = set()
        if tipo == '.red':
            for dic in símismo.datos['RAE'].values():
                if dic['parc'] is not None:
                    c_parcelas.update(dic['parc'].tolist())
        else:
            raise ValueError

        return sorted(c_parcelas)

    def obt_info_parcelas(símismo, parc):
        """
        Devuelve información de una parcela o lista de parcelas.

        :param parc: La(s) parcela(s) de interés.
        :type parc: str | list[str]

        :return: Un diccionario con información de cada parcela.
        :rtype: dict
        """

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
        """
        Devuelve las superficies de unas parcelas de interés.

        :param parc: La(s) parcela(s) de interés.
        :type parc: str | list[str]

        :return: Un vector de superficies de las parcelas.
        :rtype: np.ndarray
        """

        # Asegurar el formato de las parcelas
        if not isinstance(parc, list):
            parc = [parc]

        n_parc = len(parc)  # El número de parcelas

        # Una matriz vacía para las superficies
        superficies = np.empty(n_parc)

        # El nombre de las superficies en este experimento
        nombres = símismo.datos['Parcelas']['Nombres']  # type: list

        # Si no hay superficies en este experimento, establecer un valor de 1 ha automáticamente y avisarle al usuario.
        if símismo.datos['Parcelas']['Superficies'] is None:
            avisar('Tamaños de parcelas no especificados. Se supondrá un tamaño de 1 ha.')
            superficies[:] = 1

        else:
            # Si al contrario tenemos datos de superficies...

            for i, p in enumerate(parc):
                # Para cada parcela de interés...

                # Intentar leer sus datos de superficie
                try:
                    índ_p = nombres.index(p)  # Puede causar un ValueError aquí...
                    sfc = símismo.datos['Parcelas']['Superficies'][índ_p]
                    if sfc == np.nan:
                        raise ValueError  # ...¡o aquí!
                    else:
                        superficies[i] = sfc

                except ValueError:
                    # Si no funcionó, darle un valor de 1 ha y avisarle al usuario
                    avisar('Tamaño de parcela no especificado para parcela "{}". Se supondrá un tamaño de 1 ha.'
                           .format(p))
                    superficies[i] = 1

        # Devolver el vector de superficies.
        return superficies

    def tiempo_final(símismo, tipo):

        if tipo == '.red':
            t_final = 0
            for dic in símismo.datos['RAE'].values():  # type: dict[np.ndarray]
                if dic['días'] is not None:
                    t_final = np.max(dic['días'], t_final)
        else:
            raise ValueError

        return t_final

    def agregar_pobs(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        """
        Esta función permite agregar datos de poblaciones desde un archivo de datos externo.

        :param archivo: El archivo con los datos.
        :type archivo: str

        :param col_tiempo: La columna con datos de tiempo.
        :type col_tiempo: str

        :param col_parc: La columna (opcional) con datos de parcela.
        :type col_parc: str

        :param cols_etps: Las columnas con las observaciones. Un valor de `None` utilizará todas las columnas
        disponibles.
        :type cols_etps: list[str] | str

        :param factor: Un factor de conversión para llegar a indivíduos / ha.
        :type factor: float | int

        :param cód_na: El código que representa valores que faltan en la base de datos.
        :type cód_na: str | float | int
        """
        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Pobs',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_muertes(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        """
        Esta función permite agregar datos de muertes desde un archivo de datos externo.

        :param archivo: El archivo con los datos.
        :type archivo: str

        :param col_tiempo: La columna con datos de tiempo.
        :type col_tiempo: str

        :param col_parc: La columna (opcional) con datos de parcela.
        :type col_parc: str

        :param cols_etps: Las columnas con las observaciones. Un valor de `None` utilizará todas las columnas
        disponibles.
        :type cols_etps: list[str] | str

        :param factor: Un factor de conversión para llegar a indivíduos / ha.
        :type factor: float | int

        :param cód_na: El código que representa valores que faltan en la base de datos.
        :type cód_na: str | float | int
        """
        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Muertes',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_reprs(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        """
        Esta función permite agregar datos de reproducciones desde un archivo de datos externo.

        :param archivo: El archivo con los datos.
        :type archivo: str

        :param col_tiempo: La columna con datos de tiempo.
        :type col_tiempo: str

        :param col_parc: La columna (opcional) con datos de parcela.
        :type col_parc: str

        :param cols_etps: Las columnas con las observaciones. Un valor de `None` utilizará todas las columnas
        disponibles.
        :type cols_etps: list[str] | str

        :param factor: Un factor de conversión para llegar a indivíduos / ha.
        :type factor: float | int

        :param cód_na: El código que representa valores que faltan en la base de datos.
        :type cód_na: str | float | int
        """
        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Reproducción',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_trans_hacía(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        """
        Esta función permite agregar datos de transiciones (hacia la etapa especificada) desde un archivo de datos
        externo.

        :param archivo: El archivo con los datos.
        :type archivo: str

        :param col_tiempo: La columna con datos de tiempo.
        :type col_tiempo: str

        :param col_parc: La columna (opcional) con datos de parcela.
        :type col_parc: str

        :param cols_etps: Las columnas con las observaciones. Un valor de `None` utilizará todas las columnas
        disponibles.
        :type cols_etps: list[str] | str

        :param factor: Un factor de conversión para llegar a indivíduos / ha.
        :type factor: float | int

        :param cód_na: El código que representa valores que faltan en la base de datos.
        :type cód_na: str | float | int
        """
        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Transiciones',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_crec(símismo, archivo, col_tiempo, col_parc=None, cols_etps=None, factor=1, cód_na=None):
        """
        Esta función permite agregar datos de crecimiento de poblaciones desde un archivo de datos externo.

        :param archivo: El archivo con los datos.
        :type archivo: str

        :param col_tiempo: La columna con datos de tiempo.
        :type col_tiempo: str

        :param col_parc: La columna (opcional) con datos de parcela.
        :type col_parc: str

        :param cols_etps: Las columnas con las observaciones. Un valor de `None` utilizará todas las columnas
        disponibles.
        :type cols_etps: list[str] | str

        :param factor: Un factor de conversión para llegar a indivíduos / ha.
        :type factor: float | int

        :param cód_na: El código que representa valores que faltan en la base de datos.
        :type cód_na: str | float | int
        """

        símismo._agregar_datos_rae(archivo=archivo, tipo_egr='Crecimiento',
                                   col_tiempo=col_tiempo, col_parc=col_parc, cols_etps=cols_etps,
                                   factor=factor, cód_na=cód_na)

    def agregar_parcelas(símismo, archivo, col_nombres, col_superficies=None, col_polígonos=None, recalc_superf=False):
        """
        Esta función agrega información de parcelas desde un documento externo.

        :param archivo: El archivo de la base de datos.
        :type archivo: str

        :param col_nombres: El nombre de la columna con los nombres de las parcelas.
        :type col_nombres: str

        :param col_superficies: El nombre de la columna con datos de superficies para cada polígono (opcional).
        :type col_superficies: str

        :param col_polígonos: El nombre de la columna con coordenadas de polígonos (opcional).
        :type col_polígonos: str

        :param recalc_superf: Si hay que recalcular las superficies a parte de la información de polígono, si es que
        existen datos para los dos (siempre los calculará si hay coordenadas y no superficies ya calculadas).
        :type recalc_superf: bool

        """

        # Generar la base de datos
        archivo = símismo.prep_archivo(archivo)
        bd = gen_bd(archivo)

        # El número de parcelas
        n_parc = bd.n_obs

        # El diccionario en el Experimento donde habrá que guardar los datos.
        dic_parc = símismo.datos['Parcelas']
        dic_parc['Nombres'] = bd.obt_datos_tx(cols=col_nombres)  # Llenar los datos de nombres.

        # Llenar superficies
        if col_superficies is not None:
            dic_parc['Superficies'] = bd.obt_datos(cols=col_superficies)
        else:
            dic_parc['Superficies'] = None

        # Llenar coordenadas de polígonos
        if col_polígonos is not None:
            l_polí = [ast.literal_eval(l) for l in bd.obt_datos_tx(cols=col_polígonos)]

            dic_parc['Polígonos'] = l_polí

            # Calcular superficies
            if recalc_superf:
                # Si hay que recalcular todas las superficies, incluir todas las parcelas.
                í_parc_calc = range(n_parc)
            else:
                # ... sino, incluir únicamente las parcelas sin datos de superficies disponibles.
                í_parc_calc = [í for í in range(n_parc) if dic_parc['Superficies'][í] is None]

            # Para cada parcela cuya superficie hay que calcular...
            for í_p in í_parc_calc:

                # Si posible, calcular la superficie
                if dic_parc['Polígonos'][í_p] is not None:
                    coords = dic_parc['Polígonos'][í_p]

                    # Una función obscura...
                    sup = 0.5 * np.abs(np.dot(coords[0], np.roll(coords[1], 1))
                                       - np.dot(coords[1], np.roll(coords[0], 1)))

                    dic_parc['Superficies'][í_p] = sup  # Guardar

    def _agregar_datos_rae(símismo, archivo, tipo_egr, col_tiempo, col_parc, cols_etps, factor, cód_na):
        """
        Esta función genérica agrega datos de RAE.

        :param archivo: El archivo con la base de datos
        :type archivo: str

        :param tipo_egr: El tipo de datos.
        :type tipo_egr: str

        :param col_tiempo: El nombre de la columna de datos.
        :type col_tiempo: str

        :param col_parc: El nombre de la columna de parcelas.
        :type col_parc: str

        :param cols_etps: El nombre de las columnas con observaciones.
        :type cols_etps: str | list[str]

        :param factor: El factor de conversión.
        :type factor: float | int

        :param cód_na: El código para datos que faltan en la base de datos.
        :type cód_na: str | int | float
        """

        # Crear la base de datos
        archivo = símismo.prep_archivo(archivo)
        bd = gen_bd(archivo)

        # Procesar los nombre de columnas
        nombres_cols = bd.sacar_cols()

        # Verificar que los nombres de columnas concuerden con las columnas disponibles en la base de datos.
        if col_tiempo not in nombres_cols:
            raise ValueError
        if col_parc is not None and col_parc not in nombres_cols:
            raise ValueError

        if cols_etps is None:
            # Si no se especificó las columnas de interés, tomar todas las posibles.
            cols_etps = nombres_cols.copy()

            # ... menos las columnas de tiempo y de parcelas
            cols_etps.remove(col_tiempo)
            if col_parc is not None:
                cols_etps.remove(col_parc)
        else:
            # Asegurar formato correcto para las columnas de etapas
            if not isinstance(cols_etps, list):
                cols_etps = [cols_etps]

            for c in cols_etps:
                # Asegurarse que las columnas de interés existen, si las especificó el usuario
                if c not in nombres_cols:
                    raise ValueError

        # El número de observaciones (filas) en la base de datos.
        n_obs = bd.n_obs

        # Obtener el vector de nombres de parcelas
        if col_parc is not None:
            v_parc = bd.obt_datos_tx(cols=col_parc)
        else:
            # Si no se especificaron parcelas, nombrar la única parcela "1".
            v_parc = np.ones(n_obs, dtype=int).astype(str)
        parc_únicas = np.unique(v_parc)  # Nombres de parcelas únicos, en orden alfabético
        v_í_parc = np.array([np.argwhere(parc_únicas == x)[0][0] for x in v_parc])

        # La fecha inicial y el vector de días relativos a la fecha inicial.
        fecha_inic, v_días = bd.obt_días(col=col_tiempo)

        # Actualizar las fechas del Experimento, si necesario.
        símismo.actualizar_fechas(nueva_fecha_inic=fecha_inic, días=v_días)
        días_únicos = np.unique(v_días)  # Vector de días únicos
        v_í_días = np.array([np.argwhere(días_únicos == x)[0][0] for x in v_días])

        # El número de parcelas, días y etapas únicas.
        n_parc = parc_únicas.shape[0]
        n_días = días_únicos.shape[0]
        n_etps = len(cols_etps)

        # La matriz de observaciones
        m_obs_bd = bd.obt_datos(cols=cols_etps)  # Eje 0: col, eje 1: día/parcela
        np.multiply(m_obs_bd, factor, out=m_obs_bd)  # Ajustar por el factor

        # Si hay código especial para datos que faltan, aplicarlo aquí.
        if cód_na is not None:
            m_obs_bd[m_obs_bd == cód_na] = np.nan

        # La matriz de datos para el Experimento (vacía por el momento).
        matr_obs = np.empty((n_parc, n_etps, n_días))
        matr_obs[:] = np.nan

        # Llenar la matriz de datos
        for í_c in range(m_obs_bd.shape[0]):  # Para cada número de columna...
            matr_obs[v_í_parc, [í_c] * n_obs, v_í_días] = m_obs_bd[í_c, :]

        # Llenar el diccionario de datos con todo lo que acabamos de calcular.
        dic_datos = símismo.datos['RAE'][tipo_egr]
        dic_datos['cols'] = cols_etps
        dic_datos['días'] = días_únicos
        dic_datos['datos'] = matr_obs
        dic_datos['parc'] = parc_únicas

    def agregar_cultivos(símismo, archivo):
        """

        :param archivo:
        :type archivo: str
        """
        pass  # Para hacer

    def agregar_aplicaciones(símismo, archivo):
        """

        :param archivo:
        :type archivo: str

        """
        pass  # Para hacer

    def actualizar_fechas(símismo, nueva_fecha_inic, días=None):
        """

        :param nueva_fecha_inic:
        :type nueva_fecha_inic: ft.date
        :param días: Un vector de los nuevos días que corresponden con la nueva fecha de inicio. Se modificará este
        vector automáticamente si hay un ajusto necesario para que sean compatibles estos datos con la fecha inicial
        del resto de la base de datos.
        :type días: np.ndarray
        """

        # Si las fechas de la base de datos tienen una fecha inicial
        if nueva_fecha_inic is not None:

            # El cambio de fecha para los nuevos datos
            cambio_nuevos = 0

            if símismo.fecha_ref is None:
                # Si no había fecha de referencia para este experimento...

                símismo.fecha_ref = nueva_fecha_inic  # Guardarla

            else:

                # Sino, calcular la diferencia entre la fecha de referencia del experimento y la fecha de referencia
                # de la base de datos de organismos
                dif = (nueva_fecha_inic - símismo.fecha_ref).days

                if dif < 0:
                    # Si la fecha existente era posterior a la nueva fecha:
                    símismo.fecha_ref = nueva_fecha_inic  # Usar la nueva fecha como referencia

                    # Y ajustar las fechas de las otras partes de este experimento
                    símismo.mover_fechas(dif=dif)

                else:
                    # Si era anterior a la nueva fecha, guardar la fecha existente y ajustar los nuevos datos:
                    cambio_nuevos = dif

            if días is not None:
                np.add(cambio_nuevos, días, out=días)

    def mover_fechas(símismo, dif):
        """
        Esta función ajusta las fechas de todas las observaciones disponibles en el diccionario de datos.

        :param dif: El ajuste.
        :type dif: int
        """

        # Sacar la lista de observaciones disponibles.
        l_vecs_días = sacar_vecs_días(d=símismo.datos)

        for v in l_vecs_días:
            # Para cada observación...

            np.add(dif, v, out=v)  # Aplicar el ajuste

    def prep_archivo(símismo, archivo):
        """

        :param archivo:
        :type archivo: str
        :return:
        :rtype: str
        """

        if os.path.splitdrive(archivo)[0] == '':
            # Si no se especifica directorio, se usará el directorio de Proyectos de Tiko'n.
            archivo = os.path.join(directorio_base, 'Proyectos', símismo.proyecto, archivo)

        return archivo


def sacar_vecs_días(d, l=None):
    """
    Esta función saca todos los vectores de fechas en un diccionario de manera recursiva. Los diccionarios de datos
    deben usar la llave "días" para indicar vectores de fechas.

    :param d: El diccionario para analizar.
    :type d: dict
    :param l: Parámetro para la función recursiva. NO especificar mientras llamas esta función.
    :type l: list
    :return: La lista de vectores numpy de fechas.
    :rtype: list[np.ndarray]
    """

    # Crear la lista vacía inicial
    if l is None:
        l = []

    for ll, v in d.items():
        if isinstance(v, dict):
            sacar_vecs_días(d=v, l=l)
        else:
            if ll == 'días' and v is not None:
                l.append(v)

    return l


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
    """
    Una superclase para lectores de bases de datos.
    """

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
        :rtype: (ft.date, np.ndarray)
        """

        # Sacar la lista de fechas en formato texto
        fechas_tx = símismo.obt_datos_tx(cols=col)

        # Procesar la lista de fechas
        fch_inic_datos, v_núm = símismo.leer_fechas(lista_fechas=fechas_tx)

        # Devolver información importante
        return fch_inic_datos, v_núm

    def calc_n_obs(símismo):
        """

        :return:
        :rtype: int
        """
        raise NotImplementedError

    @staticmethod
    def leer_fechas(lista_fechas):
        """
        Esta función toma una lista de datos de fecha en formato de texto y detecta 1) la primera fecha de la lista,
        y 2) la posición relativa de cada fecha a esta.

        :param lista_fechas: Una lista con las fechas en formato de texto
        :type lista_fechas: list

        :return: Un tuple de la primera fecha y del vector numpy de la posición de cada fecha relativa a la primera.
        :rtype: (ft.date, np.ndarray)

        """

        # Primero, si los datos de fechas están en formato simplemente numérico...
        if all([x.isdigit() for x in lista_fechas]):

            # Entonces, no conocemos la fecha inicial
            fecha_inic_datos = None

            # Convertir a vector Numpy
            vec_fch_núm = np.array(lista_fechas, dtype=int)

        else:
            # Sino, intentar de leer el formato de fecha
            fechas = None

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
                vec_fch_núm = np.array(lista_fechas, dtype=int)

        return fecha_inic_datos, vec_fch_núm


class BDtexto(BD):
    """
    Una clase para leer bases de datos en formato texto delimitado por comas (.csv).
    """

    def calc_n_obs(símismo):
        """

        :rtype: int
        """
        with open(símismo.archivo) as d:
            n_filas = sum(1 for f in d if len(f)) - 1  # Sustrayemos la primera fila

        return n_filas

    def obt_datos(símismo, cols):
        """

        :param cols:
        :type cols: str | list[str]
        :return:
        :rtype: np.ndarray
        """
        if not isinstance(cols, list):
            cols = [cols]

        m_datos = np.empty((len(cols), símismo.n_obs))

        with open(símismo.archivo) as d:
            lector = csv.DictReader(d)
            for n_f, f in enumerate(lector):
                m_datos[:, n_f] = [float(f[c]) if f[c].strip() != '' else np.nan for c in cols]

        if len(cols) == 1:
            m_datos = m_datos[0]

        return m_datos

    def obt_datos_tx(símismo, cols):
        """

        :param cols:
        :type cols: list[str] | str
        :return:
        :rtype: list
        """
        if not isinstance(cols, list):
            cols = [cols]

        l_datos = [[''] * símismo.n_obs] * len(cols)

        with open(símismo.archivo) as d:
            lector = csv.DictReader(d)
            for n_f, f in enumerate(lector):
                for i_c, c in enumerate(cols):
                    l_datos[i_c][n_f] = f[c]

        if len(cols) == 1:
            l_datos = l_datos[0]

        return l_datos

    def sacar_cols(símismo):
        """

        :return:
        :rtype: list[str]
        """

        with open(símismo.archivo) as d:
            lector = csv.reader(d)

            nombres_cols = next(lector)

        return nombres_cols


class BDsql(BD):
    """
    Una clase para leer bases de datos en formato SQL.
    """

    def calc_n_obs(símismo):
        """

        :return:
        :rtype:
        """
        pass

    def obt_datos(símismo, cols):
        """

        :param cols:
        :type cols:
        :return:
        :rtype:
        """
        pass

    def obt_datos_tx(símismo, cols):
        """

        :param cols:
        :type cols:
        :return:
        :rtype:
        """
        pass

    def sacar_cols(símismo):
        """

        :return:
        :rtype:
        """
        pass
