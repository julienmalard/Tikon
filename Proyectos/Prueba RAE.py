from PLAGAS.REDES import *
from PLAGAS.INSECTOS import *

# Inicializar los insectos en la red
குளவி = Insecto("குளவி", dic={"ciclo_vida": "simple"})
அசிலிடெ = Insecto("அசிலிடெ", dic={"ciclo_vida": "simple"})
இலைசுருட்டுப்புழு= Insecto("இலைசுருட்டுப்புழு", dic={"ciclo_vida": "simple"})


# Establecer las interacciones entre insectos
இலைசுருட்டுப்புழு.fases["Adulto"].dic["Depredadores"] = [அசிலிடெ.fases["Adulto"], குளவி.fases["Adulto"]]
குளவி.fases["Adulto"].dic["Presas"] = [இலைசுருட்டுப்புழு.fases["Adulto"]]
அசிலிடெ.fases["Adulto"].dic["Presas"] = [இலைசுருட்டுப்புழு.fases["Adulto"]]
இலைசுருட்டுப்புழு.fases["Adulto"].dic["Presas"] = ["கருவேப்பிலை"]


# Crear la red agroecológica
கருவேப்பிலை = Red("கறிவேப்பிலை", dic=dict(Insectos={"அசிலிடெ": அசிலிடெ, "குளவி": குளவி,
                                                    "இலைசுருட்டுப்புழு": இலைசுருட்டுப்புழு},
                                          tipo_ecuaciones="capacidad_de_carga"))

poblaciones_iniciales={"அசிலிடெ": {"Adulto": 1}, "இலைசுருட்டுப்புழு": {"Adulto": 100}, "குளவி": {"Adulto": 2}}

# Inicializar la red
கருவேப்பிலை.ejec(poblaciones_iniciales=poblaciones_iniciales)

# Poner los coeficientes para las ecuaciones de poblaciones
இலைசுருட்டுப்புழு.fases["Adulto"].dic["coefs"]["r"] = 2
இலைசுருட்டுப்புழு.fases["Adulto"].dic["coefs"][குளவி.fases["Adulto"].nombre] = 3
இலைசுருட்டுப்புழு.fases["Adulto"].dic["coefs"][அசிலிடெ.fases["Adulto"].nombre] = 3
இலைசுருட்டுப்புழு.fases["Adulto"].dic["coefs"]["கருவேப்பிலை"] = 5
குளவி.fases["Adulto"].dic["coefs"]["r"] = 0.1
குளவி.fases["Adulto"].dic["coefs"][இலைசுருட்டுப்புழு.fases["Adulto"].nombre] = 0.4
அசிலிடெ.fases["Adulto"].dic["coefs"]["r"] = 0.15
அசிலிடெ.fases["Adulto"].dic["coefs"][இலைசுருட்டுப்புழு.fases["Adulto"].nombre] = 0.4
அசிலிடெ.fases["Adulto"].dic["coefs"]['comida_crít'] = 100


# Incrementar el tiempo
tiempo_final = 100
for i in range(tiempo_final):
    கருவேப்பிலை.incr(paso=1, estado_cultivo={"கருவேப்பிலை": 100})
print(கருவேப்பிலை.poblaciones)

import pygal
gráfico = pygal.Line(interpolate='cubic')
gráfico.title = "கருவேப்பிலைப் பூச்சிகள்"
gráfico.x_labels = map(str, range(0, tiempo_final, int(tiempo_final/10)))
gráfico.add('இலைசுருட்டுப்புழு', கருவேப்பிலை.poblaciones["இலைசுருட்டுப்புழு"]["Adulto"])
gráfico.add('குளவி', கருவேப்பிலை.poblaciones["குளவி"]["Adulto"])
gráfico.add('அசிலிடெ', கருவேப்பிலை.poblaciones["அசிலிடெ"]["Adulto"])
gráfico.render_to_file('F:\Julien\PhD\Python\PLAGAS\கருவேப்பிலைப் பூச்சிகள்.svg')




# Crear la red agroecológica
கருவேப்பிலை_௨ = Red("கறிவேப்பிலை", dic=dict(Insectos={"அசிலிடெ": அசிலிடெ, "குளவி": குளவி,
                                                      "இலைசுருட்டுப்புழு": இலைசுருட்டுப்புழு},
                                            tipo_ecuaciones="capacidad_de_carga"))

# Inicializar la red
கருவேப்பிலை_௨.ejec(poblaciones_iniciales=poblaciones_iniciales)

# Poner los coeficientes para las ecuaciones de poblaciones
குளவி.fases["Adulto"].dic["coefs"][அசிலிடெ.fases["Adulto"].nombre] = 0.05
அசிலிடெ.fases["Adulto"].dic["coefs"][குளவி.fases["Adulto"].nombre] = 0.01

# Incrementar el tiempo
tiempo_final = 100
for i in range(tiempo_final):
    கருவேப்பிலை_௨.incr(paso=1, estado_cultivo={"கருவேப்பிலை": 100})
print(கருவேப்பிலை_௨.poblaciones)


import pygal
gráfico = pygal.Line(interpolate='cubic')
gráfico.title = "கருவேப்பிலைப் பூச்சிகள்"
gráfico.x_labels = map(str, range(0, tiempo_final, int(tiempo_final/10)))
gráfico.add('இலைசுருட்டுப்புழு', கருவேப்பிலை_௨.poblaciones["இலைசுருட்டுப்புழு"]["Adulto"])
gráfico.add('குளவி', கருவேப்பிலை_௨.poblaciones["குளவி"]["Adulto"])
gráfico.add('அசிலிடெ', கருவேப்பிலை_௨.poblaciones["அசிலிடெ"]["Adulto"])
gráfico.render_to_file('F:\Julien\PhD\Python\PLAGAS\கருவேப்பிலைப் பூச்சிகள்_௨.svg')
