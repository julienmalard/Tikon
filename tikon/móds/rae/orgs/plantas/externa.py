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


class Alfalfa(CultivoExterno):
    cultivo = 'alfalfa'


class Tomate(CultivoExterno):
    cultivo = 'tomate'


class PastoBahía(CultivoExterno):
    cultivo = 'pasto bahía'


class GramaComún(CultivoExterno):
    cultivo = 'grama común'


class Frijol(CultivoExterno):
    cultivo = 'frijol'


class Brachiaria(CultivoExterno):
    cultivo = 'brachiaria'


class Repollo(CultivoExterno):
    cultivo = 'repollo'


class Canola(CultivoExterno):
    cultivo = 'canola'


class JudíaVerde(CultivoExterno):
    cultivo = 'judía verde'


class Pimiento(CultivoExterno):
    cultivo = 'pimiento'


class Cártamo(CultivoExterno):
    cultivo = 'cártamo'


class MaízDulce(CultivoExterno):
    cultivo = 'maíz dulce'


class Taro(CultivoExterno):
    cultivo = 'taro'


class FrijolTerciopelo(CultivoExterno):
    cultivo = 'frijol terciopelo'


class Cebada(CultivoExterno):
    cultivo = 'cebada'


class Mandioca(CultivoExterno):
    cultivo = 'mandioca'


class Garbanzo(CultivoExterno):
    cultivo = 'garbanzo'


class Algodón(CultivoExterno):
    cultivo = 'algodón'


class FrijolDeCarita(CultivoExterno):
    cultivo = 'frijol de carita'


class Faba(CultivoExterno):
    cultivo = 'haba'


class Maní(CultivoExterno):
    cultivo = 'maní'


class Maíz(CultivoExterno):
    cultivo = 'maíz'


class Mungo(CultivoExterno):
    cultivo = 'mungo'


class Guandú(CultivoExterno):
    cultivo = 'guandú'


class Papa(CultivoExterno):
    cultivo = 'papa'


class Raps(CultivoExterno):
    cultivo = 'raps'


class Arroz(CultivoExterno):
    cultivo = 'arroz'


class Sorgo(CultivoExterno):
    cultivo = 'sorgo'


class Soya(CultivoExterno):
    cultivo = 'soya'


class RemolachaAzucarera(CultivoExterno):
    cultivo = 'remolacha azucarera'


class Caña(CultivoExterno):
    cultivo = 'caña'


class Girasol(CultivoExterno):
    cultivo = 'girasol'


class Batata(CultivoExterno):
    cultivo = 'batata'


class Tabaco(CultivoExterno):
    cultivo = 'tabaco'


class Trigo(CultivoExterno):
    cultivo = 'trigo'
