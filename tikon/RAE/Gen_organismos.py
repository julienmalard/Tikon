import os.path

from tikon import RAE as RAE


def generar_org(archivo):
    """
    Esta función devuelve una instancia de Organismo, con la subclase apropiada para la extensión del archivo
    especificado.
    Notar que NO podrá encontrar subclases de Organismo que no se importan en el código __init__ de RAE.

    :param archivo: El archivo fuente.
    :type archivo: str

    :return: La instancia apropiada.
    :rtype: RAE.Organismo.Organismo
    """

    def sacar_subclases(cls):
        """
        Una función muy útil. Saca una lista de las subclases de una clase. 
        Se me olvido cómo hace lo que hace, exactamente.
        
        :param cls: La clase cuyas subclases querremos
        :type cls: type

        :return: Una lista de las subclases del la clase
        :rtype: list

        """
        return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                       for g in sacar_subclases(s)]

    proyecto, nombre_con_ext = os.path.split(archivo)
    nombre, ext = os.path.splitext(nombre_con_ext)

    for sub in sacar_subclases(RAE.Organismo.Organismo):
        if sub.ext == ext:
            obj_org = sub(nombre=nombre, proyecto=proyecto)  # type: RAE.Organismo.Organismo
            obj_org.cargar(fuente=archivo)

    raise ValueError('No se encontró subclase de Organismo con extensión %s.' % ext)
