from Matemáticas.Incert import VarCalib, VarPyMC2, VarPyMC3
from tikon.Matemáticas.Calib import ModBayes
from tikon.Matemáticas.Calib import ModCalib
from tikon.Matemáticas.Calib import ModGLUE


class ModCalib(ModCalib):

    def calib(தன், rep, quema, extraer):
        return super().calib(rep=rep, quema=quema, extraer=extraer)

    def guardar(தன், பெயர்=None):
        return super().guardar(nombre=பெயர்)


class ModBayes(ModBayes):

    def calib(தன், rep, quema, extraer):
        return super().calib(rep=rep, quema=quema, extraer=extraer)

    def guardar(தன், பெயர்=None):
        return super().guardar(nombre=பெயர்)


class ModGLUE(ModGLUE):

    def calib(தன், rep, quema, extraer):
        return super().calib(rep=rep, quema=quema, extraer=extraer)

    def guardar(தன், பெயர்=None):
        return super().guardar(nombre=பெயர்)


class VarCalib(VarCalib):

    def obt_val(தன்):
        return super().obt_val()

    def dibujar(தன்):
        return super().dibujar()

    def traza(தன்):
        return super().traza()


class VarPyMC2(VarPyMC2):

    def obt_val(தன்):
        return super().obt_val()

    def dibujar(தன்):
        return super().dibujar()

    def traza(தன்):
        return super().traza()


class VarPyMC3(VarPyMC3):

    def obt_val(தன்):
        return super().obt_val()

    def dibujar(தன்):
        return super().dibujar()

    def traza(தன்):
        return super().traza()
