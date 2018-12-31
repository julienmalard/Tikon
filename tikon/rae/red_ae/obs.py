from tikon.result.obs import Obs
from .red import RedAE


class ObsRAE(Obs):
    def __init__(símismo, var, datos, dims, tiempo):
        super().__init__(mód=RedAE, var=var, datos=datos, dims=dims, tiempo=tiempo)


class ObsPobs(ObsRAE):
    def __init__(símismo, datos, dims, tiempo):
        super().__init__(var='Pobs', datos=datos, dims=dims, tiempo=tiempo)
