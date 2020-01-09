import seaborn as sns

from matplotlib.backends.backend_agg import FigureCanvasAgg as TelaFigura
from matplotlib.figure import Figure as Figura


def dibujar_dist(dist, nombre, ejes=None, argsll=None):
    args_base = dict(
        color='#99CC00', cut=0, shade=True
    )
    if argsll:
        args_base.update(argsll)

    if ejes is None:
        fig = Figura()
        TelaFigura(fig)
        ejes = fig.add_subplot(111)

    puntos = dist.obt_vals(10000)

    return sns.kdeplot(puntos, ax=ejes, **args_base).set_title(nombre)
