from tikon.móds.rae.orgs.ecs.utils import ECS_CREC, ECS_DEPR, ECS_MRTE, ECS_EDAD, ECS_TRANS, ECS_REPR, ECS_ESTOC, \
    ECS_MOV
from tikon.móds.rae.orgs.plantas import Planta


class CultivoExterno(Planta):

    def __init__(símismo, nombre=None, variedad=None):
        nombre = nombre or símismo.cultivo
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

    @property
    def cultivo(símismo):
        raise NotImplementedError


class Tomate(CultivoExterno):
    cultivo = 'tomate'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Cebada(CultivoExterno):
    cultivo = 'cebada'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Mandioca(CultivoExterno):
    cultivo = 'mandioca'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Garbanzo(CultivoExterno):
    cultivo = 'garbanzo'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Algodón(CultivoExterno):
    cultivo = 'algodón'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class FrijolDeCarita(CultivoExterno):
    cultivo = 'frijol de carita'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Faba(CultivoExterno):
    cultivo = 'haba'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Maní(CultivoExterno):
    cultivo = 'maní'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Maíz(CultivoExterno):
    cultivo = 'maíz'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Mungo(CultivoExterno):
    cultivo = 'mungo'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Guandú(CultivoExterno):
    cultivo = 'guandú'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Papa(CultivoExterno):
    cultivo = 'papa'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Raps(CultivoExterno):
    cultivo = 'raps'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Arroz(CultivoExterno):
    cultivo = 'arroz'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Sorgo(CultivoExterno):
    cultivo = 'sorgo'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Soya(CultivoExterno):
    cultivo = 'soya'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class RemolachaAzucarera(CultivoExterno):
    cultivo = 'remolacha azucarera'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Caña(CultivoExterno):
    cultivo = 'caña'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Girasol(CultivoExterno):
    cultivo = 'girasol'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Batata(CultivoExterno):
    cultivo = 'batata'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Tabaco(CultivoExterno):
    cultivo = 'tabaco'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)


class Trigo(CultivoExterno):
    cultivo = 'trigo'

    def __init__(símismo, variedad=None):
        super().__init__(variedad=variedad)
