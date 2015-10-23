print("Importando dependencias...")
from REDES.REDES import *
from REDES.INSECTOS import *
# from pymc import *
# import numpy as np
# from Proyectos.Prueba_incert import *
print("Importación de dependencias terminada.")


Red_coco = Red("Red_coco",
               dic=dict(Insectos={"Oarenosella": Insecto("Oarenosella", dic={"ciclo_vida": "estadios = 5"}),
                                  "Parasitoidelarva": Insecto("Parasitoidelarva",
                                                              dic={"ciclo_vida": "simple",
                                                                   "tipo_ecuaciones": "capacidad_de_carga"}),
                                  "Parasitoidepupa": Insecto("Parasitoidepupa",
                                                             dic={"ciclo_vida": "simple",
                                                                  "tipo_ecuaciones": "capacidad_de_carga"})},
                        tipo_ecuaciones="presas_mortalidad"))

Red_coco_compl = Red("Red_coco_compl",
                     dic=dict(Insectos={"Oarenosella": Insecto("Oarenosella", dic={"ciclo_vida": "estadios = 5"}),
                                        "Parasitoidelarva": Insecto("Parasitoidelarva",
                                                                    dic={"ciclo_vida": "simple",
                                                                         "tipo_ecuaciones": "capacidad_de_carga"}),
                                        "Parasitoidepupa": Insecto("Parasitoidepupa",
                                                                   dic={"ciclo_vida": "simple",
                                                                        "tipo_ecuaciones": "capacidad_de_carga"}),
                                        "Araña": Insecto("Araña", dic={"ciclo_vida": "simple",
                                                                       "tipo_ecuaciones": "capacidad_de_carga"})},
                              tipo_ecuaciones="presas_mortalidad"))


poblaciones_iniciales = {"Oarenosella": {"Pupa": 300, "Juvenil1": 0, "Juvenil2": 90, "Juvenil3": 200,
                                         "Juvenil4": 175, "Juvenil5": 250},
                         "Parasitoidelarva": {"Adulto": 42.9},
                         "Parasitoidepupa": {"Adulto": 45},
                         "Araña": {"Adulto": 10}}


for red in [Red_coco, Red_coco_compl]:
    # Establecer las relaciones tróficas
    Oarenosella = red.dic['Insectos']['Oarenosella']
    Parasitoidelarva = red.dic['Insectos']['Parasitoidelarva']
    Parasitoidepupa = red.dic['Insectos']['Parasitoidepupa']
    Parasitoidelarva.fases["Adulto"].dic['Presas'] = []
    for i in range(3, 6):
        Oarenosella.fases["Juvenil" + str(i)].dic["Depredadores"] = [Parasitoidelarva.fases["Adulto"]]
        Parasitoidelarva.fases["Adulto"].dic['Presas'] += [Oarenosella.fases['Juvenil' + str(i)]]
    for i in range(1, 6):
        Oarenosella.fases["Juvenil" + str(i)].dic["Presas"] = ["Coco"]
    Oarenosella.fases["Pupa"].dic["Depredadores"] = [Parasitoidepupa.fases["Adulto"]]
    Parasitoidepupa.fases['Adulto'].dic['Presas'] = [Oarenosella.fases['Pupa']]

    # Establecer los coeficientes del modelo
    for i in range(1, 6):
        Oarenosella.fases["Juvenil" + str(i)].dic["coefs"]["mortalidad"] = 0.02
        Oarenosella.fases["Juvenil" + str(i)].dic["coefs"]["comida_crít"] = 48
        Oarenosella.fases["Juvenil" + str(i)].dic["coefs"]["Coco"] = 1
        Oarenosella.fases["Juvenil" + str(i)].dic["coefs"]["días_trans"] = 4
    for i in range(3, 6):
        Oarenosella.fases["Juvenil" + str(i)].dic["coefs"][Parasitoidelarva.fases["Adulto"].nombre] = .5
        Parasitoidelarva.fases["Adulto"].dic["coefs"][Oarenosella.fases["Juvenil" + str(i)].nombre] = .2

    Oarenosella.fases["Juvenil1"].dic["coefs"]["días_trans_prom"] = 9
    Oarenosella.fases["Juvenil2"].dic["coefs"]["días_trans_prom"] = 7
    Oarenosella.fases["Juvenil3"].dic["coefs"]["días_trans_prom"] = 7
    Oarenosella.fases["Juvenil4"].dic["coefs"]["días_trans_prom"] = 5
    Oarenosella.fases["Juvenil5"].dic["coefs"]["días_trans_prom"] = 10

    Oarenosella.fases["Pupa"].dic["coefs"]["días_mort_prom"] = 15
    Oarenosella.fases["Pupa"].dic["coefs"]["días_mort"] = 4
    Oarenosella.fases["Pupa"].dic["coefs"]["días_repr_prom"] = 10
    Oarenosella.fases["Pupa"].dic["coefs"]["días_repr"] = 6
    Oarenosella.fases["Pupa"].dic["coefs"]["r"] = 10
    Oarenosella.fases["Pupa"].dic["coefs"][Parasitoidepupa.fases["Adulto"].nombre] = .5

    Parasitoidepupa.fases["Adulto"].dic["coefs"][Oarenosella.fases["Pupa"].nombre] = 1
    Parasitoidepupa.fases["Adulto"].dic["coefs"]["r"] = .01

    Parasitoidelarva.fases["Adulto"].dic["coefs"]["r"] = .05
    Parasitoidelarva.fases["Adulto"].dic["coefs"]["comida_crít"] = 5

    if red == Red_coco_compl:
        Araña = red.dic['Insectos']['Araña']
        Araña.fases["Adulto"].dic["Presas"] = [Parasitoidelarva.fases["Adulto"], Parasitoidepupa.fases["Adulto"],
                                               Oarenosella.fases["Juvenil1"], Oarenosella.fases["Juvenil2"],
                                               Oarenosella.fases["Juvenil3"], Oarenosella.fases["Juvenil4"],
                                               Oarenosella.fases["Juvenil5"]
                                               ]
        Parasitoidepupa.fases["Adulto"].dic["Depredadores"] = [Araña.fases["Adulto"]]
        Parasitoidelarva.fases["Adulto"].dic["Depredadores"] = [Araña.fases["Adulto"]]
        Araña.fases["Adulto"].dic["coefs"][Parasitoidelarva.fases["Adulto"].nombre] = .1
        Araña.fases["Adulto"].dic["coefs"][Parasitoidepupa.fases["Adulto"].nombre] = .1

        Parasitoidepupa.fases["Adulto"].dic["coefs"][Araña.fases["Adulto"].nombre] = .05
        Parasitoidelarva.fases["Adulto"].dic["coefs"][Araña.fases["Adulto"].nombre] = .05
        for i in range(1, 6):
            Oarenosella.fases["Juvenil" + str(i)].dic['Depredadores'] = [Araña.fases['Adulto']]
            Oarenosella.fases["Juvenil" + str(i)].dic["coefs"][Araña.fases["Adulto"].nombre] = 1
            Araña.fases["Adulto"].dic["coefs"][Oarenosella.fases["Juvenil" + str(i)].nombre] = .5
        Araña.fases["Adulto"].dic["coefs"]["r"] = .05
        Araña.fases["Adulto"].dic["coefs"]["comida_crít"] = 1

tiempo_final = 300
Simul_coco = Red_coco.simul(paso=1, pob_inic=poblaciones_iniciales,
                            estado_cultivo={"Coco": 1000000000}, tiempo_final=tiempo_final)

print("Simulación 1 terminada.")

Simul_coco_compl = Red_coco_compl.simul(paso=1, pob_inic=poblaciones_iniciales,
                                        estado_cultivo={"Coco": 1000000000}, tiempo_final=tiempo_final)


print("Simulación 2 terminada. Generando gráficos...")

red = Red_coco
larvas = [a + b + c + d + e for a, b, c, d, e in zip(red.poblaciones["Oarenosella"]["Juvenil5"],
                                                     red.poblaciones["Oarenosella"]["Juvenil4"],
                                                     red.poblaciones["Oarenosella"]["Juvenil3"],
                                                     red.poblaciones["Oarenosella"]["Juvenil2"],
                                                     red.poblaciones["Oarenosella"]["Juvenil1"])
          ]

import pygal
gráfico = pygal.Line(interpolate='cubic', show_dots=False)
gráfico.title = "கருந்தலைப் புழு"
gráfico.x_labels = map(str, range(0, tiempo_final, max(1, int(tiempo_final/10))))
gráfico.add('புழு_௧', red.poblaciones["Oarenosella"]["Juvenil1"])
gráfico.add('புழு_௨', red.poblaciones["Oarenosella"]["Juvenil2"])
gráfico.add('புழு_௩', red.poblaciones["Oarenosella"]["Juvenil3"])
gráfico.add('புழு_௪', red.poblaciones["Oarenosella"]["Juvenil4"])
gráfico.add('புழு_௫', red.poblaciones["Oarenosella"]["Juvenil5"])
gráfico.add('புழு_எல்லாம்', larvas)
gráfico.add('கூட்டுப்புழு', red.poblaciones["Oarenosella"]["Pupa"])
# gráfico.add('ஒட்டுண்ணி_புழு', Red_coco.poblaciones["Parasitoidelarva"]["Adulto"])
# gráfico.add('ஒட்டுண்ணி_கூட்டை', Red_coco.poblaciones["Parasitoidepupa"]["Adulto"])
gráfico.render_to_file('F:\Julien\PhD\Python\PLAGAS\Oarenosella_' + red.nombre + '.svg')

print("Gráfico 1 terminado.")

gráfico_para = pygal.Line(interpolate='cubic', show_dots=False)
gráfico_para.title = "கருந்தலைப் புழு ஒட்டுண்ணிகள்"
gráfico_para.x_labels = map(str, range(0, tiempo_final, max(1, int(tiempo_final/10))))
gráfico_para.add('பு. குளவி', red.poblaciones["Parasitoidelarva"]["Adulto"])
gráfico_para.add('கூ. பு. குளவி', red.poblaciones["Parasitoidepupa"]["Adulto"])

gráfico_para.render_to_file('F:\Julien\PhD\Python\PLAGAS\Oarenosella_parasitoides_' + red.nombre + '.svg')

print("Gráfico 2 terminado.")


red = Red_coco_compl
larvas = [a + b + c + d + e for a, b, c, d, e in zip(red.poblaciones["Oarenosella"]["Juvenil5"],
                                                     red.poblaciones["Oarenosella"]["Juvenil4"],
                                                     red.poblaciones["Oarenosella"]["Juvenil3"],
                                                     red.poblaciones["Oarenosella"]["Juvenil2"],
                                                     red.poblaciones["Oarenosella"]["Juvenil1"])
          ]

import pygal
gráfico = pygal.Line(interpolate='cubic', show_dots=False)
gráfico.title = "கருந்தலைப் புழு"
gráfico.x_labels = map(str, range(0, tiempo_final, max(1, int(tiempo_final/10))))
gráfico.add('புழு_௧', red.poblaciones["Oarenosella"]["Juvenil1"])
gráfico.add('புழு_௨', red.poblaciones["Oarenosella"]["Juvenil2"])
gráfico.add('புழு_௩', red.poblaciones["Oarenosella"]["Juvenil3"])
gráfico.add('புழு_௪', red.poblaciones["Oarenosella"]["Juvenil4"])
gráfico.add('புழு_௫', red.poblaciones["Oarenosella"]["Juvenil5"])
gráfico.add('புழு_எல்லாம்', larvas)
gráfico.add('கூட்டுப்புழு', red.poblaciones["Oarenosella"]["Pupa"])
# gráfico.add('ஒட்டுண்ணி_புழு', Red_coco.poblaciones["Parasitoidelarva"]["Adulto"])
# gráfico.add('ஒட்டுண்ணி_கூட்டை', Red_coco.poblaciones["Parasitoidepupa"]["Adulto"])
gráfico.render_to_file('F:\Julien\PhD\Python\PLAGAS\Oarenosella_' + red.nombre + '.svg')

print("Gráfico 1 terminado.")

gráfico_para = pygal.Line(interpolate='cubic', show_dots=False)
gráfico_para.title = "கருந்தலைப் புழு ஒட்டுண்ணிகள்"
gráfico_para.x_labels = map(str, range(0, tiempo_final, max(1, int(tiempo_final/10))))
gráfico_para.add('பு. குளவி', red.poblaciones["Parasitoidelarva"]["Adulto"])
gráfico_para.add('கூ. பு. குளவி', red.poblaciones["Parasitoidepupa"]["Adulto"])
gráfico_para.add('சிலந்தி', red.poblaciones["Araña"]["Adulto"])
gráfico_para.render_to_file('F:\Julien\PhD\Python\PLAGAS\Oarenosella_parasitoides_' + red.nombre + '.svg')

print("Gráfico 2 terminado.")



# Entrar los datos observados para la calibración:
datos_coco = {"Oarenosella": {"Pupa": [300, -99, -99, -99, -99, -99, -99, -99, 260, -99, -99, -99, -99, -99, -99, -99, 60, -99, -99, -99, -99, -99, -99, -99, 40, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 120, -99, -99, -99, -99, -99, -99, -99, 110, -99, -99, -99, -99, -99, -99, -99, 45, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 70, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 60, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 85, -99, -99, -99, -99, -99, -99, -99, 30, -99, -99, -99, -99, -99, -99, -99, 15, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 12, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0],
                              "Juvenil1": [0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 850, -99, -99, -99, -99, -99, -99, -99, 1200, -99, -99, -99, -99, -99, -99, -99, 210, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 410, -99, -99, -99, -99, -99, -99, -99, 650, -99, -99, -99, -99, -99, -99, -99, 300, -99, -99, -99, -99, -99, -99, -99, 40, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 300, -99, -99, -99, -99, -99, -99, -99, 170, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 140, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0],
                              "Juvenil2": [90, -99, -99, -99, -99, -99, -99, -99, 25, -99, -99, -99, -99, -99, -99, -99, 25, -99, -99, -99, -99, -99, -99, -99, 100, -99, -99, -99, -99, -99, -99, -99, 780, -99, -99, -99, -99, -99, -99, -99, 800, -99, -99, -99, -99, -99, -99, -99, 300, -99, -99, -99, -99, -99, -99, -99, 125, -99, -99, -99, -99, -99, -99, -99, 40, -99, -99, -99, -99, -99, -99, -99, 25, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 250, -99, -99, -99, -99, -99, -99, -99, 25, -99, -99, -99, -99, -99, -99, -99, 375, -99, -99, -99, -99, -99, -99, -99, 175, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 25, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 15, -99, -99, -99, -99, -99, -99, -99, 100, -99, -99, -99, -99, -99, -99, -99, 250, -99, -99, -99, -99, -99, -99, -99, 270, -99, -99, -99, -99, -99, -99, -99, 100, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 150, -99, -99, -99, -99, -99, -99, -99, 160, -99, -99, -99, -99, -99, -99, -99, 100, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0],
                              "Juvenil3": [200, -99, -99, -99, -99, -99, -99, -99, 100, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 200, -99, -99, -99, -99, -99, -99, -99, 700, -99, -99, -99, -99, -99, -99, -99, 300, -99, -99, -99, -99, -99, -99, -99, 280, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 5, -99, -99, -99, -99, -99, -99, -99, 120, -99, -99, -99, -99, -99, -99, -99, 280, -99, -99, -99, -99, -99, -99, -99, 225, -99, -99, -99, -99, -99, -99, -99, 150, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 280, -99, -99, -99, -99, -99, -99, -99, 250, -99, -99, -99, -99, -99, -99, -99, 100, -99, -99, -99, -99, -99, -99, -99, 60, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 60, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0],
                              "Juvenil4": [175, -99, -99, -99, -99, -99, -99, -99, 170, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 425, -99, -99, -99, -99, -99, -99, -99, 300, -99, -99, -99, -99, -99, -99, -99, 275, -99, -99, -99, -99, -99, -99, -99, 100, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 150, -99, -99, -99, -99, -99, -99, -99, 225, -99, -99, -99, -99, -99, -99, -99, 200, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 175, -99, -99, -99, -99, -99, -99, -99, 225, -99, -99, -99, -99, -99, -99, -99, 150, -99, -99, -99, -99, -99, -99, -99, 100, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 50, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0],
                              "Juvenil5": [250, -99, -99, -99, -99, -99, -99, -99, 180, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 300, -99, -99, -99, -99, -99, -99, -99, 310, -99, -99, -99, -99, -99, -99, -99, 280, -99, -99, -99, -99, -99, -99, -99, 150, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 175, -99, -99, -99, -99, -99, -99, -99, 175, -99, -99, -99, -99, -99, -99, -99, 125, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 75, -99, -99, -99, -99, -99, -99, -99, 150, -99, -99, -99, -99, -99, -99, -99, 150, -99, -99, -99, -99, -99, -99, -99, 70, -99, -99, -99, -99, -99, -99, -99, 65, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 70, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0]},
              "Parasitoidelarva": {"Adulto": [42.9, -99, -99, -99, -99, -99, -99, -99, 76, -99, -99, -99, -99, -99, -99, -99, 71.6, -99, -99, -99, -99, -99, -99, -99, 26.2, -99, -99, -99, -99, -99, -99, -99, 22.32, -99, -99, -99, -99, -99, -99, -99, 44.9, -99, -99, -99, -99, -99, -99, -99, 36.6, -99, -99, -99, -99, -99, -99, -99, 57.6, -99, -99, -99, -99, -99, -99, -99, 88.4, -99, -99, -99, -99, -99, -99, -99, 78.3, -99, -99, -99, -99, -99, -99, -99, 26.4, -99, -99, -99, -99, -99, -99, -99, 27.75, -99, -99, -99, -99, -99, -99, -99, 3.7, -99, -99, -99, -99, -99, -99, -99, 24.45, -99, -99, -99, -99, -99, -99, -99, 20, -99, -99, -99, -99, -99, -99, -99, 23, -99, -99, -99, -99, -99, -99, -99, 17.5, -99, -99, -99, -99, -99, -99, -99, 15.4, -99, -99, -99, -99, -99, -99, -99, 12.6, -99, -99, -99, -99, -99, -99, -99, 13.5, -99, -99, -99, -99, -99, -99, -99, 7, -99, -99, -99, -99, -99, -99, -99, 32, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 24.6, -99, -99, -99, -99, -99, -99, -99, 6.9, -99, -99, -99, -99, -99, -99, -99, 10.5, -99, -99, -99, -99, -99, -99, -99, 22.8, -99, -99, -99, -99, -99, -99, -99, 6, -99, -99, -99, -99, -99, -99, -99, 1.6, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 1.8, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 3.8, -99, -99, -99, -99, -99, -99, -99, 1.2, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0]},
              "Parasitoidepupa": {"Adulto": [45, -99, -99, -99, -99, -99, -99, -99, 72.8, -99, -99, -99, -99, -99, -99, -99, 18, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 3.6, -99, -99, -99, -99, -99, -99, -99, 12, -99, -99, -99, -99, -99, -99, -99, 33.6, -99, -99, -99, -99, -99, -99, -99, 83.6, -99, -99, -99, -99, -99, -99, -99, 40.05, -99, -99, -99, -99, -99, -99, -99, 10, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 1.6, -99, -99, -99, -99, -99, -99, -99, 2.8, -99, -99, -99, -99, -99, -99, -99, 24.5, -99, -99, -99, -99, -99, -99, -99, 37.5, -99, -99, -99, -99, -99, -99, -99, 11.4, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 36, -99, -99, -99, -99, -99, -99, -99, 34, -99, -99, -99, -99, -99, -99, -99, 85, -99, -99, -99, -99, -99, -99, -99, 20.1, -99, -99, -99, -99, -99, -99, -99, 3, -99, -99, -99, -99, -99, -99, -99, 2.7, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0, -99, -99, -99, -99, -99, -99, -99, 0]}
              }

datos_coco_simpl = {"Oarenosella": {"Pupa": [300, 260, 60, 40, 0, 20, 50, 120, 110, 45, 10, 0, 0, 10, 20, 70, 50, 20, 0, 0, 0, 0, 60, 50, 85, 30, 15, 10, 0, 0, 0, 10, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    "Juvenil1": [0, 0, 850, 1200, 210, 20, 10, 0, 0, 410, 650, 300, 40, 0, 0, 0, 0, 10, 300, 170, 50, 0, 0, 0, 0, 50, 140, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    "Juvenil2": [90, 25, 25, 100, 780, 800, 300, 125, 40, 25, 10, 250, 25, 375, 175, 50, 25, 0, 15, 100, 250, 270, 100, 10, 0, 0, 10, 50, 150, 160, 100, 50, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    "Juvenil3": [200, 100, 10, 0, 200, 700, 300, 280, 50, 0, 0, 5, 120, 280, 225, 150, 50, 20, 0, 0, 50, 280, 250, 100, 60, 10, 10, 0, 10, 20, 60, 50, 50, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    "Juvenil4": [175, 170, 0, 10, 50, 425, 300, 275, 100, 0, 0, 0, 0, 150, 225, 200, 50, 20, 0, 0, 0, 175, 225, 150, 100, 50, 10, 0, 0, 0, 20, 20, 50, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    "Juvenil5": [250, 180, 10, 0, 0, 300, 310, 280, 150, 0, 0, 0, 0, 10, 175, 175, 125, 20, 0, 0, 0, 75, 150, 150, 70, 65, 20, 0, 0, 0, 0, 0, 70, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
                    "Parasitoidelarva": {"Adulto": [42.9, 76, 71.6, 26.2, 22.32, 44.9, 36.6, 57.6, 88.4, 78.3, 26.4, 27.75, 3.7, 24.45, 20, 23, 17.5, 15.4, 12.6, 13.5, 7, 32, 0, 24.6, 6.9, 10.5, 22.8, 6, 1.6, 0, 1.8, 0, 3.8, 1.2, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
                    "Parasitoidepupa": {"Adulto": [45, 72.8, 18, 0, 0, 3.6, 12, 33.6, 83.6, 40.05, 10, 0, 0, 1.6, 2.8, 24.5, 37.5, 11.4, 0, 0, 0, 0, 36, 34, 85, 20.1, 3, 2.7, 0, 0, 0, 0, 0]}
                    }
#
# # Crear el modelo
# print("Inicializando el modelo Bayesiano...")
# modelo = inic_calib(Red_coco, datos_coco_simpl, 300, poblaciones_iniciales=poblaciones_iniciales, paso=1)
# modelo += (MCMC(modelo[0]),)
# # modelo.use_step_method(pymc.AdaptiveMetropolis)
#
# # Ejecutar la calibración
# print("Calibrando el modelo...")
# modelo[-1].sample(iter=500, burn=100, thin=5)
# salvar(modelo[-1])
#
# print("Analizando la incertidumbre...")
# print(anal_incert(modelo, datos_coco, 0.95, 10, poblaciones_iniciales))