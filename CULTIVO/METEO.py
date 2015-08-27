from COSO import Coso

class Clima(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada clima
        simismo.dic_base = dict(INSI="", LAT=(), LONG=(), ELEV=(), TAV=())
        super().__init__(*args, **kwargs)  # Esta variable se initializa como
        simismo.ext = "vrd"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)

class Meteo(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para datos meteorológicos
        simismo.dic_base = dict()
        super().__init__(*args, **kwargs)  # Esta variable se initializa como
        simismo.ext = "vrd"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)