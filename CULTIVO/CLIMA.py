from COSO import Coso


# Esta clase representa el clima diario.
class Diario(Coso):
    def __init__(simismo, *args, **kwargs):
        # El diccionario de los datos para cada suelo
        simismo.dic_base = dict(Lat=(), Long=(), Elev=(), Temp_prom=(), Alt_med_temp=(), Alt_med_viento=(),
                                Amp_temp_mens=(), Fecha=[], Rad_sol=[], Temp_máx=[], Temp_mín=[], Precip=[],
                                Temp_conden=[], Viento=[], Rad_foto=[])

        super().__init__(*args, **kwargs)  # Esta variable se initializa como Coso
        simismo.ext = "cli"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
