from ..etapa import Etapa, EspecificaciónEtapaPorNombre, EspecificaciónEtapas, EspecificaciónEtapaPorPrincipioNombre
from ..organismo import Organismo

HUEVO = "huevo"
JUVENIL = 'juvenil'
PUPA = "pupa"
ADULTO = "adulto"


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
            etapas.append(HUEVO)

        if njuvenil < 0:
            raise ValueError('El número de juveniles no puede ser inferior a 0.')

        for i in range(0, njuvenil):

            # Establecer el nombre de la etapa juvenil
            if njuvenil == 1:
                nombre_juv = JUVENIL
            else:
                nombre_juv = f'{JUVENIL} {i + 1}'

            # Agregar la etapa
            etapas.append(nombre_juv)

        if pupa:
            etapas.append(PUPA)

        if adulto:
            etapas.append(ADULTO)

        super().__init__(nombre=nombre, etapas=etapas)
        símismo.activar_ecs(tipo_ecs)

    def huevo(símismo, incluir_parasitadas=True) -> EspecificaciónEtapas:
        return EspecificaciónEtapaPorNombre(
            organismo=símismo,
            nombre_etapa=HUEVO,
            incluir_parasitadas=incluir_parasitadas
        )

    def juveniles(símismo, incluir_parasitadas=True) -> EspecificaciónEtapas:

        # Incluiremos todas las etapas empezando por JUVENIL
        return EspecificaciónEtapaPorPrincipioNombre(
            organismo=símismo,
            nombre_etapa=JUVENIL,
            incluir_parasitadas=incluir_parasitadas
        )

    def pupa(símismo, incluir_parasitadas=True) -> EspecificaciónEtapas:
        return EspecificaciónEtapaPorNombre(
            organismo=símismo,
            nombre_etapa=PUPA,
            incluir_parasitadas=incluir_parasitadas
        )

    def adulto(símismo, incluir_parasitadas=True) -> EspecificaciónEtapas:
        return EspecificaciónEtapaPorNombre(
            organismo=símismo,
            nombre_etapa=ADULTO,
            incluir_parasitadas=incluir_parasitadas
        )

    def resolver_etapas(símismo, etapas):
        if isinstance(etapas, (str, Etapa)):
            etapas = [etapas]

        if etapas is not None and JUVENIL in etapas:
            etapas.remove(JUVENIL)

            for etp in símismo.etapas:
                if etp.nombre.startswith(JUVENIL):
                    etapas.append(etp)

        return super().resolver_etapas(etapas)
