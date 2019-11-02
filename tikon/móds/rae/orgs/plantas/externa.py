from tikon.móds.rae.orgs.ecs.utils import ECS_CREC, ECS_DEPR, ECS_MRTE, ECS_EDAD, ECS_TRANS, ECS_REPR, ECS_ESTOC, \
    ECS_MOV
from tikon.móds.rae.orgs.plantas import Planta


class CultivoExterno(Planta):

    def __init__(símismo, nombre, variedad=None):
        base = {
            ECS_CREC: {'Modif': 'Ninguna', 'Ecuación': 'Nada'},
            ECS_DEPR: {'Ecuación': 'Nada'},
            ECS_MRTE: {'Ecuación': 'Nada'},
            ECS_EDAD: {'Ecuación': 'Nada'},
            ECS_TRANS: {'Prob': 'Nada', 'Mult': 'Nada'},
            ECS_REPR: {'Prob': 'Nada'},
            ECS_ESTOC: {'Dist': 'Nada'},
            ECS_MOV: {'Distancia': 'Nada', 'Atracción': 'Nada'}
        }
        tipo_ecs = {parte: base for parte in ['raíz', 'palo', 'sabia', 'hoja', 'flor', 'fruta', 'semilla']}
        super().__init__(
            nombre, raíz=True, palo=True, sabia=True, hoja=True, flor=True, fruta=True, semilla=True,
            variedad=variedad, tipo_ecs=tipo_ecs
        )


class Tomate(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('tomate', variedad=variedad)


class Cebada(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('cebada', variedad=variedad)


class Mandioca(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('mandioca', variedad=variedad)


class Garbanzo(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('garbanzo', variedad=variedad)


class Algodón(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('algodón', variedad=variedad)


class FrijolDeCarita(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('frijol de carita', variedad=variedad)


class Faba(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('faba', variedad=variedad)


class Maní(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('maní', variedad=variedad)


class Maíz(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('maíz', variedad=variedad)


class Tomate(CultivoExterno):  # mungbean
    def __init__(símismo, variedad=None):
        super().__init__('tomate', variedad=variedad)


class Tomate(CultivoExterno):  # pigeonpea
    def __init__(símismo, variedad=None):
        super().__init__('tomate', variedad=variedad)


class Papa(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('papa', variedad=variedad)


class Tomate(CultivoExterno):  # rapeseed
    def __init__(símismo, variedad=None):
        super().__init__('tomate', variedad=variedad)


class Arroz(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('arroz', variedad=variedad)


class Sorgo(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('sorgo', variedad=variedad)


class Soya(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('soya', variedad=variedad)


class Remolacha(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('remolacha', variedad=variedad)


class Caña(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('caña', variedad=variedad)


class Girasol(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('girasol', variedad=variedad)


class PapaDulce(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('papa dulce', variedad=variedad)


class Tobaco(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('tobaco', variedad=variedad)


class Trigo(CultivoExterno):
    def __init__(símismo, variedad=None):
        super().__init__('trigo', variedad=variedad)
