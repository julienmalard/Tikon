from warnings import warn as avisar

import numpy as np
import pymc

import scipy.stats as estad
from scipy.optimize import minimize as minimizar

import tikon.Matemáticas.Distribuciones as Ds
from tikon import __email__ as correo

try:
    import pymc3 as pm3
except ImportError:
    pm3 = None

"""
Este código contiene funciones para manejar datos y distribuciones de incertidumbre.
"""


def trazas_a_dists(id_simul, l_d_pm, l_trazas, formato, comunes, l_lms=None, n_rep_parám=None):
    """
    Esta función toma una lista de diccionarios de parámetros y una lista correspondiente de los límites de dichos
    parámetros y genera las distribuciones apriori en formato PyMC, SciPy o NumPy para los parámetros. Devuelve una
    lista de las distribuciones, y también guarda estos variables en los diccionarios de los parámetros bajo la llave
    especificada en id_calib.

    :param id_simul: El nombre de la calibración (para guardar la distribución en el diccionario de cada parámetro).
    :type id_simul: str

    :param l_d_pm: La lista de los diccionarios de los parámetros. Cada diccionario tiene las calibraciones de su
    parámetro.
    :type l_d_pm: list

    :param l_lms: Una lista de los límites de los parámetros, en el mismo orden que l_pm.
    :type l_lms: list

    :param l_trazas: Una lista de cuales trazas incluir. Cada elemento en la lista es una lista de los nombres de las
    calibraciones (trazas) para usar para el parámetro correspondiente en l_pm.
    :type l_trazas: list

    :param formato: El formato de la lista para devolver. Puede se "simul" (NumPy), "calib" (SciPy), o "sensib"
    (SciPy/NumPy).
    :type formato: str

    :param comunes: Si hay que intentar guardar la correspondencia multivarial entre distribuciones generadas por la
    misma calibración
    :type comunes: bool

    :param n_rep_parám: El número de repeticiones paramétricas. Solamente útil, de verdad, para `formato` = "simul".
    :type n_rep_parám: int

    :return: Una lista de las distribuciones generadas, en el mismo orden que l_pm.
    :rtype: list

    """

    # Poner el formato en minúsculas para evitar errores estúpidos
    formato = formato.lower()

    if n_rep_parám is None:
        if formato == 'calib':
            n_rep_parám = 1000  # para hacer: verificar

        else:
            raise ValueError('Se debe especificar el número de repeticiones paramétricas para generar las '
                             'distribuciones NumPy para una simulación.')

    if l_lms is None and formato == 'calib':
        raise ValueError('Hay que especificar los límites teoréticos de las distribuciones para generar a prioris'
                         'PyMC para una calibración.')

    # La lista para guardar las distribuciones generadas, en el mismo orden que la lista de parámetros
    lista_dist = []

    # Generar la lista de los índices para cada traza de cada parámetro
    l_í_trazas = gen_índ_trazas(l_d_pm, l_trazas, n_rep_parám=n_rep_parám, comunes=comunes)

    # Para cada parámetro en la lista...
    for n, d_parám in enumerate(l_d_pm):

        # Una lista de todas las calibraciones aplicables a este parámetro que tienen formato de texto
        trzs_texto = [t for t in l_trazas[n] if t in d_parám and type(d_parám[t]) is str]

        if len(trzs_texto) == 1:
            # Si solamente tenemos una distribución aplicable y esta está en formato de texto...

            if formato == 'calib':
                # Si querremos generar distribuciones para una calibración, generar un variable PyMC directamente.

                # El nombre para el variable PyMC
                nombre_pymc = 'parám_{}'.format(n)

                # Convertir el texto directamente en distribución
                dist = texto_a_dist(texto=d_parám[trzs_texto[0]], usar_pymc=True, nombre=nombre_pymc)

            elif formato == 'valid':
                # Si querremos una distribución para una validación, generar una traza en NumPy

                # La distribución SciPy
                var_sp = texto_a_dist(texto=d_parám[trzs_texto[0]], usar_pymc=False)

                # Convertir en matriz NumPy
                dist = var_sp.rvs(n_rep_parám)

            elif formato == 'sensib':
                # Si querremos una distribución para una análisis de sensibilidad, devolver la distribución SciPy
                dist = texto_a_dist(texto=d_parám[trzs_texto[0]], usar_pymc=False)

            else:
                raise ValueError

        else:
            # Si tenemos más que una calibración aplicable o esta está en formato de matriz...

            if formato == 'calib':
                # El nombre para el variable PyMC
                nombre_pymc = 'parám_%i' % n

                # Un vector numpy de la traza de datos para generar la distribución PyMC.
                vec_np = gen_vector_coefs(d_parám=d_parám, í_trazas=l_í_trazas[n])

                # Generar la distribución PyMC
                dist = ajustar_dist(datos=vec_np, límites=l_lms[n], cont=True, usar_pymc=True, nombre=nombre_pymc)[0]

            elif formato == 'valid':
                # En el caso de validación, simplemente querremos una distribución NumPy
                dist = gen_vector_coefs(d_parám=d_parám, í_trazas=l_í_trazas[n])
            elif formato == 'sensib':
                # En el caso de análisis de sensibilidad, querremos una distribución NumPy también
                dist = gen_vector_coefs(d_parám=d_parám, í_trazas=l_í_trazas[n])

        # Guardar la distribución en el diccionario de calibraciones del parámetro
        d_parám[id_simul] = dist

        # Añadir una referencia a la distribución en la lista de distribuciones
        lista_dist.append(dist)

    # Devolver la lista de variables PyMC
    return lista_dist


def gen_índ_trazas(l_d_pm, l_trazas, n_rep_parám, comunes):
    """
    Esta función genera índices de trazas para cada parámetro en una lista de diccionarios de parámetros, tomando
    en cuenta la lista de trazas (calibraciones) que aplican a cada parámetro.

    :param l_d_pm:
    :type l_d_pm: list[dict]

    :param l_trazas:
    :type l_trazas: list[list[str]]

    :param n_rep_parám: El número de índices que querremos.
    :type n_rep_parám: int

    :param comunes:
    :type comunes: bool

    :return:
    :rtype: list[dict[np.ndarray]]
    """

    # Primero, una función que calcula índices de trazas para un diccionario de parámetro.
    def calc_índs(d_trza, l_trza):
        """
        Calcula los índices para un diccionario de parámetro.

        :param d_trza: El diccionario de calibraciones del parámetro
        :type d_trza: dict[str | np.ndarray | pymc.Stochastic | pymc.Deterministic]

        :param l_trza: La lista de distribuciones del parámetro que queremos utilizar
        :type l_trza: list[str]

        :return: Los índices para cada traza (calibración) de este parámetro, en formato de diccionario.
        :rtype: dict[np.ndarray]
        """

        # Calcular el número de repeticiones paramétricas por calibración. Produce una lista, en el mismo orden
        # que calibs, del número de repeticiones para cada calibración.
        n_calibs = len(l_trza)
        rep_per_calib = np.array([n_rep_parám // n_calibs] * n_calibs)

        # Calcular el número que repeticiones que no se dividieron igualmente entre las calibraciones...
        resto = n_rep_parám % n_calibs

        # ...y añadirlas la principio de la lista de calibraciones.
        rep_per_calib[:resto] += 1

        # El diccionario para guardar los índices
        d_índs = {}

        for i, nombre_trz in enumerate(l_trza):
            # Para cada traza en el diccionario...

            # La distribución
            dist = d_trza[nombre_trz]

            if isinstance(dist, str) or isinstance(dist, estad._distn_infrastructure.rv_frozen):
                # Si la distribución está en formato de texto o de distribución SciPy...

                # Solamente guardar el número de repeticiones para esta distribución (índices no tienen sentido).
                d_índs[nombre_trz] = rep_per_calib[i]

            elif isinstance(dist, np.ndarray):
                # Si la distribución está en formato de matriz NumPy...

                # Verificar si la matriz NumPy tiene el tamaño suficiente para el número de repeticiones que querremos
                tamaño_máx = dist.shape[0]
                if tamaño_máx < rep_per_calib[i]:
                    avisar('Número de repeticiones paramétricas ({}) superior al tamaño de la traza de parámetro '
                           'disponible ({}).'.format(rep_per_calib[i], tamaño_máx))
                    devolv = True
                else:
                    devolv = False

                # Escoger los índices...
                if tamaño_máx == rep_per_calib[i]:
                    # ...en órden original, si estamos tomando la traza entiera (ni más, ni menos). Esto queda
                    # bien importante para no mezclar el orden de las trazas para un análisis de sensibilidad,
                    # donde los valores de los parámetros se determinan por un algoritmo externo.
                    índs = np.arange(tamaño_máx)
                else:
                    # ...sino, de manera aleatoria.
                    índs = np.random.choice(range(tamaño_máx), size=rep_per_calib[i], replace=devolv)
                d_índs[nombre_trz] = índs

            elif isinstance(dist, pymc.Stochastic) or isinstance(dist, pymc.Deterministic):
                # ..y si es un variable de calibración activa, poner el variable sí mismo en la matriz
                d_índs[nombre_trz] = None

            else:
                raise TypeError

        return d_índs

    # Primero, tomamos el caso donde estamos usando distribuciones comunes entre parámetros.
    if comunes:

        # Antes que todo, verificar que los nombres de todas las trazas estén iguales para todos los parámetros.
        # Dado las otras funciones en Tiko'n, no deberia de ser posible tener error aquí. Pero mejor verificar,
        # justo en caso.
        if any(set(x) != set(l_trazas[0]) for x in l_trazas):
            raise ValueError('¡Gran error terrible de programación! Panica primero y depués llama al programador. '
                             '({})'.format(correo))

        # Avisarle al usuario si no será posible de guardar la correspondencia entre todos los parámetos
        if any(type(l_d_pm[0][x]) is str for x in l_trazas):
            avisar('No se podrá guardar la correspondencia entre todas las calibraciones por presencia '
                   'de distribuciones SciPy. La correspondencia sí se guardará para las otras calibraciones.')

        dic_índs = calc_índs(d_trza=l_d_pm[0], l_trza=l_trazas[0])

        l_í_trazas = [dic_índs] * len(l_d_pm)

    else:
        # Ahora, si no trabajamos con distribuciones comunes...
        l_í_trazas = [calc_índs(d_trza=d_p, l_trza=l_trazas[i]) for i, d_p in enumerate(l_d_pm)]

    return l_í_trazas


def gen_vector_coefs(d_parám, í_trazas):
    """
    Esta función genera una matríz de valores posibles para un coeficiente, dado los nombres de las calibraciones
    que queremos usar y el número de repeticiones que queremos.

    :param d_parám: Un diccionario de un parámetro con todas sus calibraciones
    :type d_parám: dict

    :param í_trazas: Un diccionario de los índices a incluir para cada traza. Para trazas en formato de texto,
    únicamente especifica el número de muestras que queremos de la distribución.
    :type í_trazas: dict[int | np.ndarray]

    :return: Una matriz unidimensional con los valores del parámetro.
    :rtype: np.ndarray

    """

    # Un vector vacío para las trazas
    vector = []

    for trz, índs in í_trazas.items():
        # Para cada pareja de traza y de índices..

        if isinstance(d_parám[trz], np.ndarray):
            # Si está en formato NumPy, generar el vector de valores basado en los índices
            vector.append(d_parám[trz][índs])

        elif isinstance(d_parám[trz], str):
            # Si está en formato texto, generar las trazas del tamaño especificado en "índs" por medio de una
            # distribución SciPy
            dist_sp = texto_a_dist(d_parám[trz], usar_pymc=False)
            vector.append(dist_sp.rvs(size=índs))

        elif isinstance(d_parám[trz], pymc.Stochastic) or isinstance(d_parám[trz], pymc.Deterministic):
            # Variables de calibraciones activas (PyMC) se agregan directamente
            vector.append([d_parám[trz]])

        elif isinstance(d_parám[trz], estad._distn_infrastructure.rv_frozen):
            # Para distribuciones en formato SciPy, generar trazas de una vez
            vector.append(d_parám[trz].rvs(size=índs))

        else:
            # Si la traza era de otro tipo, tenemos un error.
            raise TypeError('Hay un error con la traza, que no puede ser de tipo "{}".'.format(type(d_parám[trz])))

    # Combinar las trazas de cada calibración en una única matriz NumPy unidimensional.
    return np.concatenate(vector)


def texto_a_dist(texto, usar_pymc=False, nombre=None):
    """
    Esta función convierte texto a su distribución SciPy o PyMC correspondiente.

    :param texto: La distribución a convertir. Sus parámetros deben ser en el orden de especificación de parámetros
    de la distribución SciPy correspondiente.
    :type texto: str

    :param usar_pymc: Si vamos a generar una distribución PyMC (en vez de una distribución de SciPy).
    :type usar_pymc: bool

    :param nombre: El nombre para dar a la distribución pymc, si aplica.
    :type nombre: str

    :return: Una distribución o SciPy, o PyMC.
    :rtype: estad.rv_frozen | pymc.Stochastic
    """

    # Asegurarse de que, si queremos una distribución pymc, también se especificó un nombre para el variable.
    if usar_pymc and nombre is None:
        raise ValueError('Se debe especificar un nombre para el variable si quieres una distribución de PyMC.')

    # Dividir el nombre de la distribución de sus parámetros.
    tipo_dist, paráms = texto.split('~')
    paráms = paráms.replace('(', '').replace(')', '')
    paráms = tuple([float(x) for x in paráms.split(',')])

    # Si el nombre de la distribución está en la lista arriba...
    if tipo_dist in Ds.dists:

        if usar_pymc:
            # Si querremos una distribución de PyMC...

            # Sacar la clase PyMC para esta distribución
            clase_dist = Ds.dists[tipo_dist]['pymc']

            # Si existe clase PyMC correspondiente...
            if clase_dist is not None:
                # Convertir los parámetros al formato para PyMC
                paráms, transform = paráms_scipy_a_pymc(tipo_dist=tipo_dist, paráms=paráms)

                # Crear la distribución
                dist = clase_dist(nombre, *paráms)

                # Y aplicar las transformaciones
                if transform['mult'] != 1:
                    dist = pymc.Lambda('%s_m' % dist, lambda x=dist, m=transform['mult']: x * m)
                if transform['sum'] != 0:
                    dist = pymc.Lambda('%s_s' % dist, lambda x=dist, s=transform['sum']: x + s)

            else:
                # Sino, hay error.
                raise ValueError('No existe distribución PyMC correspondiendo a %s.' % tipo_dist)
        else:
            # Sino, usar una distribución de SciPy
            dist = Ds.dists[tipo_dist]['scipy'](*paráms)

        # Devolver la distribución appropiada
        return dist

    # Si no encontramos el nombre de la distribución, hay un error.
    raise ValueError('No se pudo decodar la distribución "%s".' % texto)


def dist_a_texto(dist):
    """
    Esta función toma una distribución de SciPy y devuelva una representación de texto en formato de Tiko'n para
    la distribución.

    :param dist: La distribución.
    :type dist: estad.rv_frozen

    :return: La versión texto de la distribución.
    :rtype: str

    """

    args = dist.args

    nombre_scipy = dist.dist.name
    nombre_dist = next(x for x in Ds.dists if Ds.dists[x]['scipy'] == nombre_scipy)

    texto_dist = '%s~(%s)' % (nombre_dist, str(args))

    return texto_dist


def rango_a_texto_dist(rango, certidumbre, líms, cont):
    """
    Esta función genera distribuciones estadísticas (en formato texto) dado un rango de valores y la densidad de
    probabilidad en este rango, además de las límites intrínsicas del parámetro.

    :param rango: Un rango de valores.
    :type rango: tuple

    :param certidumbre: La probabilidad de que el variable se encuentre a dentro del rango.
    :type certidumbre: float

    :param líms: Los límites intrínsicos del parámetro.
    :type líms: tuple

    :param cont: Indica si la distribución es una distribución contínua o discreta.
    :type cont: bool

    :return: Una distribución (formato texto) con las características deseadas. Esta distribución se puede convertir
      en objeto de distribución SciPy o PyMC mediante la función texto_a_dist.
    :rtype: str

    """

    # La precisión que querremos de nuestras distribuciones aproximadas
    límite_precisión = 0.0001

    # Leer los límites intrínsicos del parámetro
    mín = líms[0]
    máx = líms[1]

    # Si el rango está al revés, arreglarlo.
    if rango[0] > rango[1]:
        rango = (rango[1], rango[0])

    # Asegurarse de que el rango cabe en los límites
    if rango[0] < mín or rango[1] > máx:
        raise ValueError('El rango tiene que caber entre los límites teoréticos del variable.')

    if certidumbre == 1:
        # Si no hay incertidumbre, usar una distribución uniforme entre el rango.
        if cont:
            dist = 'Uniforme~({}, {})'.format(rango[0], (rango[1] - rango[0]))
        else:
            dist = 'UnifDiscr~({}, {})'.format(rango[0], rango[1] + 1)

    else:
        # Si hay incertidumbre...

        # Primero, hay que asegurarse que el máximo y mínimo del rango no sean iguales
        if rango[0] == rango[1]:
            raise ValueError('Un rango para una distribucion con certidumbre inferior a 1 no puede tener valores '
                             'mínimos y máximos iguales.')

        # Una idea de la escala del rango de incertidumbre
        escala_rango = rango[1] / rango[0]  # Para hacer: ¿utilizar distribuciones exponenciales para escalas grandes?

        # Ahora, asignar una distribución según cada caso posible
        if mín == -np.inf:
            if máx == np.inf:  # El caso (-inf, +inf)
                if cont:
                    mu = np.average(rango)
                    # Calcular sigma por dividir el rango por el inverso (bilateral) de la distribución cumulativa.
                    sigma = ((rango[1] - rango[0]) / 2) / estad.norm.ppf((1 - certidumbre) / 2 + certidumbre)
                    dist = 'Normal~({}, {})'.format(mu, sigma)
                else:
                    raise ValueError('No se puede especificar a prioris con niveles de certidumbres inferiores a 100% '
                                     'con parámetros discretos en el rango (-inf, +inf).')

            else:  # El caso (-np.inf, R)
                raise ValueError('Tikón no tiene funcionalidades de distribuciones a priori en intervalos (-inf, R). '
                                 'Puedes crear un variable en el intervalo (R, inf) y utilisar su valor negativo en '
                                 'las ecuaciones.')

        else:
            if máx == np.inf:  # El caso [R, +inf)
                if cont:

                    # Primero vamos a intentar crear una distribución gamma con la densidad especificada
                    # (certidumbre) entre el rango especificado y 50% de la densidad no especificada de cada
                    # lado del rango (así asegurándose que la densidad esté más o menos bien distribuida a través
                    # del rango).

                    área_cola = (1 - certidumbre) / 2  # La densidad que querremos de cada lado (cola) del rango

                    # La función de optimización.
                    def calc_ajust_gamma_1(x):
                        """
                        Emplea un rango normalizado y toma como único argumento el parámetro a de la distribución
                        gamma; devuelve el ajuste de la distribución.

                        :param x: una matriz NumPy con los parámetros para calibrar. x[0] = a
                        :type x: np.ndarray

                        :return: El ajust del modelo
                        :rtype: float
                        """

                        # Primero, calcular dónde hay que ponder el límite inferior para tener la densidad querrida
                        # a la izquierda de este límite.
                        mín_ajust = estad.gamma.ppf(área_cola, a=x[0])

                        # Ahora, calcular el límite superior proporcional (según el rango y límite teorético
                        # especificados).
                        máx_ajust = mín_ajust / (rango[0] - mín) * (rango[1] - mín)

                        # Calcular a cuál punto la densidad abajo del rango superior coincide con la densidad
                        # deseada.
                        ajust = abs(estad.gamma.cdf(máx_ajust, a=x[0]) - (1 - área_cola))

                        return ajust  # Devolver el ajuste del modelo.

                    # Hacer la optimización
                    opt = minimizar(calc_ajust_gamma_1, x0=np.array([1]),
                                    bounds=[(1, None)])

                    # Calcular la escala
                    escala = (rango[0] - mín) / estad.gamma.ppf(área_cola, a=opt.x[0])

                    # Calcular los parámetros
                    paráms = [opt.x[0], mín, escala]

                    # Validar la optimización
                    valid = abs((estad.gamma.cdf(rango[1], a=paráms[0], loc=paráms[1], scale=paráms[2]) -
                                 estad.gamma.cdf(rango[0], a=paráms[0], loc=paráms[1], scale=paráms[2])) -
                                certidumbre)

                    # Si validó bien, todo está bien.
                    if valid < límite_precisión:
                        dist = 'Gamma~({}, {}, {})'.format(paráms[0], paráms[1], paráms[2])

                    else:
                        # Si no validó bien, intentaremos otra cosa. Ahora vamos a permitir que el límite inferior
                        # de la distribución gamma cambie un poco.
                        # Esto puede ayudar en casos donde rango[1] - rango[0] << rango[0] - mín

                        def calc_ajust_gamma_2(x):
                            """
                            Emplea un rango normalizado; devuelve el ajuste de la distribución.

                            :param x: una matriz NumPy con los parámetros para calibrar. x[0] = a, x[1] = loc.
                            :type x: np.ndarray

                            :return: El ajust del modelo
                            :rtype: float
                            """

                            # Primero, calcular dónde hay que ponder el límite inferior para tener la densidad querrida
                            # a la izquierda de este límite.
                            mín_ajust = estad.gamma.ppf(área_cola, a=x[0], loc=x[1])

                            # Ahora, calcular el límite superior proporcional (según el rango y límite teorético
                            # especificados).
                            máx_ajust = mín_ajust / (rango[0] - mín) * (rango[1] - mín)

                            # Calcular a cuál punto la densidad abajo del rango superior coincide con la densidad
                            # deseada.
                            ajust = abs(estad.gamma.cdf(máx_ajust, a=x[0], loc=x[1]) - (1 - área_cola))

                            return ajust

                        opt = minimizar(calc_ajust_gamma_2, x0=np.array([1, mín]),
                                        bounds=[(1, None), (mín, None)])

                        escala = (rango[0] - mín) / estad.gamma.ppf(área_cola, a=opt.x[0], loc=opt.x[1])

                        paráms = [opt.x[0], opt.x[1] * escala + mín, escala]

                        # Validar que todo esté bien.
                        valid = abs((estad.gamma.cdf(rango[1], a=paráms[0], loc=paráms[1], scale=paráms[2]) -
                                     estad.gamma.cdf(rango[0], a=paráms[0], loc=paráms[1], scale=paráms[2])) -
                                    certidumbre)

                        if valid < límite_precisión:
                            # Si está bien, allí guardamos el resultado.
                            dist = 'Gamma~({}, {}, {})'.format(paráms[0], paráms[1], paráms[2])

                        else:
                            # Si todavía logramos encontrar una buena distribución, reconocemos que no podemos hacer
                            # milagros y abandonamos la condición que las dos colas deben tener el mismo área. Siempre
                            # guardamos el mínimo de la función gamma en mín (el mínimo teorético del parámetro
                            # especificado por el usuario).
                            # Esto puede ayudar en casos donde rango[0] - mín << rango[1] - mín y certidumbre >> 0.

                            # OTRA función de optimización...
                            mx_ajust = 5  # 5 es un buen número para evitar problemas.

                            def calc_ajust_gamma_3(x):
                                """
                                Emplea un rango normalizado y toma como único argumento el parámetro a de la
                                distribución gamma; devuelve el ajuste de la distribución.

                                :param x: x[0] es el parámetro a de la distribución gamma, y x[1] la escala de la
                                distribución.
                                :type x: np.ndarray

                                :return: El ajust del modelo
                                :rtype: float

                                """

                                máx_ajust = mx_ajust  # El rango superior

                                # El rango inferior proporcional
                                mín_ajust = (rango[0] - mín) * máx_ajust / (rango[1] - mín)

                                # La densidad de la distribución abajo del límite inferior del rango
                                dens_sup = 1 - estad.gamma.cdf(máx_ajust, a=x[0], scale=x[1])

                                # La densidad adentro de los límites del rango
                                dens_líms = estad.gamma.cdf(máx_ajust, a=x[0], scale=x[1]) - \
                                            estad.gamma.cdf(mín_ajust, a=x[0], scale=x[1])

                                # Devolver una medida del ajuste de la distribución. Lo más importante sería la
                                # densidad adentro del rango, pero también la densidad en la cola superior.
                                return abs(dens_líms - certidumbre) * 100 + abs(dens_sup - área_cola)

                            opt = minimizar(calc_ajust_gamma_3, x0=np.array([2, 1]),
                                            bounds=[(1, None), (1e-10, None)])

                            paráms = [opt.x[0], mín, (rango[1] - mín) / mx_ajust * opt.x[1]]

                            # Validar que todo esté bien.
                            valid = abs((estad.gamma.cdf(rango[1], a=paráms[0], loc=paráms[1], scale=paráms[2]) -
                                         estad.gamma.cdf(rango[0], a=paráms[0], loc=paráms[1], scale=paráms[2])) -
                                        certidumbre)

                            # Si el error en la densidad de la distribución TODAVÍA queda superior al límite
                            # acceptable...
                            if valid > límite_precisión:
                                raise ValueError('Error en la optimización de la distribución especificada. '
                                                 'Esto es un error de programación, así que mejor se queje al '
                                                 'programador. ({})'.format(correo))

                            # Guardar la distribución de todo modo.
                            dist = 'Gamma~({}, {}, {})'.format(paráms[0], paráms[1], paráms[2])

                else:
                    raise ValueError('Tikon no tiene funciones para especificar a priores discretos en un intervalo'
                                     '(R, inf). Si lo quieres añadir, ¡dale pués!')

            else:  # El caso (R, R)
                if cont:

                    # Una distribución normal truncada con límites especificados y mu en la mitad del rango
                    # especificado
                    mu = (rango[0] + rango[1]) / 2
                    opt = minimizar(lambda x: abs((estad.truncnorm.cdf(rango[1], a=(mín - mu) / x, b=(máx - mu) / x,
                                                                       loc=mu, scale=x) -
                                                   estad.truncnorm.cdf(rango[0], a=(mín - mu) / x, b=(máx - mu) / x,
                                                                       loc=mu, scale=x)) -
                                                  certidumbre),
                                    # bounds=[(1e-10, None)],  # para hacer: activar este
                                    x0=np.array([rango[1] - rango[0]]),
                                    method='Nelder-Mead')

                    paráms = np.array([mu, opt.x[0], (mín - mu) / opt.x[0], (máx - mu) / opt.x[0]])

                    # Validar la optimización
                    valid = abs((estad.truncnorm.cdf(rango[1], loc=paráms[0], scale=paráms[1],
                                                     a=paráms[2], b=paráms[3]) -
                                 estad.truncnorm.cdf(rango[0], loc=paráms[0], scale=paráms[1],
                                                     a=paráms[2], b=paráms[3], ))
                                - certidumbre)

                    # Si validó bien, guardar la distribución...
                    if valid < límite_precisión:
                        dist = 'NormalTrunc~({}, {}, {}, {})'.format(paráms[2], paráms[3], paráms[0], paráms[1])

                    else:
                        # ... si no, intentar con una distribución beta.
                        opt = minimizar(
                            lambda x: abs((estad.beta.cdf(rango[1], a=x[0], b=x[1], loc=mín, scale=máx - mín) -
                                           estad.beta.cdf(rango[0], a=x[0], b=x[1], loc=mín, scale=máx - mín)) -
                                          certidumbre), bounds=[(1e-10, None), (1e-10, None)],
                            x0=np.array([1e-10, 1e-10]))

                        paráms = [opt.x[0], opt.x[1], mín, máx - mín]

                        valid = abs((estad.beta.cdf(rango[1], a=paráms[0], b=paráms[1], loc=mín, scale=máx - mín) -
                                     estad.beta.cdf(rango[0], a=paráms[0], b=paráms[1], loc=mín, scale=máx - mín)) -
                                    certidumbre)

                        # Avizar si todavía no optimizó bien
                        if valid > límite_precisión:
                            raise ValueError('Error en la optimización de la distribución especificada. Esto es un '
                                             'error de programación, así que mejor se queje al '
                                             'programador. ({})'.format(correo))

                        dist = 'Beta~({}, {}, {}, {})'.format(paráms[0], paráms[1], paráms[2], paráms[3])

                else:
                    raise ValueError('Tikon no tiene funciones para especificar a priores discretos en un intervalo'
                                     '(R, inf). Si lo quieres añadir, ¡dale pués!')

    return dist


def límites_a_texto_dist(límites, cont=True):
    """
    Esta función toma un "tuple" de límites para un parámetro de una función y devuelve una descripción de una
    destribución a priori no informativa (espero) para los límites dados. Se usa en la inicialización de las
    distribuciones de los parámetros de ecuaciones.

    :param límites: Las límites para los valores posibles del parámetro. Para límites infinitas, usar np.inf y
    -np.inf. Ejemplos: (0, np.inf), (-10, 10), (-np.inf, np.inf). No se pueden especificar límites en el rango
    (-np.inf, R), donde R es un número real. En ese caso, usar las límites (R, np.inf) y tomar el negativo del
    variable en las ecuaciones que lo utilisan.
    :type límites: tuple

    :param cont: Determina si el variable es continuo o discreto
    :type cont: bool

    :return: Descripción de la destribución no informativa que conforme a las límites especificadas. Devuelve una
    cadena de carácteres, que facilita guardar las distribuciones de los parámetros. Otras funciones la convertirán
    en distribución de scipy o de pymc donde necesario.
    :rtype: str
    """

    # Sacar el mínimo y máximo de los límites.
    mín = límites[0]
    máx = límites[1]

    # Verificar que máx > mín
    if máx <= mín:
        raise ValueError('El valor máximo debe ser superior al valor máximo.')

    # Pasar a través de todos los casos posibles
    if mín == -np.inf:
        if máx == np.inf:  # El caso (-np.inf, np.inf)
            if cont:
                dist = 'Normal~(0, 1e10)'
            else:
                dist = 'UnifDiscr~(1e-10, 1e10)'

        else:  # El caso (-np.inf, R)
            raise ValueError('Tikón no tiene funcionalidades de distribuciones a priori en intervalos (-inf, R). Puedes'
                             'crear un variable en el intervalo (R, inf) y utilisar su valor negativo en las '
                             'ecuaciones.')

    else:
        if máx == np.inf:  # El caso (R, np.inf)
            if cont:
                dist = 'Exponencial~({}, 1e10)'.format(mín)
            else:
                loc = mín - 1  # Para incluir mín en los valores posibles de la distribución.
                dist = 'Geométrica~(1e-8, {})'.format(loc)

        else:  # El caso (R, R)
            if máx == mín:
                dist = 'Degenerado~({})'.format(máx)
            else:
                if cont:
                    esc = máx - mín
                    dist = 'Uniforme~({}, {})'.format(mín, esc)
                else:
                    dist = 'UnifDiscr~({}, {})'.format(mín, mín + 1)

    return dist


def dists_a_líms(l_dists, por_dist_ingr):
    """
    Esta función genera límites de densidad para cada distribución en una lista de distribuciones.

    :param l_dists: Una lista de las distribuciones
    :type l_dists: list[estad.rv_frozen | np.ndarray]

    :param por_dist_ingr: La fracción de la densidad de la distribución a dejar afuera de los límites
    :type por_dist_ingr: float

    :return: Una lista de los límites, con cada límite sí mismo en formato de lista
    :rtype: list[list[float]]
    """

    # Asegurarse que la lista de distribuciones sea una lista
    if type(l_dists) is not list:
        l_dists = [l_dists]

    # Las superficies de las colas que hay que dejar afuera del rango de los límites
    colas = ((1 - por_dist_ingr) / 2, 0.5 + por_dist_ingr / 2)

    # Inicializar la lista de límites
    l_líms = []

    for dist in l_dists:
        # Para cada distribución...

        # Calcular los porcentiles según el tipo de distribución
        if isinstance(dist, estad._distn_infrastructure.rv_frozen):
            # Para distribuciones SciPy...
            l_líms.append([dist.ppf(colas[0]), dist.ppf(colas[1])])
        elif isinstance(dist, np.ndarray):
            # Para distribuciones en formato de matriz NumPy...
            l_líms.append([np.percentile(dist, colas[0] * 100, np.percentile(dist, colas[1] * 100))])
        elif isinstance(dist, str):
            # Para distribuciones en formato de texto...
            d_sp = texto_a_dist(dist)  # Convertir a SciPy
            l_líms.append([d_sp.ppf(colas[0]), d_sp.ppf(colas[1])])  # Calcular los límites
        else:
            # Si no reconocimos el tipo de la distribución, hay un error.
            raise ValueError('Tipo de distribución "{}" no reconocido.'.format(type(dist)))

    return l_líms


def ajustar_dist(datos, límites, cont, usar_pymc=False, nombre=None, lista_dist=None):
    """
    Esta función, tomando las límites teoréticas de una distribución y una serie de datos proveniendo de dicha
    distribución, escoge la distribución de Scipy o PyMC la más apropriada y ajusta sus parámetros.

    :param datos: Un vector de valores del parámetro
    :type datos: np.ndarray

    :param cont: Determina si la distribución es contínua (en vez de discreta)
    :type cont: bool

    :param usar_pymc: Determina si queremos una distribución de tipo PyMC (en vez de SciPy)
    :type usar_pymc: bool

    :param límites: Las límites teoréticas de la distribucion (p. ej., (0, np.inf), (-np.inf, np.inf), etc.)
    :type límites: tuple

    :param nombre: El nombre del variable, si vamos a generar un variable de PyMC
    :type nombre: str

    :param lista_dist: Una lista de los nombres de distribuciones a considerar. dist=None las considera todas.
    :type lista_dist: list

    :return: Distribución PyMC o de Scipyy su ajuste (p)
    :rtype: (pymc.Stochastic | estad.rv_frozen, float)

    """

    # Asegurarse de que, si queremos una distribución pymc, también se especificó un nombre para el variable.
    if usar_pymc and nombre is None:
        raise ValueError('Se debe especificar un nombre para el variable si quieres una distribución de PyMC.')

    # Separar el mínimo y el máximo de la distribución
    mín_parám, máx_parám = límites

    # Un diccionario para guardar el mejor ajuste
    mejor_ajuste = dict(dist=None, p=0.0)

    # Sacar las distribuciones del buen tipo (contínuas o discretas)
    if cont:
        categ_dist = 'cont'
    else:
        categ_dist = 'discr'

    dists_potenciales = [x for x in Ds.dists if Ds.dists[x]['tipo'] == categ_dist]

    if lista_dist is not None:
        dists_potenciales = [x for x in dists_potenciales if x in lista_dist]

    # Si queremos generar una distribución PyMC, guardar únicamente las distribuciones con objeto de PyMC disponible
    # (y lo mismo para SciPy).
    if usar_pymc is True:
        dists_potenciales = [x for x in dists_potenciales if Ds.dists[x]['pymc'] is not None]
    else:
        dists_potenciales = [x for x in dists_potenciales if Ds.dists[x]['scipy'] is not None]

    # Verificar que todavia queden distribuciones para considerar.
    if len(dists_potenciales) == 0:
        raise ValueError('Ninguna de las distribuciones especificadas es apropiada para el tipo de distribución.')

    # Para cada distribución potencial para representar a nuestros datos...
    for nombre_dist in dists_potenciales:

        # El diccionario de la distribución
        dic_dist = Ds.dists[nombre_dist]

        # El tipo de distribución (nombre SciPy)
        nombre_scipy = dic_dist['scipy'].name

        # El máximo y el mínimo de la distribución
        mín_dist, máx_dist = dic_dist['límites']

        # Verificar que los límites del parámetro y de la distribución sean compatibles
        lím_igual = (((mín_dist == mín_parám == -np.inf) or
                      (not np.isinf(mín_dist) and not np.isinf(mín_parám))) and
                     ((máx_dist == máx_parám == np.inf) or
                      (not np.isinf(máx_dist) and not np.isinf(máx_parám))))

        # Si son compatibles...
        if lím_igual:

            # Restringimos las posibilidades para las distribuciones a ajustar, si necesario
            if np.isinf(mín_parám):

                if np.isinf(máx_parám):
                    # Para el caso de un parámetro sín límites teoréticos (-inf, inf), no hay restricciones en la
                    # distribución.
                    restric = {}

                else:
                    # TIKON (por culpa de SciPy), no puede tomar distribuciones en (-inf, R].
                    raise ValueError('Tikon no puede tomar distribuciones en el intervalo (-inf, R]. Hay que '
                                     'cambiar tus ecuaciones para usar un variable en el intervalo [R, inf). '
                                     'Disculpas. Pero de verdad es la culpa del módulo SciPy.')
            else:

                if np.isinf(máx_parám):
                    # En el caso [R, inf), limitamos el valor inferior de la distribución al límite inferior del
                    # parámetro
                    restric = {'floc': mín_parám}

                else:
                    # En el caso [R, R], limitamos los valores inferiores y superiores de la distribución.
                    if nombre_dist == 'Uniforme' or nombre_dist == 'Beta':
                        restric = {'floc': mín_parám, 'fscale': máx_parám - mín_parám}
                    elif nombre_dist == 'NormalTrunc':
                        restric = {'floc': (máx_parám + mín_parám) / 2}
                    else:
                        raise ValueError(nombre_dist)

            # Ajustar los parámetros de la distribución SciPy para caber con los datos.
            if nombre_dist == 'Uniforme':
                # Para distribuciones uniformes, no hay nada que calibrar.
                args = tuple(restric.values())
            else:
                args = dic_dist['scipy'].fit(datos, **restric)

            # Medir el ajuste de la distribución
            p = estad.kstest(rvs=datos, cdf=nombre_scipy, args=args)[1]

            # Si el ajuste es mejor que el mejor ajuste anterior...
            if p >= mejor_ajuste['p']:

                # Guardarlo
                mejor_ajuste['p'] = p

                # Guardar también el objeto de la distribución, o de PyMC, o de SciPy, según lo que queremos
                if usar_pymc:
                    # Convertir los argumentos a formato PyMC
                    args_pymc, transform = paráms_scipy_a_pymc(tipo_dist=nombre_dist, paráms=args)

                    # Y crear la distribución.
                    dist = dic_dist['pymc'](nombre, *args_pymc)

                    if transform['mult'] != 1:
                        dist = dist * transform['mult']

                    if transform['sum'] != 0:
                        dist = dist + transform['sum']
                    mejor_ajuste['dist'] = dist

                else:

                    mejor_ajuste['dist'] = dic_dist['scipy'](*args)

    # Si no logramos un buen aujste, avisar al usuario.
    if mejor_ajuste['p'] <= 0.10:
        avisar('El ajuste de la mejor distribución quedó muy mal (p = %f).' % round(mejor_ajuste['p'], 4))

    # Devolver la distribución con el mejor ajuste, tanto como el valor de su ajuste.
    return mejor_ajuste['dist'], mejor_ajuste['p']


def paráms_scipy_a_pymc(tipo_dist, paráms):
    """
    Esta función transforma un tuple de parámetros de distribución SciPy a parámetros correspondientes para una función
    de PyMC.

    :param tipo_dist: El tipo de distribución.
    :type tipo_dist: str

    :param paráms: Los parámetros SciPy
    :type paráms: tuple

    :return: Un tuple de parámetros PyMC y un diccionario de transformaciones adicionales necesarias.
    :rtype: (tuple, dict)

    """

    transform_pymc = {'mult': 1, 'sum': 0}

    if tipo_dist == 'Beta':
        paráms_pymc = (paráms[0], paráms[1])
        transform_pymc['sum'] = paráms[2]
        transform_pymc['mult'] = paráms[3]

    elif tipo_dist == 'Cauchy':
        paráms_pymc = (paráms[0], paráms[1])

    elif tipo_dist == 'Chi2':
        paráms_pymc = (paráms[0],)
        transform_pymc['sum'] = paráms[1]
        transform_pymc['mult'] = paráms[2]

    elif tipo_dist == 'Exponencial':
        paráms_pymc = (1 / paráms[1],)
        transform_pymc['sum'] = paráms[0]

    elif tipo_dist == 'WeibullExponencial':
        paráms_pymc = (paráms[0], paráms[1], paráms[2], paráms[3])

    elif tipo_dist == 'Gamma':
        paráms_pymc = (paráms[0], 1 / paráms[2])
        transform_pymc['sum'] = paráms[1]

    elif tipo_dist == 'MitadCauchy':
        paráms_pymc = (paráms[0], paráms[1])

    elif tipo_dist == 'MitadNormal':
        paráms_pymc = (1 / paráms[1] ** 2,)
        transform_pymc['sum'] = paráms[0]

    elif tipo_dist == 'GammaInversa':
        paráms_pymc = (paráms[0], paráms[2])
        transform_pymc['sum'] = paráms[1]

    elif tipo_dist == 'Laplace':
        paráms_pymc = (paráms[0], 1 / paráms[1])

    elif tipo_dist == 'Logística':
        paráms_pymc = (paráms[0], 1 / paráms[1])

    elif tipo_dist == 'LogNormal':
        paráms_pymc = (np.log(paráms[2]), 1 / (paráms[0] ** 2))
        transform_pymc['mult'] = paráms[2]
        transform_pymc['sum'] = paráms[1]

    elif tipo_dist == 'TNoCentral':
        paráms_pymc = (paráms[2], 1 / paráms[3], paráms[0])

    elif tipo_dist == 'Normal':
        paráms_pymc = (paráms[0], 1 / paráms[1] ** 2)

    elif tipo_dist == 'Pareto':
        paráms_pymc = (paráms[0], paráms[2])
        transform_pymc['sum'] = paráms[1]

    elif tipo_dist == 'T':
        paráms_pymc = (paráms[0],)
        transform_pymc['sum'] = paráms[1]
        transform_pymc['mult'] = 1 / np.sqrt(paráms[2])

    elif tipo_dist == 'NormalTrunc':
        mu = paráms[2]
        mín, máx = min(paráms[0], paráms[1]), max(paráms[0], paráms[1])  # SciPy, aparamente, los puede inversar
        paráms_pymc = (mu, 1 / paráms[3] ** 2, mín * paráms[3] + mu, máx * paráms[3] + mu)

    elif tipo_dist == 'Uniforme':
        # Normalizar la distribución Uniforme para PyMC. Sino hace muchos problemas.
        paráms_pymc = (0, 1)
        transform_pymc['sum'] = paráms[0]
        transform_pymc['mult'] = paráms[1]

    elif tipo_dist == 'VonMises':
        paráms_pymc = (paráms[1], paráms[0])
        transform_pymc['mult'] = paráms[2]

    elif tipo_dist == 'Weibull':
        raise NotImplementedError  # Para hacer: implementar la distrubución Weibull (minweibull en SciPy)

    elif tipo_dist == 'Bernoulli':
        paráms_pymc = (paráms[0],)
        transform_pymc['sum'] = paráms[1]

    elif tipo_dist == 'Binomial':
        paráms_pymc = (paráms[0], paráms[1])
        transform_pymc['sum'] = paráms[2]

    elif tipo_dist == 'Geométrica':
        paráms_pymc = (paráms[0],)
        transform_pymc['sum'] = paráms[1]

    elif tipo_dist == 'Hypergeométrica':
        paráms_pymc = (paráms[1], paráms[0], paráms[2])
        transform_pymc['sum'] = paráms[3]

    elif tipo_dist == 'BinomialNegativo':
        paráms_pymc = (paráms[1], paráms[0])
        transform_pymc['sum'] = paráms[2]

    elif tipo_dist == 'Poisson':
        paráms_pymc = (paráms[0],)
        transform_pymc['sum'] = paráms[1]

    elif tipo_dist == 'UnifDiscr':
        paráms_pymc = (paráms[0], paráms[1] - 1)

    else:
        raise ValueError('La distribución %s no existe en la base de datos de Tikon para distribuciones PyMC.' %
                         tipo_dist)

    return paráms_pymc, transform_pymc


def numerizar(f, c=None):
    """
    Esta función toma un diccionaro o una lista de estructura arbitraria y convierte todos
      los objetos adentro en forma numérica. Es particularmente útil para sacar los valores
      de variables de PyMC durante una corrida del modelo.
      Notar que puede tomar diccionarios, listas, listas de diccionarios, diccionarios de listas,
      etc. No mmodifica el objeto original, sino genera una copia.

    :param f: El diccionario o lista para numerizar.
    :type f: dict | list

    :param c: Para recursiones. No especificar al llamar la función.
    :type c: dict | list

    :return: El diccionario o la lista numerizada.
    :rtype: dict | list

    """

    if c is None:
        if type(f) is list:
            c = []
        elif type(f) is dict:
            c = {}

    if type(f) is list:
        for n, v in enumerate(f):
            if type(v) is dict:
                c.append({})
                numerizar(v, c=c[n])
            elif type(v) is list:
                c.append([])
                numerizar(v, c=c[n])
            else:
                c[n] = v.astype(float)

    elif type(f) is dict:
        for ll, v in f.items():

            if type(v) is dict:
                c[ll] = {}
                numerizar(v, c=c[ll])

            elif type(v) is list:
                c[ll] = []
                numerizar(v, c=c[ll])

            else:
                c[ll] = v.astype(float)

    else:
        raise ValueError

    return c


def validar_matr_pred(matr_predic, vector_obs):
    """
    Esta función valida una matriz de predicciones de un variable según los valores observados correspondientes.

    :param matr_predic: La matriz de predicciones. Eje 0 = incertidumbre estocástica, eje 1 = incertidumbre
      paramétrica, eje 2 = día.
    :type matr_predic: np.ndarray

    :param vector_obs: El vector de las observaciones. Eje 0 = día.
    :type vector_obs: np.ndarray

    :return: Devuelve los valores de R2, de RCNEP (Raíz cuadrada normalizada del error promedio), y el R2 de la
    exactitud de los intervalos de confianza (1.0 = exactitud perfecta).
    :rtype: (float, float, float)
    """

    # Quitar observaciones que faltan
    matr_predic = matr_predic[:, :, ~np.isnan(vector_obs)]
    vector_obs = vector_obs[~np.isnan(vector_obs)]

    # El número de días de predicciones y observaciones
    n_rep_estoc, n_rep_parám, n_días = matr_predic.shape

    # Combinar los dos ejes de incertidumbre (repeticiones estocásticas y paramétricas)
    matr_predic = matr_predic.reshape((n_rep_estoc * n_rep_parám, n_días))

    # Calcular el promedio de todas las repeticiones de predicciones
    vector_predic = matr_predic.mean(axis=0)

    # Calcular R cuadrado
    r2 = calc_r2(vector_predic, vector_obs)

    # Raíz cuadrada normalizada del error promedio
    rcnep = np.divide(np.sqrt(np.square(vector_predic - vector_obs).mean()), np.mean(vector_obs))

    # Validar el intervalo de incertidumbre
    confianza = np.empty_like(vector_obs, dtype=float)
    for n in range(n_días):
        perc = estad.percentileofscore(matr_predic[..., n], vector_obs[n]) / 100
        confianza[n] = abs(0.5 - perc) * 2

    confianza.sort()

    percentiles = np.divide(np.arange(1, n_días + 1), n_días)

    r2_percentiles = calc_r2(confianza, percentiles)

    return {'r2': r2, 'rcnep': rcnep, 'r2_percentiles': r2_percentiles}


def calc_r2(y_obs, y_pred):
    """
    Calcula el coeficiente de determinación (R2) entre las predicciones de un modelo y los valores observados.
    Notar que calcula R2 *entre valores predichos y observados*, y *no* entre un variable predictor y dependiente.
    Para este últimeo, emplear `scipy.stats.linregress`.

    :param y_obs: Valores observados.
    :type y_obs: np.ndarray
    :param y_pred: Valores predichos. (y_sombrero)
    :type y_pred: np.ndarray
    :return: El coeficiente de determinación, R2.
    :rtype: float
    """
    prom_y = np.mean(y_obs)
    sc_rs = np.sum(np.subtract(y_obs, y_pred) ** 2)
    sc_reg = np.sum(np.subtract(y_pred, prom_y) ** 2)
    sc_t = sc_rs + sc_reg

    r2 = 1 - np.divide(sc_rs, sc_t)

    return r2


def paráms_scipy_a_dist_pymc3(tipo_dist, paráms):
    if pm3 is None:
        raise ImportError(
            'PyMC 3 (pymc3) no está instalado en esta máquina.\nDeberías de instalarlo un día. De verdad que'
            'es muy chévere.')

    transform_pymc = {'mult': 1, 'sum': 0}

    if not Ds.obt_dist(dist=tipo_dist, tipo='pymc3'):
        raise ValueError('La distribución "{}" no parece existir en Tiko\'n al momento.'.format(tipo_dist))

    if tipo_dist == 'Beta':
        dist_pm3 = pm3.Beta(alpha=paráms['a'], beta=paráms['b'])
        transform_pymc['mult'] = paráms['scale']
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'Cauchy':
        dist_pm3 = pm3.Cauchy(alpha=paráms['a'], beta=paráms['scale'])

    elif tipo_dist == 'Chi2':
        dist_pm3 = pm3.ChiSquared(nu=paráms['df'])
        transform_pymc['mult'] = paráms['scale']
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'Exponencial':
        dist_pm3 = pm3.Exponential(lam=1 / paráms['scale'])
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'Gamma':
        dist_pm3 = pm3.Gamma(alpha=paráms['alpha'], beta=1 / paráms['scale'])
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'MitadCauchy':
        dist_pm3 = pm3.HalfCauchy(beta=paráms['scale'])
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'MitadNormal':
        dist_pm3 = pm3.HalfNormal(sd=paráms['scale'])
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'GammaInversa':
        dist_pm3 = pm3.InverseGamma(alpha=paráms['a'], beta=paráms['scale'])
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'Laplace':
        dist_pm3 = pm3.Laplace(mu=paráms['loc'], b=paráms['scale'])

    elif tipo_dist == 'Logística':
        paráms_pymc = (paráms[0], 1 / paráms[1])
        dist_pm3 = pm3.Logistic(mu=paráms['loc'], s=paráms['scale'])

    elif tipo_dist == 'LogNormal':
        dist_pm3 = pm3.Lognormal(mu=paráms['loc'], sd=paráms['scale'])  # para hacer: verificar

    elif tipo_dist == 'Normal':
        dist_pm3 = pm3.Normal(mu=paráms['loc'], sd=paráms['scale'])

    elif tipo_dist == 'Pareto':
        dist_pm3 = pm3.Pareto(alpha=paráms['b'], m=paráms['scale'])  # para hacer: verificar

    elif tipo_dist == 'T':
        dist_pm3 = pm3.StudentT(nu=paráms['df'], mu=paráms['loc'], sd=paráms['scale'])  # para hacer: verificar

    elif tipo_dist == 'NormalTrunc':
        mín, máx = min(paráms[0], paráms[1]), max(paráms[0], paráms[1])  # SciPy, aparamente, los puede inversar
        mín_abs, máx_abs = mín * paráms['scale'] + paráms['mu'], máx * paráms['scale'] + paráms['mu']
        NormalTrunc = pm3.Bound(pm3.Normal, lower=mín_abs, upper=máx_abs)
        dist_pm3 = NormalTrunc(mu=paráms['loc'], sd=paráms['scale'])

    elif tipo_dist == 'Uniforme':
        dist_pm3 = pm3.Uniform(paráms['loc'], paráms['loc'] + paráms['scale'])

    elif tipo_dist == 'VonMises':
        dist_pm3 = pm3.VonMises(mu=paráms['loc'], kappa=paráms['kappa'])
        transform_pymc['mult'] = paráms['scale']

    elif tipo_dist == 'Weibull':
        raise NotImplementedError  # Para hacer: implementar la distrubución Weibull (minweibull en SciPy)
        dist_pm3 = pm3.Weibull()

    elif tipo_dist == 'Bernoulli':
        dist_pm3 = pm3.Bernoulli(p=paráms['p'])
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'Binomial':
        dist_pm3 = pm3.Binomial(n=paráms['n'], p=paráms['p'])
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'Geométrica':
        dist_pm3 = pm3.Geometric(p=paráms['p'])
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'BinomialNegativo':
        n = paráms['n']
        p = paráms['p']
        dist_pm3 = pm3.NegativeBinomial(mu=n(1-p)/p, alpha=n)  # para hacer: verificar
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'Poisson':
        dist_pm3 = pm3.Poisson(mu=paráms['mu'])
        transform_pymc['sum'] = paráms['loc']

    elif tipo_dist == 'UnifDiscr':
        dist_pm3 = pm3.DiscreteUniform(lower=paráms['low'], upper=paráms['high'])
        transform_pymc['sum'] = paráms['loc']

    else:
        raise ValueError('La distribución %s no existe en la base de datos de Tikon para distribuciones de PyMC 3.' %
                         tipo_dist)

    return dist_pm3
