from tikon.móds.rae.orgs.ecs._plntll import EcuaciónOrg


class Euclidiana(EcuaciónOrg):
    nombre = 'Euclidiana'

    def eval(símismo, paso, sim):
        # Devolvemos distancia cuadrada
        return símismo.obt_val_control(sim, 'distancias') ** 2

    def requísitos(símismo, controles=False):
        if controles:
            return ['distancias']
