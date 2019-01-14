import math as mat
from warnings import warn as avisar

import numpy as np
from scipy import stats as estad

from tikon0.Matemáticas import Distribuciones as Ds


class VarAlea(object):

    @classmethod
    def de_líms(cls, líms, cont, nombre):
        """
                Esta función toma una "tupla" de límites para un parámetro de una función y devuelve una distribución
                Scipy correspondiente. Se usa en la inicialización de las
                distribuciones de los parámetros de ecuaciones.

                :param líms: Los límites para los valores posibles del parámetro. Para límites infinitas, usar np.inf y
                -np.inf. Ejemplos: (0, np.inf), (-10, 10), (-np.inf, np.inf).
                :type líms: tuple

                :param cont: Determina si el variable es continuo o discreto
                :type cont: bool

                :param nombre: Nombre para algunos tipos de distribuciones. Inútil para SciPy.
                :type nombre: str

                :return: Destribución no informativa conforme a las límites especificadas.
                :rtype: str
                """

        tipo_dist, paráms = _líms_a_dist(líms, cont)

        return cls(tipo_dist=tipo_dist, paráms=paráms, nombre=nombre)

    @classmethod
    def aprox_dist(cls, datos, líms, cont, lista_dist=None):
        """

        :param datos:
        :type datos:
        :param líms:
        :type líms:
        :param cont:
        :type cont:
        :param lista_dist:
        :type lista_dist:
        :return:
        :rtype: dict[str, VarSciPy | str | float | dict]
        """

        # Separar el mínimo y el máximo de la distribución
        mín_parám, máx_parám = líms

        # Un diccionario para guardar el mejor ajuste
        mejor_ajuste = dict(prms={}, tipo='', p=0.0)

        # Sacar las distribuciones del buen tipo (contínuas o discretas)
        if cont:
            categ_dist = 'cont'
        else:
            categ_dist = 'discr'

        dists_potenciales = [x for x in Ds.dists if Ds.dists[x]['tipo'] == categ_dist]

        if lista_dist is not None:
            dists_potenciales = [x for x in dists_potenciales if x in lista_dist]

        dists_potenciales = [x for x in dists_potenciales if x in cls.dists_disp()]

        # Verificar que todavia queden distribuciones para considerar.
        if len(dists_potenciales) == 0:
            raise ValueError('Ninguna de las distribuciones especificadas es apropiada para el tipo de distribución.')

        # Para cada distribución potencial para representar a nuestros datos...
        for nombre_dist in dists_potenciales:

            # El diccionario de la distribución
            dic_dist = Ds.dists[nombre_dist]

            # El máximo y el mínimo de la distribución
            mín_dist, máx_dist = dic_dist['límites']

            # Verificar que los límites del parámetro y de la distribución sean compatibles
            lím_igual = (((mín_dist == mín_parám == -np.inf) or
                          (not np.isinf(mín_dist) and not np.isinf(mín_parám))) and
                         ((máx_dist == máx_parám == np.inf) or
                          (not np.isinf(máx_dist) and not np.isinf(máx_parám))))

            # Si son compatibles...
            if lím_igual:

                if mín_parám == -np.inf and máx_parám != np.inf:
                    inv = True
                else:
                    inv = False

                # Restringimos las posibilidades para las distribuciones a ajustar, si necesario
                if np.isinf(mín_parám):

                    if np.isinf(máx_parám):
                        # Para el caso de un parámetro sín límites teoréticos (-inf, inf), no hay restricciones en la
                        # distribución.
                        restric = {}

                    else:
                        raise ValueError('No debería ser posible llegar hasta este error.')
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
                        elif nombre_dist == 'VonMises':
                            restric = {'floc': mín_parám + mat.pi, 'fscale': máx_parám - mín_parám}
                        else:
                            raise ValueError(nombre_dist)

                # Ajustar los parámetros de la distribución SciPy para caber con los datos.
                if nombre_dist == 'Uniforme':
                    # Para distribuciones uniformes, no hay nada que calibrar.
                    prms = {'ubic': restric['floc'], 'escl': restric['fscale']}
                else:
                    try:
                        tupla_prms = dic_dist['scipy'].fit(datos, **restric)
                        l_prms = dic_dist['paráms']
                        prms = {p: v for p, v in zip(l_prms, tupla_prms)}
                    except:
                        prms = None

                if prms is not None:
                    # Medir el ajuste de la distribución
                    prms_scipy = prms.copy()
                    prms_scipy['loc'] = prms_scipy.pop('ubic')
                    prms_scipy['scale'] = prms_scipy.pop('escl')
                    p = estad.kstest(rvs=datos, cdf=dic_dist['scipy'](**prms_scipy).cdf)[1]

                    # Si el ajuste es mejor que el mejor ajuste anterior...
                    if p > mejor_ajuste['p'] or mejor_ajuste['tipo'] == '':
                        # Guardarlo
                        mejor_ajuste['p'] = p
                        mejor_ajuste['prms'] = prms
                        mejor_ajuste['tipo'] = nombre_dist

                        # Inversar la distribución sinecesario
                        if inv and 'escl' in prms:
                            prms['escl'] = -prms['escl']

        # Si no logramos un buen aujste, avisar al usuario.
        if mejor_ajuste['p'] <= 0.10:
            avisar('El ajuste de la mejor distribución quedó muy mal (p = %f).' % round(mejor_ajuste['p'], 4))
            # Para hacer: ¿Permitir transformaciones adicionales a los datos?

        # Devolver la distribución con el mejor ajuste, tanto como el valor de su ajuste.
        resultado = {'dist': VarSciPy(tipo_dist=mejor_ajuste['tipo'], paráms=mejor_ajuste['prms']),
                     'nombre': mejor_ajuste['tipo'],
                     'prms': mejor_ajuste['prms'],
                     'p': mejor_ajuste['p']}

        return resultado


class VarSpotPy(VarAlea):

    def __init__(símismo, nombre, tipo_dist, paráms, transf=None):
        """

        :param tipo_dist: El tipo de distribución. (P.ej., ``Normal``, ``Uniforme``, etc.)
        :type tipo_dist: str
        :param paráms:
        :type paráms: dict
        :param transf:
        :type transf: dict[str, str | float | int]
        """

        super().__init__(tipo_dist=tipo_dist, paráms=paráms)

        símismo.traza = np.array([])

        símismo.val = None
        símismo.modelo = None

        nombre = re.sub('\W|^(?=\d)', '_', nombre)
        símismo.nombre = nombre

        # Sacar los límites y también verificar que existe este variable
        if tipo_dist in Ds.dists:
            líms_dist = Ds.dists[tipo_dist]['límites']
        elif tipo_dist in ['NormalExp', 'LogitInv']:
            líms_dist = (-np.inf, np.inf)
        else:
            raise ValueError('La distribución %s no existe en la base de datos de Tikon para distribuciones SpotPy.' %
                             tipo_dist)

        # Hacer transformaciones de forma de distribución si necesario

        # El caso (-inf, R] se transforma a [-R, inf)
        if líms_dist[0] == -np.inf and líms_dist[1] != np.inf:
            líms_dist[0] = -líms_dist[1]
            líms_dist[1] = np.inf
            inv = True  # Invertimos la distribución
        else:
            inv = False

        # Generar la distribución y sus parámetros
        if tipo_dist == 'Chi2':
            raise NotImplementedError
            var = spotpy.parameter.Chisquare(símismo.nombre, dt=paráms['df'])

        elif tipo_dist == 'Exponencial':
            var = spotpy.parameter.Exponential(símismo.nombre, scale=1)

        elif tipo_dist == 'Gamma':
            raise NotImplementedError
            var = spotpy.parameter.Gamma(símismo.nombre, k=paráms['a'])

        elif tipo_dist == 'LogNormal':
            raise NotImplementedError
            var = spotpy.parameter.logNormal(símismo.nombre)

        elif tipo_dist == 'Normal':
            var = spotpy.parameter.Normal(símismo.nombre, mean=0, stddev=1)

        elif tipo_dist == 'Uniforme':
            var = spotpy.parameter.Uniform(símismo.nombre, low=0, high=1)

        elif tipo_dist == 'Weibull':
            raise NotImplementedError
            var = spotpy.parameter.Weibull(símismo.nombre)

        else:
            raise ValueError(
                'La distribución "{}" existe en la base de datos de Tiko\'n para distribuciones SpotPy,'
                'pero no está configurada en la clase VarSpotPy.'.format(tipo_dist))

        # Hacer transformaciones necesarias
        símismo.transf = transf
        if transf is not None and transf['tipo'] not in ['Exp', 'LogitInv']:
            raise ValueError(transf['tipo'])

        símismo.mult = paráms['escl']
        símismo.suma = paráms['ubic']
        if inv:
            símismo.mult *= -1

        símismo.var = var

        símismo.tipo_dist = tipo_dist

    def dibujar(símismo, ejes=None):
        if ejes is None:
            fig, ejes = dib.subplots(1, 2)

        n = 10000
        puntos = símismo.var(size=n)

        # Transformaciones necesarias
        puntos = símismo._transf_vals(puntos)

        # Crear el histograma
        y, delim = np.histogram(puntos, density=True, bins=n // 100)
        x = 0.5 * (delim[1:] + delim[:-1])

        # Dibujar el histograma
        ejes[0].plot(x, y, 'b-', lw=2, alpha=0.6)
        ejes[0].set_title('Distribución')

        # Dibujar la traza sí misma
        ejes[1].plot(símismo.traza)
        ejes[1].set_title('Traza')

    @classmethod
    def de_densidad(cls, dens, líms_dens, líms, cont, nombre=None):
        # Convertir None a infinidad en los límites de densidad y teoréticos.
        mín = líms[0] if líms[0] is not None else -np.inf
        máx = líms[1] if líms[1] is not None else np.inf

        if líms_dens[0] < mín or líms_dens[1] > máx:
            raise ValueError(
                'Los límites de densidad ({}, {}) están afuera del rango teorético ({}, {}).'
                    .format(*líms_dens, mín, máx)
            )

        # Primero, arreglar unos casos especiales que nos podrían causar problemas después...

        # Si tenemos una densidad de 100% en el rango especificado...
        if dens == 1:
            # Generar una distribución uniforme en este rango.
            return cls(nombre, 'Uniforme', paráms={'ubic': líms_dens[0], 'escl': líms_dens[1] - líms_dens[0]})

        # No se puede tener límites de densidad iguales con densidad < 1, por supuesto.
        if líms_dens[0] == líms_dens[1]:
            raise ValueError('No se puede tener una densidad < 1 en un rango [a, b] si a = b.')

        # Si los rangos de la densidad corresponden con los rangos teoréticos, pero con densidad < 1...
        if líms_dens[0] == mín and líms_dens[1] == máx:
            raise ValueError('No se puede tener una densidad < 1 en un rango igual al rango teorético.')

        # Inicializar el diccionario de parámetros.
        paráms = {'escl': 1, 'ubic': 0}

        # Invertir distribuciones entre (-inf, R]
        if mín == -np.inf and máx != np.inf:
            mín = -máx
            máx = np.inf
            paráms['escl'] = -1

        # Ahora, crear la distribución apriopiada.
        if mín == -np.inf:
            # Ya convertimos distribuciones en (-inf, R] a [-R, inf), así que no es posible tener máx != inf.

            # El caso (-inf, inf). Muy facil.
            mu = np.mean(líms_dens)
            sigma = mu / estad.norm.ppf((1 - dens) / 2 + dens)

            tipo_dist = 'Normal'
            paráms = {'ubic': mu, 'escl': sigma}
            transf = None

        else:

            # Primero, normalizar el límite inferior.
            paráms['ubic'] += mín
            líms_dens = np.subtract(líms_dens, mín)
            máx -= mín

            if máx == np.inf:
                # El caso [R, inf)
                if líms_dens[0] == 0:
                    # Si el límite inferior del rango de densidad es igual al límite teorético, solamente tenemos
                    # que asegurarnos que ``dens`` densidad quede abajo del límite inferior transformado.

                    lím_norm_sup = np.log(líms_dens[1])  # El límite superior de densidad en la distribución normal

                    sigma = 1  # Tomar un sigma de 1, por simplicidad. De verdad no importa mucho.
                    mu = lím_norm_sup - estad.norm(0, 1).ppf(dens)  # Mu en función de sigma y la densidad

                else:
                    # Sino, tenemos que asegurarnos que la densidad caiga entre los dos límites transformados.
                    log_rango = np.log(líms_dens)

                    mu = np.mean(log_rango)  # Mu es el promedio entre ambos límites de densidad

                    # Sigma se calcular analíticamente
                    sigma = ((log_rango[1] - log_rango[0]) / 2) / estad.norm.ppf((1 - dens) / 2 + dens)

                # Especificar la distribución Normal con transformación exponencial
                tipo_dist = 'Normal'

                # Pasar escala y ubicación a la transformación...
                transf = {'tipo': 'Exp', 'mult': sigma, 'suma': mu}

            else:
                # El caso [R, R]

                # Normalizar la distribución
                paráms['escl'] *= máx
                rango = np.divide(líms_dens, máx)

                if rango[0] == 0:
                    # Si el límite inferior del rango de densidad es igual al límite teorético, solamente tenemos
                    # que asegurarnos que ``dens`` densidad quede abajo del límite superior transformado.
                    lím_norm_sup = _logit(rango[1])

                    sigma = 1  # Tomar un sigma de 1, por simplicidad. De verdad no importa mucho.
                    mu = lím_norm_sup - estad.norm(0, sigma).ppf(dens)  # Mu en función de sigma y la densidad

                elif rango[1] == 1:
                    # Si el límite superior del rango de densidad es igual al límite teorético, solamente tenemos
                    # que asegurarnos que la densidad quede arriba del límite inferior transformado.
                    lím_norm_inf = _logit(rango[0])

                    sigma = 1  # Tomar un sigma de 1, por simplicidad. De verdad no importa mucho.
                    mu = lím_norm_inf - estad.norm(0, 1).ppf(1 - dens)  # Mu en función de sigma y la densidad

                else:
                    # Sino, tenemos que asegurarnos que la densidad caiga entre los dos límites transformados.
                    lgt_rango = np.log(np.divide(rango, np.subtract(1, rango)))

                    mu = np.mean(lgt_rango)  # Mu es el promedio entre ambos límites de densidad

                    # Sigma se calcular analíticamente
                    sigma = ((lgt_rango[1] - lgt_rango[0]) / 2) / estad.norm.ppf((1 - dens) / 2 + dens)

                # Especificar la distribución Normal con transformación Logit Inverso
                tipo_dist = 'Normal'

                # Pasar escala y ubicación a la transformación...
                transf = {'tipo': 'LogitInv', 'suma': mu, 'mult': sigma}

        return cls(nombre=nombre, tipo_dist=tipo_dist, paráms=paráms, transf=transf)

    def _transf_vals(símismo, vals):

        if símismo.transf is None:
            return vals * símismo.mult + símismo.suma
        else:
            mult = símismo.transf['mult']
            suma = símismo.transf['suma']
            tipo = símismo.transf['tipo']
            if tipo == 'Exp':
                vals_transf = np.exp(vals * mult + suma)
            elif tipo == 'LogitInv':
                vals_transf = _inv_logit(vals * mult + suma)
            else:
                raise ValueError(tipo)

            return vals_transf * símismo.mult + símismo.suma

    @classmethod
    def _ajust_dist(cls, datos, líms, cont, lista_dist, nombre=None):

        mín = líms[0] if líms[0] is not None else -np.inf
        máx = líms[1] if líms[1] is not None else np.inf

        transf = {'mult': 1, 'suma': 0}
        if mín == -np.inf and máx != np.inf:
            mín = -máx
            máx = np.inf
            transf['mult'] = -1

        if mín == -np.inf:
            if máx == np.inf:
                ajustado = VarSciPy.aprox_dist(datos=datos, líms=(-np.inf, np.inf), cont=cont, lista_dist=lista_dist)
                tipo_dist = ajustado['nombre']
                paráms = ajustado['prms']  # Sacar el los parámetros de la distribución

                transf = None  # Sin transformación especial en este caso

            else:
                raise ValueError('No debería ser posible llegar hasta este error.')
        else:
            # Normalizar el límite inferior.
            transf['suma'] += mín
            máx -= mín
            datos = np.subtract(datos, mín)  # No borrar datos originales

            # Evitar log(0) y logit(0)
            if np.min(datos) == 0:
                transf['suma'] -= 1e-5
                máx += 1e-5
                datos = np.add(datos, 1e-5)

            if máx == np.inf:

                log_datos = np.log(datos)
                ajustado = VarSciPy.aprox_dist(datos=log_datos, líms=(-np.inf, np.inf),
                                               cont=cont, lista_dist=lista_dist)
                tipo_dist = ajustado['nombre']
                transf['tipo'] = 'Exp'
                paráms = ajustado['prms']

            else:
                transf['mult'] *= máx
                datos = np.divide(datos, máx)  # No borrar datos originales

                # Evitar logit(1)
                if np.max(datos) == 1:
                    transf['mult'] /= (1 - 1e-5)
                    datos = np.multiply(datos, 1 - 1e-5)

                lgt_datos = _logit(datos)

                ajustado = VarSciPy.aprox_dist(datos=lgt_datos, líms=(-np.inf, np.inf), cont=cont,
                                               lista_dist=lista_dist)
                tipo_dist = ajustado['nombre']
                transf['tipo'] = 'LogitInv'
                paráms = ajustado['prms']

        return {'dist': cls(nombre=nombre, tipo_dist=tipo_dist, paráms=paráms, transf=transf), 'p': ajustado['p']}
