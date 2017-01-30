from tikon.Coso import Coso
from tikon.Matemáticas import Ecuaciones as Ec


# Esta clase representa los suelos de una parcela.
class Suelo(Coso):

    ext = '.suel'

    dic_ecs = Ec.ecs_suelo

    def __init__(símismo, nombre, proyecto=None):

        # Esta variable se initializa como Coso
        super().__init__(nombre=nombre, proyecto=proyecto)

        # Guardar las ecuaciones del suelo en la sección 'coefs' de la receta
        símismo.receta['coefs'] = Ec.gen_ec_inic(Ec.ecs_suelo)
        Textura_suelo = ""
        Color = ""


    def _sacar_líms_coefs_interno(símismo):
        """
        Ver la documentación de Coso.

        :rtype: list

        """

        return [símismo.dic_ecs[x]['límites'] for x in símismo.receta['coefs']]

    def _sacar_coefs_interno(símismo):
        """
        Ver la documentación de Coso.

        :rtype: list

        """

        return list(símismo.receta['coefs'].values())
