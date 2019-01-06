import datetime as ft

import pandas as pd
from تقدیر.ذرائع.مشاہدات import دن_مشا, مہنہ_مشا, سال_مشا

from تقدیر.مقام import مقام

# Ofrecemos la oportunidad de utilizar تقدیر, taqdir, en español

conv_vars = {
    'Precipitación': 'بارش',
    'Radiación solar': 'شمسی_تابکاری',
    'Temperatura máxima': 'درجہ_حرارت_زیادہ',
    'Temperatura promedia': 'درجہ_حرارت_کم',
    'Temperatura mínima': 'درجہ_حرارت_اوسط'
}


# Una subclase traducida
class Lugar(مقام):
    """
    Esta clase conecta con la clase مقام, o Lugar, del paquete taqdir.
    """

    def __init__(símismo, nombre, lat, long, elev):
        """
        Inciamos el :class:`Lugar` con sus coordenadas.
        :param lat: La latitud del lugares.
        :type lat: float | int
        :param long: La longitud del lugares.
        :type long: float | int
        :param elev: La elevación del lugares, en metros.
        :type elev: float | int
        """

        símismo.nombre = nombre
        # Iniciamos como مقام
        super().__init__(چوڑائی=lat, طول=long, بلندی=elev)

    def observar_diarios(símismo, archivo, cols_datos, conv, c_fecha):
        """
        Esta función permite conectar observaciones diarias de datos climáticos.
        :param archivo: El archivo con la base de datos.
        :type archivo: str
        :param cols_datos: Un diccionario, donde cada llave es el nombre oficial del variable climático y
          el valor es el nombre de la columna en la base de datos.
        :type cols_datos: dict[str, str]
        :param conv: Diccionario de factores de conversión para cada variable. Las llaves deben ser el nombre del
          variable **en Tinamït**.
        :type conv: dict[str, int | float]
        :param c_fecha: El nombre de la columna con las fechas de las observaciones.
        :type c_fecha: str
        """

        for v in cols_datos:
            if v not in conv_vars:
                raise KeyError(_('Error en observaciones diarias: "{}" no es variable climático reconocido en Tikon. '
                                 'Debe ser uno de: {}').format(v, ', '.join(conv_vars)))
        for v in conv:
            if v not in conv_vars:
                raise KeyError(_('Error en factores de conversión: "{}" no es variable climático reconocido en '
                                 'Tinamït. Debe ser uno de: {}').format(v, ', '.join(conv_vars)))

        d_cols = {conv_vars[x]: cols_datos[x] for x in cols_datos}
        d_conv = {conv_vars[v]: c for v, c in conv.items()}

        obs = دن_مشا(مسل=archivo, تبادلوں=d_conv, س_تاریخ=c_fecha, س_اعداد=d_cols)

        símismo.مشاہدہ_کرنا(مشاہد=obs)

    def observar_mensuales(símismo, archivo, cols_datos, meses, años, conv=None):
        """
        Esta función permite conectar observaciones mensuales de datos climáticos.
        :param archivo: El archivo con la base de datos.
        :type archivo: str
        :param cols_datos: Un diccionario, donde cada llave es el nombre oficial del variable climático y el valor es
          el nombre de la columna en la base de datos.
        :type cols_datos: dict[str, str]
        :param conv: Diccionario de factores de conversión para cada variable. Las llaves deben ser el nombre del
          variable **en Tinamït**.
        :type conv: dict[str, int | float]
        :param meses: El nombre de la columna con los meses de las observaciones.
        :type meses: str
        :param años: El nombre de la columna con los años de las observaciones.
        :type años: str
        """

        for v in cols_datos:
            if v not in conv_vars:
                raise KeyError(_('Error en observaciones mensuales: "{}" no es variable climático reconocido en '
                                 'Tinamït. Debe ser uno de: {}').format(v, ', '.join(conv_vars)))
        if conv is None:
            conv = {v: 1 for v in cols_datos}
        for v in conv:
            if v not in conv_vars:
                raise KeyError(_('Error en factores de conversión: "{}" no es variable climático reconocido en '
                                 'Tinamït. Debe ser uno de:\t\n{}').format(v, ', '.join(conv_vars)))

        d_cols = {conv_vars[x]: cols_datos[x] for x in cols_datos}
        d_conv = {conv_vars[v]: c for v, c in conv.items()}

        obs = مہنہ_مشا(مسل=archivo, س_اعداد=d_cols, تبادلوں=d_conv, س_مہینہ=meses, س_سال=años)

        símismo.مشاہدہ_کرنا(obs)

    def observar_anuales(símismo, archivo, cols_datos, conv, años):
        """
        Esta función permite conectar observaciones anuales de datos climáticos.
        :param archivo: El archivo con la base de datos.
        :type archivo: str
        :param cols_datos: Un diccionario, donde cada llave es el nombre oficial del variable climático y el valor es
          el nombre de la columna en la base de datos.
        :type cols_datos: dict[str, str]
        :param conv: Diccionario de factores de conversión para cada variable. Las llaves deben ser el nombre del
          variable **en Tinamït**.
        :type conv: dict[str, int | float]
        :param años: El nombre de la columna con los años de las observaciones.
        :type años: str
        """

        for v in cols_datos:
            if v not in conv_vars:
                raise KeyError(_('Error en observaciones anuales: "{}" no es variable climático reconocido en Tinamït. '
                                 'Debe ser uno de: {}').format(v, ', '.join(conv_vars)))
        for v in conv:
            if v not in conv_vars:
                raise KeyError(_('Error en factores de conversión: "{}" no es variable climático reconocido en '
                                 'Tinamït. Debe ser uno de: {}').format(v, ', '.join(conv_vars)))

        d_cols = {conv_vars[x]: cols_datos[x] for x in cols_datos}
        d_conv = {conv_vars[v]: c for v, c in conv.items()}

        obs = سال_مشا(مسل=archivo, س_اعداد=d_cols, تبادلوں=d_conv, س_سال=años)
        símismo.مشاہدہ_کرنا(obs)

    def prep_datos(símismo, fecha_inic, fecha_final, tcr, prefs=None, lím_prefs=False, regenerar=False):
        """
        Esta función actualiza el diccionario interno de datos climáticos del Lugar, listo para una simulación.
        Intentará obtener datos de todas fuentes posibles, incluso observaciones y modelos de predicciones climáticas.
        :param fecha_inic: La fecha inicial.
        :type fecha_inic: ft.date | ft.datetime
        :param fecha_final: La fecha final.
        :type fecha_final: ft.date | ft.datetime
        :param tcr: El escenario climático, o trayectorio de concentración relativa (tcr), de la IPCC
          (puede ser uno de 2.6, 4.5, 6.0, o 8.5).
        :type tcr: str | float
        :param prefs: Una lista opcional de fuentes potenciales de datos, en orden de preferencia.
        :type prefs: list
        :param lím_prefs: Si hay que limitar las fuentes de datos
        :type lím_prefs: bool
        :param regenerar: Si hay que regenerar datos o no.
        :type regenerar: bool
        """
        super().اعداد_تیاری(fecha_inic, fecha_final, tcr, ش_ترکار=1, ترجیحات=prefs, ترجیحات_محدود=lím_prefs,
                            دوبارہ_پیدا=regenerar)

    def devolver_datos(símismo, vars_clima, f_inic, f_final):
        """
        Esta función devuelve datos ya calculados por :func:`~tinamit.Geog.Geog.Lugar.prep_datos`.
        :param vars_clima: Una lista de variables climáticos de interés.
        :type vars_clima: list[str]
        :param f_inic: La fecha inicial.
        :type f_inic: ft.datetime | ft.date
        :param f_final: La fecha final.
        :type f_final: ft.datetime | ft.date
        :return: Los datos pedidos.
        :rtype: pd.DataFrame
        """
        bd = símismo.اعداد_دن  # type: pd.DataFrame
        datos_interés = bd.loc[f_inic:f_final]

        for v in vars_clima:
            if v not in conv_vars:
                raise ValueError(_('El variable "{}" está erróneo. Debe ser uno de:\n'
                                   '\t{}').format(v, ', '.join(conv_vars)))

        v_conv = [conv_vars[v] for v in vars_clima]

        return datos_interés[v_conv]

    def comb_datos(símismo, vars_clima, combin, f_inic, f_final):
        """
        Esta función combina datos climáticos entre dos fechas.
        :param vars_clima: Los variables de clima de interés.
        :type vars_clima: list[str]
        :param combin: Cómo hay que combinar (promedio o total)
        :type combin: list[str]
        :param f_inic: La fecha inicial
        :type f_inic: ft.datetime | ft.date
        :param f_final: La fecha final
        :type f_final: ft.datetime | ft.date
        :return: Un diccionario con los resultados.
        :rtype: dict[np.ndarray]
        """

        bd = símismo.اعداد_دن  # type: pd.DataFrame
        datos_interés = bd.loc[f_inic:f_final]

        resultados = {}
        for v, c in zip(vars_clima, combin):
            try:
                v_conv = conv_vars[v]
            except KeyError:
                raise ValueError(_('El variable "{}" está erróneo. Debe ser uno de:\n'
                                   '\t{}').format(v, ', '.join(conv_vars)))
            if c is None:
                if v in ['درجہ_حرارت_زیادہ', 'درجہ_حرارت_کم', 'درجہ_حرارت_اوسط']:
                    c = 'prom'
                else:
                    c = 'total'

            if c == 'prom':
                resultados[v] = datos_interés[v_conv].mean()
            elif c == 'total':
                resultados[v] = datos_interés[v_conv].sum()
            else:
                raise ValueError

        return resultados
