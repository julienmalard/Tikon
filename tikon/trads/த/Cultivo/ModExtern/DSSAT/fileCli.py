from tikon.Cultivo.ModExtern.DSSAT.fileCli import FileCli


class FileCli(FileCli):

    def leer(தன், cod_clima):
        return super().leer(cod_clima=cod_clima)

    def escribir(தன்):
        return super().escribir()

    def decodar(தன், doc):
        return super().decodar(doc=doc)

    def encodar(தன், doc_clima):
        return super().encodar(doc_clima=doc_clima)
