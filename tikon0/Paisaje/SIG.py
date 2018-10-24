"""
Para manejar datos de SIG de parcelas.
"""


class Parcela(object):
    def __init__(símismo, coordinadas):
        símismo.coordinadas = coordinadas
        símismo.área = símismo.calcular_área()

    def calcular_área(símismo):
        área = 0
        # Mágia aquí
        return área
