from tikon.RAE.orgs.organismo import Organismo, Etapa

JUVENIL = 'juvenil'


class Insecto(Organismo):
    def __init__(símismo, nombre, huevo=False, njuvenil=0, pupa=False, adulto=True, tipo_ecuaciones=None):

        super().__init__(nombre=nombre)

        if tipo_ecuaciones is None:
            tipo_ecuaciones = {}

        # Añadir las etapas
        pos = 0
        if huevo:
            símismo.añadir_etapa('huevo', pos=pos)
            pos += 1

        if njuvenil < 0:
            raise ValueError('El número de juveniles no puede ser inferior a 0.')

        for i in range(0, njuvenil):

            # Establecer el nombre de la etapa juvenil
            if njuvenil == 1:
                nombre = JUVENIL
            else:
                nombre = f'{JUVENIL}_{i+1}'

            # Agregar la etapa
            símismo.añadir_etapa(nombre, pos=pos)
            pos += 1

        if pupa:
            símismo.añadir_etapa('pupa', pos=pos)
            pos += 1

        if adulto:
            símismo.añadir_etapa('adulto', pos=pos)

        símismo.activar_ecs(tipo_ecuaciones)

    def resolver_etapas(símismo, etapas):
        if isinstance(etapas, (str, Etapa)):
            etapas = [etapas]

        if JUVENIL in etapas:
            etapas.remove(JUVENIL)

        for etp in símismo.etapas:
            if str(etp).startswith(JUVENIL):
                etapas.append(etp)

        return super().resolver_etapas(etapas)
