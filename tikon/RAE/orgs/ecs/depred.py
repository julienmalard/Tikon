import numpy as np

from tikon.RAE.red_ae.utils import probs_conj
from tikon.ecs.paráms import Parám
from tikon.ecs.árb_mód import CategEc, SubcategEc, Ecuación, EcuaciónVacía

inf = np.inf


class PrATipoIDP(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class TipoIDP(Ecuación):
    nombre = 'Tipo I_Dependiente presa'
    _cls_ramas = [PrATipoIDP]


class PrATipoIIDP(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class PrBTipoIIDP(Parám):
    nombre = 'b'
    líms = (0, inf)
    inter = ['presa', 'huésped']


class TipoIIDP(Ecuación):
    nombre = 'Tipo I_Dependiente presa'
    _cls_ramas = [PrATipoIIDP]


class PrATipoIIIDP(Parám):
    nombre = 'a'
    líms = (0, 1)
    inter = ['presa', 'huésped']


class PrBTipoIIIDP(Parám):
    nombre = 'b'
    líms = (0, inf)
    inter = ['presa', 'huésped']


class TipoIIIDP(Ecuación):
    nombre = 'Tipo III_Dependiente presa'
    _cls_ramas = [PrATipoIIIDP, PrBTipoIIIDP]




class PrAKovai(Parám):
    nombre = 'a'
    líms = (0, inf)
    inter = ['presa', 'huésped']


class PrBKovai(Parám):
    nombre = 'b'
    líms = (0, inf)
    inter = ['presa', 'huésped']


class Kovai(Ecuación):
    nombre = 'Kovai'
    _cls_ramas = [PrAKovai, PrBKovai]


class EcuaciónDepred(SubcategEc):
    nombre = 'Ecuación'
    _cls_ramas = [EcuaciónVacía, TipoIDP, TipoIIDP, TipoIIIDP]
    auto = Kovai


class EcsDepred(CategEc):
    nombre = 'Depredación'
    _cls_ramas = [EcuaciónDepred]

    def __call__(símismo, paso):
        super()(paso)
        depred = símismo._res.obt_valor()

        # Reemplazar valores NaN con 0.
        depred[np.isnan(depred)] = 0

        # Arreglar errores de redondeo en la computación
        depred[depred < 0] = 0

        # Ajustar por superficies
        np.multiply(depred, extrn['superficies'].reshape(depred.shape[0], 1, 1, 1, 1), out=depred)

        # Convertir depredación potencial por depredador a depredación potencial total (multiplicar por la población
        # de cada depredador). También multiplicamos por el paso de la simulación. 'depred' ahora está en unidades
        # del número total de presas comidas por cada tipo de depredador por unidad de tiempo.
        np.multiply(depred, np.multiply(pobs, paso)[..., np.newaxis], out=depred)

        # Ajustar por la presencia de varios depredadores (eje = depredadores)
        eje_depredador = símismo._res.í_eje('etapa')
        probs_conj(depred, pesos=1, máx=pobs, eje=eje_depredador)

        depred[np.isnan(depred)] = 0

        # Redondear (para evitar de comer, por ejemplo, 2 * 10^-5 moscas). NO usamos la función "np.round()", porque
        # esta podría darnos valores superiores a los límites establecidos por probs_conj() arriba.
        np.floor(depred, out=depred)


dict(subs=[
    SubCategEc(

        ecs=[
            Ecuación(
                'Tipo I_Dependiente ratio',
                paráms=[
                    Parám('a', (0, 1), inter=['presa', 'huésped'])
                ]
            ),
            Ecuación(
                'Tipo II_Dependiente ratio',
                paráms=[
                    Parám('a', (0, 1), inter=['presa', 'huésped']),
                    Parám('b', (0, inf), inter=['presa', 'huésped'])
                ]
            ),
            Ecuación(
                'Tipo III_Dependiente ratio',
                paráms=[
                    Parám('a', (0, 1), inter=['presa', 'huésped']),
                    Parám('b', (0, inf), inter=['presa', 'huésped'])
                ]
            ),
            Ecuación(
                'Beddington-DeAngelis',
                paráms=[
                    Parám('a', (0, 1), inter=['presa', 'huésped']),
                    Parám('b', (0, inf), inter=['presa', 'huésped']),
                    Parám('c', (0, inf), inter=['presa', 'huésped'])
                ]
            ),
            Ecuación(
                'Tipo I_Hassell-Varley',
                paráms=[
                    Parám('a', (0, inf), inter=['presa', 'huésped']),
                    Parám('m', (0, inf), inter=['presa', 'huésped']),
                ]
            ),
            Ecuación(
                'Tipo II_Hassell-Varley',
                paráms=[
                    Parám('a', (0, inf), inter=['presa', 'huésped']),
                    Parám('b', (0, inf), inter=['presa', 'huésped']),
                    Parám('m', (0, inf), inter=['presa', 'huésped'])
                ]
            ),
            Ecuación(
                'Tipo III_Hassell-Varley',
                paráms=[
                    Parám('a', (0, inf), inter=['presa', 'huésped']),
                    Parám('b', (0, inf), inter=['presa', 'huésped']),
                    Parám('m', (0, inf), inter=['presa', 'huésped'])
                ]
            ),

        ],
    )
]
)
