from REDES.REDES import Red
from REDES.INSECTOS import Simple

# Inicializar los insectos en la red
குளவி = Simple("குளவி")
அசிலிடெ = Simple("அசிலிடெ")
இலைசுருட்டுப்புழு= Simple("இலைசுருட்டுப்புழு")


# Establecer las interacciones entre insectos
இலைசுருட்டுப்புழு.secome('கருவேப்பிலை')
குளவி.secome(இலைசுருட்டுப்புழு)
அசிலிடெ.secome(இலைசுருட்டுப்புழு)

# Poner los coeficientes para las ecuaciones de poblaciones
இலைசுருட்டுப்புழு.fases["Adulto"].dic["coefs"]["r"] = 2
இலைசுருட்டுப்புழு.fases["Adulto"].dic["coefs"][குளவி.fases["Adulto"].nombre] = 3
இலைசுருட்டுப்புழு.fases["Adulto"].dic["coefs"][அசிலிடெ.fases["Adulto"].nombre] = 3
இலைசுருட்டுப்புழு.fases["Adulto"].dic["coefs"]["கருவேப்பிலை"] = 5
குளவி.fases["Adulto"].dic["coefs"]["r"] = 0.1
குளவி.fases["Adulto"].dic["coefs"][இலைசுருட்டுப்புழு.fases["Adulto"].nombre] = 0.4
குளவி.fases["Adulto"].dic["coefs"]['comida_crít'] = 100
அசிலிடெ.fases["Adulto"].dic["coefs"]["r"] = 0.15
அசிலிடெ.fases["Adulto"].dic["coefs"][இலைசுருட்டுப்புழு.fases["Adulto"].nombre] = 0.4
அசிலிடெ.fases["Adulto"].dic["coefs"]['comida_crít'] = 100

# Crear la red agroecológica
கருவேப்பிலை = Red("கறிவேப்பிலை", insectos=[இலைசுருட்டுப்புழு, குளவி, அசிலிடெ])

poblaciones_iniciales = {"அசிலிடெ": {"Adulto": 1}, "இலைசுருட்டுப்புழு": {"Adulto": 100}, "குளவி": {"Adulto": 2}}

# Inicializar la red
கருவேப்பிலை.ejec(poblaciones_iniciales=poblaciones_iniciales)

# Incrementar el tiempo
tiempo_final = 100
for i in range(tiempo_final):
    கருவேப்பிலை.incr(paso=1, estado_cultivo={"கருவேப்பிலை": 100})
print(கருவேப்பிலை.poblaciones)


# Crear la red agroecológica
கருவேப்பிலை_௨ = Red("கறிவேப்பிலை", insectos=[குளவி, இலைசுருட்டுப்புழு, அசிலிடெ])

# Inicializar la red
கருவேப்பிலை_௨.ejec(poblaciones_iniciales=poblaciones_iniciales)

# Poner los coeficientes para las ecuaciones de poblaciones
குளவி.fases["Adulto"].dic["coefs"][அசிலிடெ.fases["Adulto"].nombre] = 0.05
அசிலிடெ.fases["Adulto"].dic["coefs"][குளவி.fases["Adulto"].nombre] = 0.01

# Incrementar el tiempo
கருவேப்பிலை_௨.simul(paso=1, estado_cultivo=100000, tiempo_final=100)
