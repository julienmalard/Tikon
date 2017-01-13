import re


trads_núm = {'हिंदी': {'núms': ('०', '१', '२', '३', '४', '५', '६', '७', '८', '९'),
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
                    'sep_dec': '.'},
             '日本語': {'núms': ('〇', '一', '二', '三', '四', '五', '六', '七', '八', '九'),
                     'sep_dec': '.'},
             }


def núm_a_tx(núm, lengua, bases=False):
    """

    :param núm:
    :type núm: float | int

    :param lengua:
    :type lengua: str

    :param bases:
    :type bases: bool

    :return:
    :rtype: str

    """

    núms = trads_núm[lengua]['núms']
    sep_dec = trads_núm[lengua]['sep_dec']
    try:
        l_bases = trads_núm[lengua]['bases']
    except KeyError:
        l_bases = None

    tx_número = str(núm)

    entero, dec = tx_número.split('.')

    if bases:

        if l_bases is not None:
            trad_ent = ''
            con_bases = gen_bases(entero, bases=l_bases)
            for i, n in enumerate(con_bases):
                try:
                    trad_ent += núms[int(n)]
                except KeyError:
                    trad_ent += n

        else:
            raise ValueError('No hay sistema de bases definido para la lengua %s.' % lengua)

    else:
        trad_ent = ''.join(núms[int(n)] for n in entero)
    trad_dec = ''.join(núms[int(n)] for n in dec)

    trad_núm = '{ent}{sep_dec}{dec}'.format(ent=trad_ent, dec=trad_dec, sep_dec=sep_dec)

    return trad_núm


def tx_a_núm(texto):
    """
    Esta función toma texto de un número en cualquier idioma y lo cambia a un número Python.

    :param: El texto a convertir.
    :type texto: str

    :return: El número de Python correspondiendo
    :rtype: float

    """

    for lengua, d_l in trads_núm.items():

        sep_dec = d_l['sep_dec']
        l_núms = d_l['núms']
        try:
            bases = d_l['bases']
        except KeyError:
            bases = None

        try:
            núm = trad_texto(texto=texto, núms=l_núms, sep_dec=sep_dec)
            return núm

        except ValueError:
            if bases is not None:
                try:
                    try:
                        entero, dec = texto.split(sep_dec)
                    except ValueError:
                        entero = texto

                    regex_núm = r'[{}]'.format(''.join([n for n in l_núms]))
                    regex_unid = r'[{}]'.format(''.join([b[1] for b in bases]))

                    regex = r'((?P<núm>{})?(?P<unid>{}|$))'.format(regex_núm, regex_unid)

                    m = re.finditer(regex, entero)
                    if m is None:
                        continue
                    else:
                        grupos = list(m)[:-1]

                        núms = [trad_texto(g.group('núm'), núms=l_núms, sep_dec=sep_dec) for g in grupos]
                        unids = [trad_texto(g.group('unid'), núms=[b[1] for b in bases], sep_dec=sep_dec)
                                 for g in grupos]

                        vals = [núms[i] * u for i, u in enumerate(unids)]

                        val_entero = vals[0]
                        for i, v in enumerate(vals[1:]):
                            if unids[i+1] > unids[i]:
                                val_entero *= v
                            else:
                                val_entero += v

                        tx_dec = trad_texto(texto=dec, núms=l_núms, sep_dec=sep_dec, txt=True)

                        núm = str(val_entero) + sep_dec + tx_dec

                    return núm

                except (KeyError, ValueError):
                    pass

    raise ValueError('No se pudo decifrar el número %s' % texto)


def trad_texto(texto, núms, sep_dec, txt=False):
    if all([x in núms + (sep_dec,) for x in texto]):
        texto = texto.replace(sep_dec, '.')

        for n, d in enumerate(núms):
            texto = texto.replace(d, str(n))

        if txt:
            return texto
        else:
            return float(texto)

    else:
        raise ValueError


def gen_bases(núm, bases, t=''):
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

    bases.sort()

    for símb, mag in reversed(bases):

        dividendo = núm // mag
        if dividendo == 0:
            continue
        else:
            if dividendo >= bases[-1][0]:
                t += gen_bases(núm=dividendo, bases=bases, t=t)
            else:
                resto = núm % mag
                if resto > 1:
                    t += str(resto) + símb
                else:
                    t += símb

    return t


def leer_bases(texto, núms, sep_dec, bases, n=0):

    '௨௲௩௱௰'

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

    tx_a_núm('௨௲௩௰')
    for leng in trads_núm:
        número = 123456.7809
        tx = núm_a_tx(número, leng)
        latín = tx_a_núm(tx)
        print(leng, ':', número, tx, latín)
