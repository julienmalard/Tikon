from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg


class Euclidiana(EcuaciónOrg):
    nombre = 'Euclidiana'

    def eval(símismo, paso, sim):
        # Devolvemos distancia cuadrada
        return símismo.obt_valor_control(sim, 'distancias') ** 2

    @classmethod
    def requísitos(cls, controles=False):
        if controles:
            return {'distancias'}
