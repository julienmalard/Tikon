from tikon.RAE import Insecto as Ins


class பூச்சி(Ins.Insecto):
    def __init__(தாங்கள், பெயர், திட்டம், முட்டை=False, புழு_எண்=0, கூடு=False, பெரியது=True, சமன்பாடு_வகை=None):
        super().__init__(nombre=பெயர், proyecto=திட்டம், huevo=முட்டை, njuvenil=புழு_எண்,
                         pupa=கூடு, adulto=பெரியது, tipo_ecuaciones=சமன்பாடு_வகை)

    def தின்றுகிறது(தாங்கள், இரை, இரை_படி=None, தின்றவர்_படி=None):
        super().secome(presa=இரை, etps_presa=இரை_படி, etps_depred=தின்றவர்_படி)

    def தின்றாது(தாங்கள், இரை, இரை_படி=None, தின்றவர்_படி=None):
        super().nosecome(presa=இரை, etps_presa=இரை_படி, etps_depred=தின்றவர்_படி)


class ஒட்டுணி(Ins.Parasitoide):
    def __init__(தாங்கள்,  பெயர், திட்டம், கூடு=False):
        super().__init__(nombre=பெயர், proyecto=திட்டம், pupa=கூடு)

    def ஒட்டுணி_இல்லை(símismo, இரை, உள்ளே=None):
        super().noparasita(víctima=இரை, etps_infec=உள்ளே)

    def இதின்_ஒட்டுணி(தாங்கள், இரை, உள்ளே, வெளியே):
        super().parasita(víctima=இரை, etps_infec=உள்ளே, etp_sale=வெளியே)


class ஸ்பெசிடெ(Ins.Esfécido):
    def __init__(தாங்கள்,  பெயர், திட்டம்):
        super().__init__(nombre=பெயர், proyecto=திட்டம்)

    def பிடிக்காது(தாங்கள், இரை, இரை_படி=None):
        super().nocaptura(víctima=இரை, etps_víc=இரை_படி)

    def பிடிக்கும்(தாங்கள், இரை, இரை_படி):
        super().captura(víctima=இரை, etps_víc=இரை_படி)


class எளியது(Ins.Sencillo):
    def __init__(தாங்கள்,  பெயர், திட்டம்):
        super().__init__(nombre=பெயர், proyecto=திட்டம்)

    def தின்றுகிறது(தாங்கள், இரை, இரை_படி=None, தின்றவர்_படி=None):
        super().secome(presa=இரை, etps_presa=இரை_படி, etps_depred=தின்றவர்_படி)

    def தின்றாது(தாங்கள், இரை, இரை_படி=None, தின்றவர்_படி=None):
        super().nosecome(presa=இரை, etps_presa=இரை_படி, etps_depred=தின்றவர்_படி)
