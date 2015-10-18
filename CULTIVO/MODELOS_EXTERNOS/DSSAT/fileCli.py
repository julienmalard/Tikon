import os

from CULTIVO.MODELOS_EXTERNOS.DSSAT.DSSAT import DocDssat


# Objeto para representar documentos de datos de clima mensuales de DSSAT
class FileCli(DocDssat):
    def __init__(simismo, dic="", *args, **kwargs):
        super().__init__(*args, **kwargs)  # Esta variable se initializa como DocDssat
        simismo.dic = dic

        if len(simismo.dic) == 0:
            simismo.dic = {"SITE": [], "INSI": [], "LAT": [], "LONG": [], "ELEV": [], "TAV": [], "AMP": [], "SPRAY": [],
                           "TMXY": [], "TMNY": [], "RAIY": [], "START": [], "DURN": [], "ANGA": [], "ANGB": [],
                           "REFHT": [], "WNDHT": [], "SOURCE": [], "GSST": [], "GSDU": [], "MONTH": [], "SAMN": [],
                           "XAMN": [], "NAMN": [], "RTOT": [], "RNUM": [], "SHMN": [], "AMTH": [], "BMTH": [],
                           "MTH": [], "SDMN": [], "SDSD": [], "SWMN": [], "SWSD": [], "XDMN": [], "XDSD": [],
                           "XWMN": [], "XWSD": [], "NASD": [], "ALPHA": [], "PDW": []}

        # Lista del tamaño (en carácteres) de cada variable
        simismo.prop_vars = {
            "SITE": 50, "INSI": 5, "LAT": 8, "LONG": 8, "ELEV": 5, "TAV": 5, "AMP": 5, "SPRAY": 5,
            "TMXY": 5, "TMNY": 5, "RAIY": 5, "START": 5, "DURN": 5, "ANGA": 5, "ANGB": 5,
            "REFHT": 5, "WNDHT": 5, "SOURCE": 20, "GSST": 5, "GSDU": 5, "MONTH": 5, "SAMN": 5, "XAMN": 5,
            "NAMN": 5, "RTOT": 5, "RNUM": 5, "SHMN": 5, "AMTH": 5, "BMTH": 5, "MTH": 5,
            "SDMN": 5, "SDSD": 5, "SWMN": 5, "SWSD": 5, "XDMN": 5, "XDSD": 5, "XWMN": 5,
            "XWSD": 5, "NASD": 5, "ALPHA": 5, "PDW": 5
        }

    def leer(simismo, cod_clima):

        # Vaciar el diccionario
        for i in simismo.dic:
            simismo.dic[i] = []

        encontrado = False

        for doc_clima in os.listdir(os.path.join(simismo.dir_DSSAT, 'Weather', 'Climate')):
            if doc_clima.upper().endswith(".CLI") and cod_clima.upper() in doc_clima.upper():
                with open(os.path.join(simismo.dir_DSSAT, 'Weather', 'Climate', doc_clima)) as d:
                    doc = d.readlines()
                    simismo.decodar(doc)
                encontrado = True

        # Si no lo encontramos
        if not encontrado:
            print("Error: El código de clima no se ubica en la base de datos 'Clima' de DSSAT.")
            return False

    # Esta función escribe los datos de clima para que los lea DSSAT
    def escribir(simismo):
        cod_clim = simismo.dic["INSI"] + "TKON"

        for i in simismo.dic:  # Llenar variables vacíos con -99 (el código de DSSAT para datos que faltan)
            if not len(simismo.dic[i]):
                simismo.dic[i] = ["-99"]

        with open("FILECli.txt", "r") as d:  # Abrir el esquema general para archivos FILES
            esquema = d.readlines()
        esquema.append("\n")  # Terminar con una línea vacía para marcar el fin del documento

        esquema = simismo.encodar(esquema)
        esquema = ''.join(esquema)  # Lo que tenemos que escribir

        # Salvar la carpeta FILECli en DSSAT46/Weather/Climate
        with open(os.path.join(simismo.dir_DSSAT, 'Weather', 'Clima', cod_clim, '.CLI'), "w") as d:
            d.write(''.join(esquema))

    # Esta funcción convierte datos de clima de un documento FILECli de DSSAT en diccionario Python.
    def decodar(simismo, doc):
        # Encuentra la ubicación del principio y del fin de cada sección
        for línea in doc:
            if "*" in línea and "CLIMATE" in línea:
                simismo.dic['SITE'] = línea[línea.index(':') + 1:].strip()
                continue

            if "@" in línea:
                variables = línea.replace('@', '').split()
                # Empezamos a leer los valores en la línea que sigue los nombres de los variables
                núm_lin = línea + 1

                # Mientras no llegamos a la próxima línea de nombres de variables o el fin de la sección
                while "@" not in doc[núm_lin] and doc[núm_lin] != '\n':
                    valores = doc[núm_lin].replace('\n', '')
                    for j, var in enumerate(variables):
                        if var in simismo.dic:
                            valor = valores[:simismo.prop_vars[var] + 1].strip()
                            simismo.dic[var].append(valor)
                            valores = valores[simismo.prop_vars[var] + 1:]
                    núm_lin += 1

    def encodar(simismo, doc_clima):
        for n, línea in enumerate(doc_clima):
            l = n
            texto = línea
            if '{' in texto:  # Si la línea tiene variables a llenar
                # Leer el primer variable de la línea (para calcular el número de niveles de suelo más adelante)
                var = texto[texto.index("{") + 2:texto.index("]")]
                for k, a in enumerate(simismo.dic[var]):  # Para cada nivel del perfil del suelo
                    l += 1
                    nueva_línea = texto.replace('[', '').replace("]", "[" + str(k) + "]")
                    nueva_línea = nueva_línea.format(**simismo.dic)
                    doc_clima.insert(l, nueva_línea)
                doc_clima.remove(texto)
        return doc_clima
