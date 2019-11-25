from ..organismo import Organismo, Etapa

JUVENIL = 'juvenil'


class Insecto(Organismo):
    """
    La clase
    pariente para cada tipo de insecto.
    """

    def __init__(símismo, nombre, huevo=False, njuvenil=0, pupa=False, adulto=True, tipo_ecs=None):

        if tipo_ecs is None:
            tipo_ecs = {}

        # Añadir las etapas
        etapas = []
        if huevo:
            etapas.append('huevo')

        if njuvenil < 0:
            raise ValueError('El número de juveniles no puede ser inferior a 0.')

        for i in range(0, njuvenil):

            # Establecer el nombre de la etapa juvenil
            if njuvenil == 1:
                nombre = JUVENIL
            else:
                nombre = f'{JUVENIL} {i + 1}'

            # Agregar la etapa
            etapas.append(nombre)

        if pupa:
            etapas.append('pupa')

        if adulto:
            etapas.append('adulto')

        super().__init__(nombre=nombre, etapas=etapas)
        símismo.activar_ecs(tipo_ecs)

    def resolver_etapas(símismo, etapas):
        if isinstance(etapas, (str, Etapa)):
            etapas = [etapas]

        if etapas is not None and JUVENIL in etapas:
            etapas.remove(JUVENIL)

            for etp in símismo._etapas:
                if etp.nombre.startswith(JUVENIL):
                    etapas.append(etp)

        return super().resolver_etapas(etapas)
