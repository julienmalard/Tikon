from tikon.rae.orgs.organismo import Organismo, Etapa

JUVENIL = 'juvenil'


class Insecto(Organismo):
    def __init__(símismo, nombre, huevo=False, njuvenil=0, pupa=False, adulto=True, tipo_ecuaciones=None):

        super().__init__(nombre=nombre)

        if tipo_ecuaciones is None:
            tipo_ecuaciones = {}

        # Añadir las etapas
        if huevo:
            símismo.añadir_etapa('huevo')

        if njuvenil < 0:
            raise ValueError('El número de juveniles no puede ser inferior a 0.')

        for i in range(0, njuvenil):

            # Establecer el nombre de la etapa juvenil
            if njuvenil == 1:
                nombre = JUVENIL
            else:
                nombre = f'{JUVENIL}_{i + 1}'

            # Agregar la etapa
            símismo.añadir_etapa(nombre)

        if pupa:
            símismo.añadir_etapa('pupa')

        if adulto:
            símismo.añadir_etapa('adulto')

        símismo.activar_ecs(tipo_ecuaciones)

    def resolver_etapas(símismo, etapas):
        if isinstance(etapas, (str, Etapa)):
            etapas = [etapas]

        if etapas is not None and JUVENIL in etapas:
            etapas.remove(JUVENIL)

            for etp in símismo._etapas:
                if etp.nombre.startswith(JUVENIL):
                    etapas.append(etp)

        return super().resolver_etapas(etapas)
