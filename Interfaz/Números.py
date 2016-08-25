

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
                       'unid': [(10, '௰'), (100, '௱'), (1000, '௲')]},
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


def núm_a_tx(número, lengua, dec=True):
    """

    :param número:
    :type número: float | int

    :param lengua:
    :type lengua: str

    :param dec:
    :type dec: bool

    :return:
    :rtype: str

    """

    núms = trads_núm[lengua]['núms']
    sep_dec = trads_núm[lengua]['sep_dec']
    tx_número = str(número)

    entero, dec = tx_número.split('.')

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

    for l in trads_núm.values():

        sep_dec = l['sep_dec']
        núms = l['núms']

        if all([x in núms + (sep_dec,) for x in texto]):
            texto = texto.replace(sep_dec, '.')

            for n, d in enumerate(núms):
                texto = texto.replace(d, str(n))

            texto = float(texto)

            return texto

    raise ValueError('No se pudo decifrar el número %s' % texto)


# Prueba
if __name__ == '__main__':
    for leng in trads_núm:
        núm = 123456.7809
        tx = núm_a_tx(núm, leng)
        latín = tx_a_núm(tx)
        print(leng, ':', núm, tx, latín)
