import copy as copiar
import json
import os
from datetime import datetime as ft
from warnings import warn as avisar

import numpy as np

from tikon0.Matemáticas import Arte, Incert
from tikon0.Matemáticas.Sensib import prep_anal_sensib
from tikon0.Matemáticas.Variables import VarSpotPy


class Coso(object):

    def borrar_calib(símismo, id_calib, recursivo=True):
        """
        Esta función borra una calibración de la receta del Coso.

        :param id_calib: El nombre de la calibración que hay que borrar.
        :type id_calib: str

        :param recursivo: Si también borramos lo mismo en los otros Cosos asociados con este.
        :type recursivo: bool

        """

        # Borramos la distribución de la receta de coeficientes
        símismo._borrar_dist(d=símismo.receta['coefs'], nombre=id_calib)

        # Tambien borramos el nombre de la calibracion del diccionario de calibraciones, si es que existe allí.
        try:
            símismo.receta['Calibraciones'].pop(id_calib)
        except KeyError:
            pass

        # Si es una limpieza recursiva, limpiamos todos los objetos vinculados de manera recursiva también.
        if recursivo:
            for coso in símismo.objetos:
                coso.borrar_calib(id_calib=id_calib, recursivo=recursivo)

    def limpiar_especificados(símismo, recursivo=True):
        """
        Esta función limpia (borra) todas las distribuciones especificadas para este Coso.

        :param recursivo: Si también limpiamos las distribuciones especificadas de los otros Cosos asociados con este.
        :type recursivo: bool

        """
        símismo.borrar_calib(id_calib='especificado', recursivo=recursivo)

    def guardar_especificados(símismo, nombre_dist='dist_especificada'):
        """
        Esta función guarda los valores de distribuciones especificadas bajo un nuevo nombre. Esto permite, después,
        guardar y cargar el Coso sin perder las distribuciones especificadas, que son normalmente temporarias.

        :param nombre_dist: El nombre de la distribución.
        :type nombre_dist: str

        """

        # Cambiar el nombre de las distribuciones especificadas en el diccionario de coeficientes.
        símismo._renombrar_dist(símismo.receta['coefs'], nombre_ant='especificado', nombre_nuevo=nombre_dist)

    def ver_coefs_no_espec(símismo):
        """

        :return:
        :rtype: dict

        """

        sin_especif = {símismo.nombre: símismo._sacar_coefs_no_espec()}

        for obj in símismo.objetos:
            sin_especif[obj.nombre] = obj.ver_coefs_no_espec()

        return sin_especif

    @classmethod
    def _borrar_dist(cls, d, nombre):
        """
        Esta función borra todas las distribuciones con un nombre específico en un diccionario de coeficientes.

        :param d: El diccionario de coeficientes.
        :type d: dict

        :param nombre: El nombre de la distribución.
        :type nombre: str

        """

        # Para cada itema (llave, valor) del diccionario
        for ll in list(d):
            v = d[ll]

            if type(v) is dict:

                # Si el itema era otro diccionario, llamar esta función de nuevo con el nuevo diccionario
                cls._borrar_dist(v, nombre=nombre)

            else:

                # Si la distribución lleva el nombre especificado...
                if ll == str(nombre):
                    # ...borrar la distribución
                    d.pop(ll)

    @classmethod
    def _renombrar_dist(cls, d, nombre_ant, nombre_nuevo):
        """
        Esta función cambia el nombre de una distribución en un diccionario de coeficientes.

        :param d: El diccionario de coeficientes.
        :type d: dict

        :param nombre_ant: El nombre actual de la distribución.
        :type nombre_ant: str

        :param nombre_nuevo: El nuevo nombre de la distribución.
        :type nombre_nuevo: str

        """

        # Para cada itema (llave, valor) del diccionario
        for ll, v in d.items():

            if type(v) is dict:

                # Si el itema era otro diccionario, llamar esta función de nuevo con el nuevo diccionario
                cls._renombrar_dist(v, nombre_ant=nombre_ant, nombre_nuevo=nombre_nuevo)

            elif type(v) is str:

                # Cambiar el nombre de la llave
                if ll == nombre_ant:
                    # Crear una llave con el nuevo nombre
                    d[nombre_nuevo] = d[ll]

                    # Quitar el viejo nombre
                    d.pop(ll)


class Simulable(Coso):
    """
    Una subclase de Coso para objetos que se pueden simular y calibrar. (Por ejemplo, una Red AgroEcológica o una
    Parcela, pero NO un Insecto.
    """

    def sensibilidad(símismo, nombre, exper, n, método='Sobol', calibs=None, por_dist_ingr=0.95,
                     n_rep_estoc=30, tiempo_final=None, detalles=False, usar_especificadas=True,
                     opciones_sens=None, dibujar=False):
        """
        Esta función calcula la sensibilidad de los parámetros del modelo. Puede aplicar varios tipos de análisis de
        sensibilidad.

        :param nombre: El nombre para la simulación de incertidumbre.
        :type nombre: str
        :param exper: Los experimentos para incluir.
        :type exper: str | list | Experimento
        :param n: El número de valores de parámetros para intentar.
        :type n: int
        :param método: El método de análisis. Puede ser uno de `Sobol`, `FAST`, `Morris`, `DMIM`, `DGSM`, o `FF`. Ver
        el paquete `SALib` para más detalles.
        :type método: str
        :param calibs: Las calibraciones para incluir en el análisis.
        :type calibs: list | str
        :param por_dist_ingr: El porcentaje de las distribuciones cumulativas de los parámetros para incluir en el
        análisis.
        :type por_dist_ingr: float | int
        :param n_rep_estoc: El número de repeticiones estocásticas.
        :type n_rep_estoc: int
        :param tiempo_final: El tiempo final de la simulación
        :type tiempo_final: int
        :param detalles: Si quieres simular con detalles (o no).
        :type detalles: bool
        :param usar_especificadas: Si hay que utilizar a prioris especificados.
        :type usar_especificadas: bool
        :param opciones_sens: Opciones específicos al método de análisis de sensibilidad.
        :type opciones_sens: dict
        :param dibujar: Si hay que dibujar los resultados.
        :type dibujar: bool
        :return: Un tuple de la lista de nombres de los párámetros y de un diccionario con los resultados.
        :rtype: (list[list], dict)
        """

        # La lista de diccionarios de parámetros y de sus límites teoréticos
        lista_paráms, lista_líms, nombres_paráms = símismo._gen_lista_coefs_interés_todos()

        # Las calibraciones para utilizar para el análisis
        lista_calibs = símismo._filtrar_calibs(calibs=calibs, l_paráms=lista_paráms,
                                               usar_especificadas=usar_especificadas)

        # Una lista de las distribuciones de los parámetros. Esta función también llena los diccionarios de los
        # parámetros con estas mismas distribuciones.
        lista_dists = Incert.trazas_a_dists(id_simul=nombre, l_d_pm=lista_paráms, l_trazas=lista_calibs,
                                            formato='sensib', comunes=False, l_lms=lista_líms, n_rep_parám=1000)

        # Basado en las distribuciones de los parámetros, establecer los límites para el análisis de sensibilidad
        lista_líms_efec = Incert.dists_a_líms(l_dists=lista_dists, por_dist_ingr=por_dist_ingr)

        # Definir los parámetros del análisis en el formato que le gusta al paquete SALib.
        i_acetables = [i for i, lms in enumerate(lista_líms_efec) if lms[0] != lms[1]]
        nombres = [str(x) for x in range(len(lista_paráms))]  # Nombres numéricos muy sencillos
        n_paráms = len(i_acetables)  # El número de parámetros para el análisis de sensibilidad
        problema = {
            'num_vars': n_paráms,  # El número de parámetros
            # Nombres numéricos muy sencillos
            'names': [n for i, n in enumerate(nombres) if i in i_acetables],
            # La lista de los límites de los parámetros para el analisis de sensibilidad
            'bounds': [n for i, n in enumerate(lista_líms_efec) if i in i_acetables]
        }

        # Finalmente, hacer el análisis de sensibilidad. Primero generamos los valores de parámetros para intentar.
        vals_paráms, fun_anlz, ops_anlz = prep_anal_sensib(método, n=n, problema=problema, opciones=opciones_sens)

        # Aplicar las matrices de parámetros generadas a los diccionarios de coeficientes. Las con distribuciones sin
        # incertidumbre guardarán su distribución SciPy original.
        for i in i_acetables:
            i_rel = i_acetables.index(i)
            lista_paráms[i][nombre] = vals_paráms[:, i_rel]

        # El número de repeticiones paramétricas
        n_rep_parám = vals_paráms.shape[0]

        # Correr la simulación. Hay que poner usar_especificadas=False aquí para evitar que distribuciones
        # especificadas tomen el lugar de las distribuciones que acabamos de generar por SALib. gen_dists=True
        # asegurar que se guarde el orden de los valores de los variables tales como especificados por SALib.
        símismo.simular(exper=exper, nombre=nombre, calibs=nombre, detalles=detalles, tiempo_final=tiempo_final,
                        n_rep_parám=n_rep_parám, n_rep_estoc=n_rep_estoc, usar_especificadas=False,
                        dibujar=False, mostrar=False, dib_dists=False)

        # Procesar las matrices
        l_matrs_proc, ubics_m = símismo._procesar_matrs_sens()

        # Borrar las distribuciones creadas para el análisis
        símismo.borrar_calib(id_calib=nombre)

        # Una lista para guardar los resultados. Cada diccionario en la lista tiene el formato siguiente:
        # {índice_sensibilidad1: [matriz de resultados, eje 0 = parám, (eje 1 = parám2), eje -1 = día)],
        #  índice_sensibilidad2: ...}
        l_d_sens = []

        # Por fin, analizar la sensibilidad
        for m in l_matrs_proc:
            # Para cada matriz procesada...

            # El diccionario para los resultados
            d_sens = {}

            # Agregarlo a la lista de resultados
            l_d_sens.append(d_sens)

            # Llenar la matriz de resultados para cada día de simulación
            n_días = m.shape[1]
            for d in range(n_días):
                # Para cada día de simulación...

                # Analizar la sensibilidad
                d_egr_sens = fun_anlz(problema, Y=m[:, d], **ops_anlz)

                for egr, m_egr in d_egr_sens.items():
                    # Para cada tipo de egreso del análisis de sensibilidad...

                    # Crear la matriz de resultados vacía, si necesario
                    if egr not in d_sens:
                        d_sens[egr] = np.zeros((*m_egr.shape, n_días))

                    # Llenar los datos para este día
                    d_sens[egr][..., d] = d_egr_sens[egr]

        # Convertir la lista de resultados de AS a un diccionario de resultados para devolver al usuario
        resultado = llaves_a_dic(l_ubics=ubics_m, vals=l_d_sens)

        # Si necesario, dibujar los resultados
        if dibujar:

            for ubic, d in zip(ubics_m, l_d_sens):
                # Para cada matriz de análisis de sensibilidad...

                for índ, m in d.items():
                    # Para cada índice de sensibilidad y su matriz de resultados correspondiente...

                    # El directorio del gráfico
                    direc = os.path.join(símismo.proyecto, símismo.nombre, nombre, *ubic)
                    direc = símismo._prep_directorio(directorio=direc)

                    if len(m.shape) == 2:
                        # Si no tenemos interacción de parámetros...

                        for i, prm in enumerate(nombres_paráms):
                            # Para cada parámetro...

                            # El título del gráfico
                            título = '{}: {}'.format(prm, índ)

                            # Dibujar el gráfico
                            Arte.graficar_línea(datos=m[i, :], título=título, etiq_y='{}: {}'.format(método, índ),
                                                etiq_x='Día', directorio=direc)
                    elif len(m.shape) == 3:
                        # Si tenemos interacciones entre parámetros...

                        for i, prm_1 in enumerate(nombres_paráms):
                            # Para cada parámetro...

                            for j, prm_2 in enumerate(nombres_paráms):
                                # Para cada parámetro otra vez...

                                # El título del gráfico
                                título = '{}-{}: {}'.format(prm_1, prm_2, índ)

                                # Dibujar el gráfico
                                Arte.graficar_línea(datos=m[i, j, :], título=título,
                                                    etiq_y='{}: {}'.format(método, índ), etiq_x='Día', directorio=direc)
                    else:
                        # Si tenemos otra forma de matriz, no sé qué hacer.
                        raise ValueError('Número de ejes ({}) inesperado. Quejarse al programador.'
                                         .format(len(m.shape)))

        # Devolver los resultados
        return nombres_paráms, resultado

    def dibujar_calib(símismo):
        """
        Esta función dibuja los parámetros incluidos en una calibración, antes y después de calibrar. Tiene
        funcionalidad para buscar a todos los parámetros incluidos en objetos vinculados a este Simulable también.

        """

        def sacar_dists_de_dic(d, l=None, u=None):
            """
            Esta función recursiva saca las distribuciones `VarCalib` de un diccionario de coeficientes.
            Devuelva los resultados en forma de tuple:


            :param d: El diccionario
            :type d: dict
            :param l:
            :type l: list
            :param u:
            :type u: list
            :return:
            :rtype: list
            """

            if l is None:
                l = []
            if u is None:
                u = []

            for ll, v in d.items():
                if type(v) is dict:
                    u.append(ll)
                    sacar_dists_de_dic(d=v, l=l, u=u)

                elif isinstance(v, VarSpotPy):
                    u.append(ll)
                    l.append((u.copy(), v))
                    u.pop()
                else:
                    # Si no, hacer nada
                    pass
            if len(u):
                u.pop()
            return l

        def sacar_dists_calibs(obj, l=None):
            """
            Esta función auxiliar saca las distribuciones PyMC de un objeto y de todos los otros objetos vinculados
            con este.

            :param obj: El objeto cuyas distribuciones de parámetros hay que sacar.
            :type obj: Coso

            :param l: Una lista para la recursión. Nunca especificar este parámetro mientras que se llama la función.
            :type l: list

            :return: Una lista de tuples de los parámetros, cada uno con la forma general:
            (lista de la ubicación del parámetro, distribución PyMC)
            :rtype: list

            """

            if l is None:
                l = []

            dic_coefs = obj.receta['coefs']

            if len(dic_coefs):
                l += sacar_dists_de_dic(dic_coefs, u=[obj.nombre])

            for o in obj.objetos:
                l += sacar_dists_calibs(obj=o)

            return l

        lista_dists = sacar_dists_calibs(símismo)

        for ubic, dist in lista_dists:

            directorio = os.path.join(directorio_base, 'Proyectos', os.path.splitext(símismo.proyecto)[0],
                                      símismo.nombre, 'Gráficos calibración', símismo.ModCalib.id, ubic[0])
            archivo = os.path.join(directorio, '_'.join(ubic[1:-1]) + '.png')

            if not os.path.exists(directorio):
                os.makedirs(directorio)

            título = ':'.join(ubic[1:-1])

            try:
                Arte.graficar_dists(dists=dist, título=título, archivo=archivo)
            except AttributeError:
                pass
