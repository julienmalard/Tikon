from COSO import Coso
from PARCELA import Parcela


class Paisaje(Coso):
    def __init__(self, *args, **kwargs):
        self.dic_base = {"Parcelas": [], "Cultivos": [], "Fechas_siembra": [], "Suelos": []}
        super().__init__(*args, **kwargs)
        self.ext = "pais"  # La extensión para este tipo de documento. (Para guadar y cargar datos.)
