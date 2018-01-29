import re

dic_trads = {'Latino': {'núms': ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'),
                        'sep_dec': '.'},
             'हिंदी': {'núms': ('०', '१', '२', '३', '४', '५', '६', '७', '८', '९'),
                       'sep_dec': '.'},
             'ਪੰਜਾਬੀ': {'núms': ('੦', '੧', '੨', '੩', '੪', '੫', '੬', '੭', '੮', '੯'),
                        'sep_dec': '.'},
             'ગુજરાતી': {'núms': ('૦', '૧', '૨', '૩', '૪', '૫', '૬', '૭', '૮', '૯'),
                         'sep_dec': '.'},
             'മലയാളം': {'núms': ('൦', '൧', '൨', '൩', '൪', '൫', '൬', '൭', '൮', '൯'),
                        'sep_dec': '.'},
             'தமிழ்': {'núms': ('൦', '௧', '௨', '௩', '௪', '௫', '௬', '௭', '௮', '௯'),
                       'sep_dec': '.',
                       'bases': [(10, '௰'), (100, '௱'), (1000, '௲')]},
             'اردو': {'núms': ('٠', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'),
                      'sep_dec': '.'},
             'العربية': {'núms': ('٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩',),
                         'sep_dec': '.'},
             'فارسی': {'núms': ('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'),
                       'sep_dec': '.'},
             'ଓରିୟା': {'núms': ('୦', '୧', '୨', '୩', '୪', '୫', '୬', '୭', '୮', '୯'),
                       'sep_dec': '.'},
             'ಕನ್ನಡ': {'núms': ('೦', '೧', '೨', '೩', '೪', '೫', '೬', '೭', '೮', '೯'),
                       'sep_dec': '.'},
             'తెలుగు': {'núms': ('౦', '౧', '౨', '౩', '౪', '౫', '౬', '౭', '౮', '౯'),
                        'sep_dec': '.'},
             '汉语': {'núms': ('〇', '一', '二', '三', '四', '五', '六', '七', '八', '九'),
                    'bases': [(10, "十"), (100, "百"), (1000, "千"), (10000, "万")],
                    'sep_dec': '.'},
             '日本語': {'núms': ('〇', '一', '二', '三', '四', '五', '六', '七', '八', '九'),
                     'bases': [(10, "十"), (100, "百"), (1000, "千"), (10000, "万")],
                     'sep_dec': '.'},
             }


def trad_núm(núm, lengua_final, bases=True):
    """
    Esta función traduce un número.

    :param núm: El número para traducir, en formato de número o de texto.
    :type núm: float | int | str

    :param lengua_final: La lengua a la cual traducir.
    :type lengua_final: str

    :param bases: Si hay que devolver el número en formato de bases o no. Solamente aplica a algunas lenguas, tal como
    el Chino, el Japonés y el Tamil. Por ejemplo, `123` se traducirá a `百二十三` (Chino) o `௱௨௰௩` (Tamil) con
    ``bases=True`` y a `一二三` o `௧௨௩` con ``bases=False``.

    :return: El número traducido.
    :rtype: str
    """

    # Convertir el número a un valor numérico en Python, si necesario
    if isinstance(núm, str):
        val = tx_a_núm(texto=núm)
    else:
        val = núm

    # Convertir el valor numérico a la lengua deseada
    núm_trad = núm_a_tx(núm=val, lengua=lengua_final, bases=bases)

    return núm_trad


def tx_a_núm(texto):
    """
    Esta función toma texto de un número en cualquier idioma y lo cambia a un número Python.

    :param: El texto a convertir.
    :type texto: str

    :return: El número de Python correspondiendo
    :rtype: float

    """

    for lengua, d_l in dic_trads.items():
        # Intentar cada lengua disponible.

        sep_dec = d_l['sep_dec']  # El separador de decimales
        l_núms = list(d_l['núms'])  # Los números

        # Ver si hay posibilidad de un sistema de bases
        try:
            bases = d_l['bases']
        except KeyError:
            bases = None

        try:
            # Intentar traducir literalmente, número por número
            núm = _trad_texto(texto=texto, núms=l_núms, sep_dec=sep_dec)

            # ¿Funcionó? ¡Perfecto!
            return núm

        except ValueError:
            pass  # ¿No funcionó? Qué pena. Ahora tenemos que trabajar.

        if bases is not None:
            # Intentar ver si puede ser un sistema de bases (unidades).

            l_bases = [b[1] for b in bases]

            # Ver si hay de separar decimales
            try:
                entero, dec = texto.split(sep_dec)
            except ValueError:
                entero = texto
                dec = None

            error = False
            val_entero = 0
            v = última_base = None
            for j, i in enumerate(entero):
                if i in l_núms:
                    v = _conv_tx_cifra(i, lengua)
                    if j == len(entero) -1:
                        val_entero += v
                elif i in l_bases:

                    base = bases[l_bases.index(i)][0]
                    if última_base is None or base < última_base:
                        if v is None:
                            v = 1
                        v *= base
                        val_entero += v
                    else:
                        if v is None:
                            v = 0
                        val_entero += v
                        val_entero *= base
                    v = None
                    última_base = base
                else:
                    error = True
                    continue

            if error:
                continue

            # Calcular el número traducido
            if dec is not None:
                # Si había decima, convertir el texto decimal
                val_dec = _trad_texto(texto=dec, núms=l_núms, sep_dec=sep_dec, txt=True)

                # Calcular el número
                núm = float(str(val_entero) + sep_dec + val_dec)

            else:
                # ... si no había decimal, no hay nada más que hacer
                núm = val_entero

            return núm  # Devolver el número

    # Si ninguna de las lenguas funcionó, hubo error.
    raise ValueError('No se pudo decifrar el número %s' % texto)


def _trad_texto(texto, núms, sep_dec, txt=False):
    """
    Esta función traduce un texto a un valor numérico o de texto (formato latino).

    :param texto: El texto para traducir.
    :type texto: str
    :param núms: La lista, en orden ascendente, de los carácteres que corresponden a los números 0, 1, 2, ... 9.
    :type núms: list[str]
    :param sep_dec: El separador de decimales
    :type sep_dec: str
    :param txt: Si hay que devolver en formato de texto
    :type txt: bool
    :return: El número convertido.
    :rtype: float | txt
    """

    if all([x in núms + [sep_dec, ] for x in texto]):
        # Si todos los carácteres en el texto están reconocidos...

        # Cambiar el separador de decimal a un punto.
        texto = texto.replace(sep_dec, '.')

        for n, d in enumerate(núms):
            # Reemplazar todos los números también.
            texto = texto.replace(d, str(n))

        # Devolver el resultado, o en texto, o en formato numeral.
        if txt:
            return texto
        else:
            return float(texto)

    else:
        # Si no se reconocieron todos los carácteres, no podemos hacer nada más.
        raise ValueError('Texto "{}" no reconocido.'.format(texto))


def _conv_cifra(n, lengua):
    return dic_trads[lengua]['núms'][n]


def _conv_tx_cifra(tx, lengua):
    return dic_trads[lengua]['núms'].index(tx)


def núm_a_tx(núm, lengua, bases=True):
    """
    Esta función convierte un número Python en texto traducido.

    :param núm: El numero para convertir a texto.
    :type núm: float | int

    :param lengua: La lengua del texto deseado.
    :type lengua: str

    :param bases: Si hay que convertir a formato con bases (solamente aplica a algunas lenguas).
    :type bases: bool

    :return: El número en formato de texto traducido.
    :rtype: str

    """

    # Los números y separador de decimal de la lengua escogida.
    núms = dic_trads[lengua]['núms']
    sep_dec = dic_trads[lengua]['sep_dec']

    # La lista de bases para la lengua escogida
    l_bases = None
    if bases:
        try:
            l_bases = dic_trads[lengua]['bases']  # type: list[tuple]
        except KeyError:
            bases = False

    # Convertir el número a texto
    tx_número = str(núm)

    # Dividir las partes enteras y de decimales
    entero, dec = tx_número.split('.')

    # Si queremos utilizar bases...
    if bases:

        # Si la lengua tiene opciones de bases...
        if l_bases is not None:

            trad_ent = gen_bases(int(entero), bases=l_bases, lengua=lengua)

        else:
            trad_ent = ''.join(núms[int(n)] for n in entero)

    else:
        trad_ent = ''.join(núms[int(n)] for n in entero)
    trad_dec = ''.join(núms[int(n)] for n in dec)

    trad_núm = '{ent}{sep_dec}{dec}'.format(ent=trad_ent, dec=trad_dec, sep_dec=sep_dec)

    return trad_núm


def gen_bases(núm, bases, lengua, t=''):
    """

    :param núm:
    :type núm: int
    :param bases:
    :type bases: list
    :param t: Para la iteración
    :type t: str
    :return:
    :rtype: str
    """

    # Ordenar las bases
    bases.sort()

    # Para cada base, en orden de magnitud disminuyendo
    for mag, símb in reversed(bases):

        # Calcular el dividendo del número dividido por la magnitud
        dividendo = núm // mag

        if dividendo == 0:
            # Si el número era más pequeño, seguir a la próxima base posible
            continue

        else:
            # Sino...

            # Si el dividendo queda más alto que la base más pequeña, hay que seguir.
            if dividendo >= bases[0][0]:
                t += gen_bases(núm=dividendo, bases=bases, t=t, lengua=lengua)
                t += bases[-1][1]
                núm %= mag
            else:

                if dividendo > 1:
                    t += _conv_cifra(dividendo, lengua=lengua) + símb
                else:
                    t += símb
                núm %= mag
                if núm < bases[0][0]:
                    t += _conv_cifra(núm, lengua=lengua)

    return t


def leer_bases(texto, núms, sep_dec, bases, n=0):
    """

    :param texto:
    :type texto:
    :param núms:
    :type núms:
    :param sep_dec:
    :type sep_dec:
    :param bases:
    :type bases:
    :param n:
    :type n:
    :return:
    :rtype:
    """
    res = re.match(r'[%s]+' % ''.join([b[1] for b in bases]), texto[::-1])

    if res:
        base_fin = res.group(0)
        val_base_fin = [x[0] for x in bases if x[1] == base_fin][0]
        texto = texto[:-res.span()[1]]
    else:
        val_base_fin = 1

    res = re.match(r'[%s]+' % ''.join(núms), texto[::-1])
    if res:
        núm_fin = res.group(0)
        val_núm_fin = tx_a_núm(texto=núm_fin)

        texto = texto[:-res.span()[1]]
    else:
        val_núm_fin = 1

    n += val_núm_fin * val_base_fin

    if len(texto):
        n += leer_bases(texto=texto, núms=núms, sep_dec=sep_dec, bases=bases, n=n)
    else:
        return n


# Prueba
if __name__ == '__main__':

    for leng in dic_trads:
        número = 123456.7809
        tx = núm_a_tx(número, leng)
        latín = tx_a_núm(tx)
        print(leng, ':', número, tx, latín)
