

trads_núm = {'हिंदी': {'núms': ('०', '१', '२', '३', '४', '५', '६', '७', '८', '९'),
                       'sep_dec': '.'},
             'ਪੰਜਾਬੀ': {'núms': ('੦', '੧', '੨', '੩', '੪', '੫', '੬', '੭', '੮', '੯')},
             'ગુજરાતી': {'núms': ('૦', '૧', '૨', '૩', '૪', '૫', '૬', '૭', '૮', '૯'),
                         'sep_dec': '.'},
             'മലയാളം': {'núms': ('൦', '൧', '൨', '൩', '൪', '൫', '൬', '൭', '൮', '൯')},
             'தமிழ்': {'núms': ('൦', '௧', '௨', '௩', '௪', '௫', '௬', '௭', '௮', '௯')},
             'اردو': {'núms': ('.', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'),
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
             '汉语': {'núms': ('零', '一', '二', '三', '四', '五', '六', '七', '八', '九'),
                    'sep_dec': '.'}
             }


def núm_a_tx(número, lengua):
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

    :type texto: str
    """
    núm = texto
    for l in trads_núm.values():
        trads = l['núms']
        for n, d in enumerate(trads):
            if d in núm:
                núm.replace(d, str(n))
        try:
            núm = float(núm)
            return núm
        except ValueError:
            continue

    raise ValueError('No se pudo decifrar el número %s' % texto)


print(núm_a_tx(123456.7890, 'ગુજરાતી'))
print(núm_a_tx(123456.7890, '汉语'))
print(núm_a_tx(123456.7890, 'ଓରିୟା'))
print(núm_a_tx(123456.7890, 'اردو'))

print(tx_a_núm('१२३.४५६'))
print(tx_a_núm('一'))
