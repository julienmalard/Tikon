from tikon.RAE.Insecto import Esfécido
from tikon.RAE.Insecto import Insecto
from tikon.RAE.Insecto import MetamCompleta
from tikon.RAE.Insecto import MetamIncompleta
from tikon.RAE.Insecto import Parasitoide
from tikon.RAE.Insecto import Sencillo


class பூச்சி(Insecto):

    def தின்றுகிறது(தன், இரை, இரை_படி=None, தின்றவர்_படி=None):
        return தன்.secome(presa=இரை, etps_presa=இரை_படி, etps_depred=தின்றவர்_படி)

    def தின்றாது(தன், இரை, இரை_படி=None, தின்றவர்_படி=None):
        return தன்.nosecome(presa=இரை, etps_presa=இரை_படி, etps_depred=தின்றவர்_படி)


class Sencillo(Sencillo):


class MetamCompleta(MetamCompleta):


class MetamIncompleta(MetamIncompleta):


class Parasitoide(Parasitoide):

    def parasita(தன், víctima, etps_infec, etp_sale):
        return super().parasita(víctima=víctima, etps_infec=etps_infec, etp_sale=etp_sale)

    def noparasita(தன், víctima, etps_infec=None):
        return super().noparasita(víctima=víctima, etps_infec=etps_infec)


class Esfécido(Esfécido):

    def captura(தன், víctima, etps_víc):
        return super().captura(víctima=víctima, etps_víc=etps_víc)

    def nocaptura(தன், víctima, etps_víc=None):
        return super().nocaptura(víctima=víctima, etps_víc=etps_víc)
