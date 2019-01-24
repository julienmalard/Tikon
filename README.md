![Tiko'n](docs/source/Imágenes/Logo_Tikon.png)

[![Build Status](https://travis-ci.org/julienmalard/Tikon.svg?branch=master)](https://travis-ci.org/julienmalard/Tikon)
[![Coverage Status](https://coveralls.io/repos/github/julienmalard/Tikon/badge.svg?branch=master)](https://coveralls.io/github/julienmalard/Tikon?branch=master)
[![Documentation Status](https://readthedocs.org/projects/tikon/badge/?version=latest)](https://tikon.readthedocs.io/ur/latest/?badge=latest)

[![CodeFactor](https://www.codefactor.io/repository/github/julienmalard/tikon/badge)](https://www.codefactor.io/repository/github/julienmalard/tikon)
[![Maintainability](https://api.codeclimate.com/v1/badges/855ebb601a34ec094956/maintainability)](https://codeclimate.com/github/julienmalard/Tikon/maintainability)
# Tiko'n

Tiko'n es una librería Python para desarrollar modelos de redes agroecológicas (RAE).

## ¿Qué es una RAE?
Una RAE (Red AgroEcológica) es un modelo de las interacciones tróficas en un ecosystema agrícola.
Estos componentes incluyen insectos herbívoros, cultivos, e insectos benéficos, además de acciones de gestión humana
(biocontrol, irrigación, aplicaciones de fertilizantes, etc.).

## ¿Qué hace Tiko'n?
En breve, hace todo lo que no sabías que tenías que hacer, y que no quieres saber que tienes que hacer,
para desarrollar un modelo de redes agroecológicas.

En más detalles, Tiko'n:

1. Te deja crear un modelo de RAE con insectos, plantas y más.
2. Automágicamente maneja ecuaciones para las relaciones entre cada parte de la RAE.
3. Conecta(rá) con bases de datos de clima y modelos de cultivos externos
4. Simula, calibra, y valida modelos.
5. Y, por supuesto, te da bonitos gráficos.

## Un ejemplo
```python
from tikon.rae.red_ae import RedAE
from tikon.rae.orgs.insectos import MetamCompleta, Parasitoide
from tikon.estruc.simulador import Simulador

# Crear los insectos
oruga = MetamCompleta('oruga', njuvenil=3)
paras = Parasitoide('parasitoide')

# Relaciones tróficas
paras.parasita(oruga, etps_entra='juvenil_1', etp_emerg='pupa')

# Crear la red
mi_red = RedAE([oruga, paras])

# Simular
res = Simulador(mi_red).simular(días=30)
res.graficar()

```

## Instalación

Es muy fácil:

   `pip install tikon`

Si quieres la versión más recién (en desarrollo), puedes obtenerla de GitHub directamente con:

   `pip install git+git://github.com/julienmalard/tikon.git@master`

## Autores

* [Julien Jean Malard](https://www.researchgate.net/profile/Julien_Malard); julien.malard@mail.mcgill.ca
* [Marcela Rojas Días](https://www.researchgate.net/profile/Azhar_Baig); marcela.rojas@mail.mcgill.ca

