from tikon.Cultivo.ModExtern.DSSAT.fileX import FileX


class FileX(FileX):

    def leer(தன், documento):
        return super().leer(documento=documento)

    def escribir(தன், carpeta):
        return super().escribir(carpeta=carpeta)

    def decodar(தன், doc, sección):
        return super().decodar(doc=doc, sección=sección)

    def encodar(தன், doc, sección):
        return super().encodar(doc=doc, sección=sección)
